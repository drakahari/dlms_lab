"""Attempt transitions, independent of Qt and storage."""
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from .domain.engine import Engine
from .domain.validation import ValidationError, applied_state, initial_applied
from .networking import NetworkingDomain


def now():
    return datetime.now(timezone.utc).isoformat()


def new_attempt(pack, mode="Learn"):
    if mode not in ("Learn", "Challenge"):
        raise ValidationError("Unknown mode.")
    return {
        "id": str(uuid4()), "lab_id": pack["lab_id"], "content_version": pack["content_version"],
        "mode": mode, "started": now(), "updated": now(), "ended": None, "end_reason": None,
        "applied": initial_applied(pack), "draft": {}, "revision": 0,
        "hints": 0, "console": [], "commands": [], "assessments": {},
    }


class Session:
    def __init__(self, pack, attempt=None, domain=None):
        self.pack = pack
        self.domain = domain or NetworkingDomain(pack)
        self.attempt = deepcopy(attempt or new_attempt(pack))

    @property
    def engine(self):
        return self.domain.engine(self.attempt["applied"])

    def edit(self, field, value):
        if field not in self.pack["editable_fields"][self.engine.source]:
            raise ValidationError("That field is not editable.")
        if not isinstance(value, str) or len(value) > 128:
            raise ValidationError("Field input is too long.")
        if value == str(self.attempt["applied"][field]):
            self.attempt["draft"].pop(field, None)
        else:
            self.attempt["draft"][field] = value
        self.attempt["updated"] = now()

    def apply(self):
        candidate = applied_state(self.pack, {**self.attempt["applied"], **self.attempt["draft"]})
        initial = self.pack["initial_state"][self.engine.source]
        editable = self.pack["editable_fields"][self.engine.source]
        if any(candidate[k] != initial[k] for k in initial if k not in editable):
            raise ValidationError("A fixed scenario setting cannot be changed.")
        # A duplicate interface address is structurally invalid; other faults
        # remain allowed so the rubric can explain their consequences.
        engine = self.engine
        if any(i["address"] == candidate["address"] for d in engine.devices if d["id"] != engine.source for i in d["interfaces"]):
            raise ValidationError("That address is already assigned to another simulated device.")
        if candidate != self.attempt["applied"]:
            self.attempt["applied"] = candidate
            self.attempt["revision"] += 1
        self.attempt["draft"] = {}
        self.attempt["updated"] = now()

    def policy_draft(self):
        from .domain.firewall import editable_policy
        if 'firewall' not in self.pack:
            raise ValidationError('This lab does not expose firewall rules.')
        return deepcopy(self.attempt['draft'].get('firewall', editable_policy(self.attempt['applied']['firewall'])))

    def save_policy_draft(self, value):
        from .domain.firewall import draft_policy, editable_policy
        value = draft_policy(value)
        if value == editable_policy(self.attempt['applied']['firewall']):
            self.attempt['draft'].pop('firewall', None)
        else:
            self.attempt['draft']['firewall'] = value
        self.attempt['updated'] = now()

    def edit_rule(self, index, field, value):
        from .domain.firewall import RULE_FIELDS
        draft = self.policy_draft()
        if type(index) is not int or not 0 <= index < len(draft['rules']) or field not in RULE_FIELDS - {'protocol'}:
            raise ValidationError('Unknown rule or editable field.')
        draft['rules'][index][field] = value
        self.save_policy_draft(draft)

    def edit_default(self, value):
        draft = self.policy_draft(); draft['default'] = value; self.save_policy_draft(draft)

    def add_rule(self):
        from .domain.firewall import MAX_RULES
        draft = self.policy_draft()
        if len(draft['rules']) >= MAX_RULES:
            raise ValidationError('At most 16 rules are supported.')
        ids = {r['id'] for r in draft['rules']}
        name = next('rule-'+str(i) for i in range(1, MAX_RULES+2) if 'rule-'+str(i) not in ids)
        objective = next(o['params'] for o in self.pack['objectives'] if o['predicate'] == 'tcp_isolated')
        draft['rules'].append({'id': name, 'action': 'deny', 'protocol': 'tcp', 'source': self.attempt['applied']['address']+'/32', 'destination': objective['target']+'/32', 'port': str(objective['port'])})
        self.save_policy_draft(draft)
        return len(draft['rules']) - 1

    def remove_rule(self, index):
        draft = self.policy_draft()
        if type(index) is not int or not 0 <= index < len(draft['rules']):
            raise ValidationError('Unknown rule.')
        draft['rules'].pop(index); self.save_policy_draft(draft)

    def move_rule(self, index, offset):
        draft = self.policy_draft()
        if type(index) is not int or type(offset) is not int or offset not in (-1, 1) or not 0 <= index < len(draft['rules']) or not 0 <= index+offset < len(draft['rules']):
            raise ValidationError('Rule cannot move farther in that direction.')
        draft['rules'][index], draft['rules'][index+offset] = draft['rules'][index+offset], draft['rules'][index]
        self.save_policy_draft(draft)
        return index + offset

    def log(self, message):
        self.attempt["console"] = (self.attempt["console"] + message.splitlines())[-500:]
        self.attempt["updated"] = now()

    def execute(self, command):
        if command.strip() == "clear":
            self.attempt["console"] = []
            return
        if len(command) <= 512 and command.strip():
            self.attempt["commands"] = (self.attempt["commands"] + [command])[-100:]
        if self.attempt["draft"]:
            self.log("Warning: drafts exist. Commands use applied settings.")
        self.log("> " + command[:512])
        self.log(self.engine.command(command))

    def test(self):
        if self.attempt["draft"]:
            self.log("Warning: drafts exist. Tests use applied settings.")
        results = self.domain.diagnose(self.attempt['applied'])
        for row in results:
            self.log(f"{'PASS' if row['ok'] else 'FAIL'} · {row['label']}: {row['evidence']}")
        return results

    def hint(self):
        if self.attempt["mode"] != "Learn":
            raise ValidationError("Hints are hidden in Challenge mode.")
        self.attempt["hints"] = min(len(self.pack['hints']), self.attempt["hints"] + 1)
        self.attempt["updated"] = now()

    def submit(self):
        key = str(self.attempt["revision"])
        if key not in self.attempt["assessments"]:
            self.attempt["assessments"][key] = {
                **self.engine.grade(), "revision": self.attempt["revision"], "submitted": now(),
                "hints_at_submission": self.attempt["hints"], "applied": deepcopy(self.attempt["applied"]),
            }
        return deepcopy(self.attempt["assessments"][key])

    def archived(self, reason):
        archived = deepcopy(self.attempt)
        archived.update(ended=now(), end_reason=reason)
        return archived
