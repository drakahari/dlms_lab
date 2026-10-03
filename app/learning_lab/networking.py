"""Trusted networking adapter. No Qt, filesystem, or host I/O."""
from .domain.engine import Engine
from .scenario_identity import EngineVersion


NETWORKING_RUNTIME = EngineVersion('networking', 1, 'networking-1')


class NetworkingDomain:
    workspace = 'networking'

    def __init__(self, pack, diagnostics=None, constraints=None):
        self.pack = pack
        self.source = next(iter(pack['initial_state']))
        self.constraints = constraints if constraints is not None else [
            o['label'] for o in pack['objectives'] if o['predicate'] in ('address_equals', 'prefix_equals')]
        self.diagnostics = diagnostics if diagnostics is not None else self._legacy_diagnostics()

    def session(self, attempt=None, mode='Learn'):
        from .session import Session, new_attempt
        return Session(self.pack, attempt or new_attempt(self.pack,mode), self)

    @staticmethod
    def policy_text(value):
        lines = [f"Applied TCP policy · first match · default {value['default']}"]
        lines += [f"{i+1}. [{r['id']}] {r['action']} tcp {r['source']} → {r['destination']} port {r['port']}" for i,r in enumerate(value['rules'])]
        return '\n'.join(lines)

    def view_state(self, session, selected, rule_index):
        a=session.attempt
        source = session.engine.source
        firewall = 'firewall' in self.pack
        policy_draft = session.policy_draft() if firewall else {'default':'deny','rules':[]}
        rules = policy_draft['rules']
        selected_rule = rules[rule_index] if 0 <= rule_index < len(rules) else {'id':'','action':'deny','protocol':'tcp','source':'','destination':'','port':''}
        firewall_view = {'hasFirewall':firewall, 'firewallDevice':self.pack['firewall']['device'] if firewall else '', 'ruleIndex':rule_index, 'draftDefault':policy_draft['default'],
                         'ruleCount':len(rules), 'ruleInputs':selected_rule,
                         'ruleChoices':[f"{i+1}. {r['id']} · {r['action']} tcp {r['source']} → {r['destination']}:{r['port']}" for i,r in enumerate(rules)],
                         'appliedPolicy':self.policy_text(a['applied']['firewall']) if firewall else '',
                         'firewallDirty':'firewall' in a['draft']}
        links = ['%s: %s' % (segment, ' ↔ '.join(d['id'] for d in self.pack['topology']['devices'] if any(i['segment'] == segment for i in d['interfaces']))) for segment in self.pack['topology']['segments']]
        return {**firewall_view, 'editable':self.pack['editable_fields'][source], 'devices':[d['id'] for d in self.pack['topology']['devices']], 'deviceLinks':'\n'.join(links), 'inputs':{k:str(v) for k,v in {**a['applied'],**a['draft']}.items() if k!='firewall'}}

    def engine(self, applied):
        return Engine(self.pack, applied)

    def _legacy_diagnostics(self):
        checks = [{'id': o['id'], 'label': o['label'], 'operation': 'reach', 'target': o['params']['target']}
                  for o in self.pack['objectives'] if o['predicate'] == 'reachable']
        names = list(dict.fromkeys(o['params']['hostname'] for o in self.pack['objectives']
                                   if o['predicate'] == 'dns_and_portal'))
        if not names:
            names = list(dict.fromkeys(n for d in self.pack['topology']['devices'] for n in d['endpoints']))
        for index, name in enumerate(names):
            suffix = '' if len(names) == 1 else ' · ' + name
            checks += [{'id': 'dns-' + str(index), 'label': 'DNS' + suffix, 'operation': 'resolve', 'hostname': name},
                       {'id': 'portal-' + str(index), 'label': 'Portal (DNS/reachability only)' + suffix, 'operation': 'portal', 'hostname': name}]
        checks += [{'id': o['id'], 'label': o['label'], 'operation': 'connect',
                    'target': o['params']['target'], 'port': o['params']['port'],
                    'expected': 'denied' if o['predicate'] == 'tcp_blocked' else 'connected'}
                   for o in self.pack['objectives'] if o['predicate'] in ('tcp_allowed', 'tcp_blocked')]
        return checks

    def diagnose(self, applied):
        engine = self.engine(applied)
        rows = []
        for check in self.diagnostics:
            op = check['operation']
            if op == 'reach': result = engine.reach(check['target'])
            elif op == 'resolve': result = engine.resolve(check['hostname'])[0]
            elif op == 'portal': result = engine.portal(check['hostname'])
            else: result = engine.connect(check['target'], check['port'])
            ok = result.kind == 'policy-deny' if check.get('expected') == 'denied' else result.ok
            rows.append({'id': check['id'], 'label': check.get('label', check['id']), 'ok': ok,
                         'evidence': result.message, 'kind': result.kind, 'hops': list(result.hops)})
        return rows

    def presentation(self, applied, selected):
        engine = self.engine(applied)
        device = engine.by_id[selected]
        details = [f"{device['id']} · {device['role']}"]
        details += [f"{i['id']} · {i['address']}/{i['prefix']} · {i['segment']}" for i in device['interfaces']]
        details += [f"Gateway: {device['gateway'] or 'connected routes only'}", f"DNS: {device['dns'] or 'not configured'}"]
        if device['role'] == 'router': details.append('Forwarding ' + ('enabled' if device['forwarding'] else 'disabled'))
        details += [f'DNS: {name} → {ip}' for name, ip in device['records'].items()]
        details += ['Endpoint: ' + name for name in device['endpoints']]
        ports = next((s['ports'] for s in self.pack.get('tcp_services', []) if s['device'] == selected), [])
        if ports: details.append('Declared TCP listeners: ' + ', '.join(map(str, ports)))
        nodes = [{'id': d['id'], 'role': d['role'], 'addresses': '\n'.join(f"{i['address']}/{i['prefix']}" for i in d['interfaces']),
                  'segments': [i['segment'] for i in d['interfaces']]} for d in engine.devices]
        return {'sourceDevice': self.source, 'workspaceKind': self.workspace,
                'simulationNotice': 'Simulation only. Portal checks model DNS and reachability; TCP permission uses connect. No real commands or traffic.',
                'workspaceTools': ['topology', 'settings', 'console'] + (['firewall'] if 'firewall' in self.pack else []),
                'deviceDetails': '\n'.join(details), 'topologyNodes': nodes,
                'topologySegments': list(self.pack['topology']['segments']),
                'constraints': list(self.constraints), 'taskSummary': self.pack['metadata']['brief'],
                'consolePrompt': f'{self.source} bounded console · type help for syntax · ↑/↓ history'}


# Only application-shipped implementations can appear here. Pack text is never
# an import path, Python class name, or QML component URL.
