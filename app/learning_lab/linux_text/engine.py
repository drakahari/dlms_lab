"""Opt-in text-stream contract. All learner I/O is dictionary-backed UTF-8."""
from copy import deepcopy
from dataclasses import dataclass
import re
from ..domain.validation import ValidationError, require, keys, text
from ..linux_service.vfs import VirtualFS, validate_nodes, canonical, parent, permitted
from ..linux_navigation.engine import NavigationEngine
from ..linux_navigation.file_management import target

CAPABILITIES = {'virtual-filesystem', 'file-navigation', 'activity-evidence', 'bounded-text-streams'}
TOOLS = {'head', 'tail', 'grep', 'wc', 'sort', 'uniq', 'cut', 'cat'}
EVIDENCE_TOOLS = (TOOLS-{'wc'})|{'wc -l','wc -w','wc -c','pipeline'}
HELP = '''Simulated Linux terminal — bounded UTF-8 text streams, C locale.
help; pwd; ls [-l] [PATH]; cd [PATH]  (enter ONE command; semicolons unsupported)
cat FILE
head [-n N] [FILE]; tail [-n N] [FILE]  N: 0–4096, default 10
 grep -F [-n] TEXT [FILE]             one nonempty fixed string, no regex
wc -l|-w|-c [FILE]                    one option: LF, ASCII words, UTF-8 bytes
sort [FILE]                          bytewise ascending, keeps duplicates
uniq [-c] [FILE]                      adjacent duplicates only
cut -d DELIM -f N [FILE]              one ASCII delimiter, field 1–64
First stream stage needs FILE; later stages may consume stdin instead.
Up to four stages: command | command; optional final > PATH or >> PATH.
Quotes group one literal word (e.g. cut -d "|" -f 2). No escaping or expansion.
Only declared output files may be written. > truncates BEFORE reading input;
errors do NOT roll back writes. >> appends. Pipeline source/output aliases rejected.
No scripts, shell, processes, host files/network, regex, globs, variables, stdin
redirects, stderr redirects, substitutions, chaining or unsupported options.
8 KiB/file, 64 KiB total, 32 KiB/stage, 16 KiB display; bounded UTF-8 text only.
Actual writes clear verification. Inspect final output again before submission.
Pipeline status is the last stage's status; upstream errors remain visible.'''


@dataclass
class Result:
    stdout: bytes = b''
    errors: tuple = ()
    status: int = 0


def prefix(data, size):
    return data[:max(0, size)].decode('utf-8', errors='ignore').encode('utf-8')


def lex(command):
    require(isinstance(command, str) and 0 < len(command) <= 512, 'Command must be 1–512 characters.')
    try:command.encode('utf-8')
    except UnicodeError as exc:raise ValidationError('Command must be valid UTF-8 text.') from exc
    require(not any(c in command for c in '\n\r;<$`\\&') and not any(ord(c)<32 and c!='\t' for c in command),
            'Unsupported shell construct. No expansion, escaping, substitution or host command is run.')
    tokens=[];i=0
    while i<len(command):
        c=command[i]
        if c in ' \t':i+=1;continue
        if c in '|>':
            op='>>' if command[i:i+2]=='>>' else c;tokens.append(('op',op));i+=len(op);continue
        if c in "'\"":
            end=command.find(c,i+1);require(end!=-1,'Unclosed literal quote.')
            require(end+1==len(command) or command[end+1] in ' \t|>', 'Quote concatenation is unsupported.')
            tokens.append(('word',command[i+1:end]));i=end+1;continue
        end=i
        while end<len(command) and command[end] not in ' \t|>':
            require(command[end] not in "'\"", 'Quotes must surround a complete literal word.');require(command[end] not in '*?(){}[]#~', 'Unsupported unquoted expansion/comment construct.');end+=1
        tokens.append(('word',command[i:end]));i=end
    require(bool(tokens),'Empty command.');return tokens


def spec(words, first):
    require(bool(words),'Empty pipeline stage.');op=words[0];args=words[1:];options={};file=None
    require(op in TOOLS or op in ('help','pwd','ls','cd'), 'Unsupported command. Type help; no host command is run.')
    if op in ('help','pwd'):require(not args,'No arguments supported.')
    elif op in ('ls','cd'):
        if op=='ls' and args[:1]==['-l']:options['long']=True;args=args[1:]
        require(len(args)<=1 and not any(a.startswith('-') for a in args),'Supported: ls [-l] [PATH]; cd [PATH]')
        file=args[0] if args else None
    elif op in ('head','tail'):
        options['n']=10
        if args[:1]==['-n']:
            require(len(args)>=2 and re.fullmatch('[0-9]{1,4}',args[1]) and int(args[1])<=4096,'-n needs decimal 0–4096.')
            options['n']=int(args[1]);args=args[2:]
    elif op=='grep':
        require(args[:1]==['-F'],'Supported: grep -F [-n] TEXT [FILE]');args=args[1:]
        if args[:1]==['-n']:options['number']=True;args=args[1:]
        require(bool(args) and bool(args[0]) and not args[0].startswith('-'),'grep needs one nonempty literal TEXT.');options['pattern']=args[0].encode('utf-8');args=args[1:]
    elif op=='wc':
        require(bool(args) and args[0] in ('-l','-w','-c'),'Supported: wc -l|-w|-c [FILE]');options['count']=args[0];args=args[1:]
    elif op=='uniq':
        if args[:1]==['-c']:options['count']=True;args=args[1:]
    elif op=='cut':
        require(len(args)>=4 and args[0]=='-d' and args[2]=='-f' and len(args[1].encode('utf-8'))==1 and args[1]!='\n'
                and re.fullmatch('[0-9]{1,2}',args[3]) and 1<=int(args[3])<=64,'Supported: cut -d ASCII_DELIM -f FIELD [FILE], FIELD 1–64.')
        options={'delimiter':args[1].encode('utf-8'),'field':int(args[3])};args=args[4:]
    if op in TOOLS:
        require(len(args)<=1 and not any(a.startswith('-') for a in args),'One FILE or pipeline stdin; unsupported option/extra operand.')
        file=args[0] if args else None
        require(file is not None if first or op=='cat' else True,'First stream stage (and cat) requires FILE; no terminal stdin.')
    if file is not None:canonical(file)
    return op,options,file


def parse(command):
    tokens=lex(command);stages=[];words=[];redirect=None;i=0
    while i<len(tokens):
        kind,value=tokens[i]
        if kind=='word':words.append(value)
        elif value=='|':
            stages.append(spec(words,not stages));words=[]
        else:
            require(i+2==len(tokens) and tokens[i+1][0]=='word','One final > or >> PATH is supported.')
            redirect=(value,tokens[i+1][1]);canonical(redirect[1]);i+=2;break
        i+=1
    stages.append(spec(words,not stages));require(len(stages)<=4,'At most four pipeline stages.')
    require(len(stages)==1 and redirect is None or all(s[0] in TOOLS for s in stages),'Navigation/help cannot be piped or redirected.')
    return stages,redirect


def records(data):
    rows=data.split(b'\n')
    return rows[:-1] if data.endswith(b'\n') else rows if data else []


def filter_text(op, options, data, file=None):
    rows=records(data);status=0
    if op=='cat':out=data
    elif op in ('head','tail'):
        n=options['n'];chunks=data.splitlines(keepends=True)
        out=b''.join(chunks[:n] if op=='head' else chunks[-n:] if n else [])
    elif op=='grep':
        out=b''.join((str(i).encode()+b':' if options.get('number') else b'')+r+b'\n'
                     for i,r in enumerate(rows,1) if options['pattern'] in r)
        status=0 if out else 1
    elif op=='wc':
        kind=options['count'];n=data.count(b'\n') if kind=='-l' else len(data) if kind=='-c' else len(data.split())
        out=str(n).encode()+(b' '+file.encode('utf-8') if file is not None else b'')+b'\n'
    elif op=='sort':out=b''.join(r+b'\n' for r in sorted(rows))
    elif op=='uniq':
        groups=[]
        for r in rows:
            if groups and groups[-1][0]==r:groups[-1][1]+=1
            else:groups.append([r,1])
        out=b''.join((f'{n:7d} '.encode() if options.get('count') else b'')+r+b'\n' for r,n in groups)
    else:
        out=b'';delimiter=options['delimiter'];n=options['field']-1
        for r in rows:
            fields=r.split(delimiter);out+=(r if delimiter not in r else fields[n] if n<len(fields) else b'')+b'\n'
    if len(out)>32768:return Result(prefix(out,32768),('Simulated stage output limit reached (32 KiB); prefix retained.',),1)
    return Result(out,(),status)


def initial_state(pack):
    return {'filesystem':deepcopy(pack['domain']['filesystem']),'cwd':pack['domain']['cwd'],'observed':[]}


def validate_state(pack,state):
    keys(state,{'filesystem','cwd','observed'},'text-stream state');validate_nodes(state['filesystem'])
    initial=pack['domain']['filesystem'];outputs=pack['domain']['output_files'];nodes=state['filesystem']
    for p,n in initial.items():
        require(p in nodes,'Initial nodes cannot be removed.')
        if p not in outputs:require(nodes[p]==n,'Pinned source/outside node changed.')
        else:require({k:v for k,v in nodes[p].items() if k!='content'}=={k:v for k,v in n.items() if k!='content'},'Output metadata changed.')
    for p,n in nodes.items():
        if p not in initial:require(p in outputs and n=={'kind':'file','owner':'learner','group':'learner','mode':'0644','content':n['content']},'Unsupported new node.')
    VirtualFS(nodes).directory(state['cwd'],'/','learner')
    ids={o['id'] for o in pack['objectives'] if o['predicate']=='stream_observed'}
    require(isinstance(state['observed'],list) and all(isinstance(x,str) for x in state['observed'])
            and state['observed']==sorted(set(state['observed'])) and set(state['observed'])<=ids,'Invalid observation IDs.')
    return deepcopy(state)


class TextEngine(NavigationEngine):
    help_text=HELP
    def __init__(self,pack,state=None):self.pack=pack;self.state=deepcopy(state if state is not None else initial_state(pack))
    def validate(self,state):return validate_state(self.pack,state)

    def run(self,command):
        state=deepcopy(self.state);events=[];errors=[];data=b'';sources=set();redirect=None;dest=None;stages=None
        try:
            stages,redirect=parse(command);fs=VirtualFS(state['filesystem']);cwd=state['cwd'];nodes=fs.nodes
            if stages[0][0] not in TOOLS:
                op,opt,file=stages[0]
                if op=='help':out=HELP
                elif op=='pwd':out=cwd
                elif op=='cd':state['cwd']=fs.directory(file or self.pack['domain']['cwd'],cwd,'learner');out=state['cwd']
                else:out=fs.listing(file or '.',cwd,'learner',opt.get('long',False))
                return state,Result(out.encode())
            if redirect:
                dest=target(fs,redirect[1],cwd)
                require(dest in self.pack['domain']['output_files'],'Write destination is not a declared output file.')
                # Concurrent alias order is deliberately outside this contract.
                require(len(stages)==1 or all(file is None or canonical(file,cwd)!=dest for _,_,file in stages),'Pipeline source/output alias is unsupported; nothing opened.')
                require(not (redirect[0]=='>>' and stages[0][0]!='cat' and stages[0][2] is not None and canonical(stages[0][2],cwd)==dest), 'Filter self-append is unsupported; nothing opened.')
                if dest in nodes:
                    require(nodes[dest]['kind']=='file' and permitted(nodes[dest],'learner',2),'Permission denied (output write): '+dest)
                else:
                    fs.directory(parent(dest),'/','learner',3);require(len(nodes)<128,'Simulated node limit; output not created.')
                    nodes[dest]={'kind':'file','owner':'learner','group':'learner','mode':'0644','content':''};state['observed']=[]
                if redirect[0]=='>':
                    if nodes[dest]['content']:state['observed']=[]
                    nodes[dest]['content']=''
            for op,opt,file in stages:
                stage_sources=set(sources)
                try:
                    if file is not None:
                        data=fs.read(file,cwd,'learner').encode('utf-8');stage_sources={fs.resolve(file,cwd,'learner')}
                        require(not(op=='cat' and redirect and dest in stage_sources and data), 'Input file is output file (cat); nonempty self-copy refused.')
                    result=filter_text(op,opt,data,file)
                except ValidationError as exc:result=Result(b'',(op+': '+str(exc),),2 if op=='grep' else 1)
                data=result.stdout;sources=stage_sources;errors.extend(result.errors)
                evidence_tool=op+' '+opt['count'] if op=='wc' else op
                observed_data=(data.split(b' ',1)[0].rstrip(b'\n')+b'\n') if op=='wc' and result.status==0 else data
                events.append((evidence_tool,stage_sources,observed_data,result.status))
            status=result.status
            if redirect:
                previous=nodes[dest]['content'].encode('utf-8');combined=previous+data if redirect[0]=='>>' else data
                other=sum(len(n['content'].encode('utf-8')) for p,n in nodes.items() if p!=dest)
                allowed=min(8192,65536-other);written=prefix(combined,allowed)
                if written!=previous:state['observed']=[]
                nodes[dest]['content']=written.decode('utf-8')
                if len(written)!=len(combined):errors.append('Simulated file/total write limit reached; fitting prefix retained.');status=1
            elif not errors and all(e[3]==0 for e in events):
                # Evidence is for inspected output, not hidden redirected stdout.
                observations=[events[-1]]+([('pipeline',sources,data,status)] if len(stages)>1 else [])
                for o in self.pack['objectives']:
                    if o['predicate']!='stream_observed':continue
                    p=o['params']
                    if any(tool==p['tool'] and p['source'] in paths and output.decode('utf-8')==p['output'] for tool,paths,output,_ in observations):
                        state['observed']=sorted(set(state['observed'])|{o['id']})
            self.validate(state)
            return state,Result(b'' if redirect else data,tuple(errors),status)
        except ValidationError as exc:
            # Preserve any output open/truncate side effect already performed.
            self.validate(state)
            return state,Result(b'',('Simulation: '+str(exc),),2 if stages is None else 1)

    def command(self,command):
        state,result=self.run(command);shown=prefix(result.stdout,16384).decode('utf-8')
        if len(result.stdout)>16384:shown+='\n[display truncated; stream/report bytes unchanged]'
        output=(shown or '(empty stdout)')+'\n'+('\n'.join(result.errors)+'\n' if result.errors else '')+'[status '+str(result.status)+']'
        return state,output

    def checks(self):
        rows=[];nodes=self.state['filesystem'];initial=self.pack['domain']['filesystem']
        for o in self.pack['objectives']:
            p=o['params'];kind=o['predicate']
            if kind=='stream_observed':ok=o['id'] in self.state['observed'];evidence='Inspection: '+p['tool']+' output from '+p['source']+'; expected '+repr(p['output'])[:160]
            elif kind=='file_content':ok=p['path'] in nodes and nodes[p['path']]['content']==p['content'];evidence='Final report: '+p['path']+'; expected '+repr(p['content'])[:160]+'; actual '+repr(nodes.get(p['path'],{}).get('content','[missing]'))[:160]
            elif kind=='original_preserved':ok=nodes.get(p['path'])==initial[p['path']];evidence='Original preserved: '+p['path']
            else:ok=self.state['cwd']==p['path'];evidence='Final directory: '+p['path']
            rows.append({'id':o['id'],'label':o['label'],'ok':ok,'evidence':evidence+(' satisfied.' if ok else ' not yet satisfied.'),'kind':kind,'hops':[]})
        return rows


def guide(pack,state):
    passed={r['id']:r['ok'] for r in TextEngine(pack,state).checks()};steps=pack['domain']['lesson']['steps']
    index=next((i for i,s in enumerate(steps) if not passed[s['objective']]),len(steps)-1)
    return {**steps[index],'index':index,'total':len(steps),'verified':all(passed.values()),'completionMessage':'Text/report objectives met. Submit when ready.'}


def content_text(value,label):
    require(isinstance(value,str) and len(value.encode('utf-8'))<=8192 and not any(ord(c)<32 and c not in '\n\t' for c in value),'Invalid '+label+'. Expected bounded UTF-8 text.')


def validate_pack(value):
    require(re.fullmatch('[a-z][a-z0-9-]{0,63}',value['identity']['id']) is not None,'Invalid scenario ID.')
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',value['identity']['content_version']) is not None,'Invalid content version.')
    caps=value['engine']['required_capabilities'];require(isinstance(caps,list) and all(isinstance(c,str) for c in caps) and len(caps)==len(set(caps)) and set(caps)==CAPABILITIES,'Unsupported text capabilities.')
    text(value['mission']['brief'],'brief');require(type(value['metadata']['minutes']) is int and 1<=value['metadata']['minutes']<=240,'Invalid duration.')
    require(isinstance(value['hints'],list) and len(value['hints'])<=32,'At most 32 hints.')
    for h in value['hints']:text(h,'hint')
    d=value['domain'];keys(d,{'schema_version','filesystem','cwd','output_files','lesson'},'text domain');require(type(d['schema_version']) is int and d['schema_version']==3,'Unsupported text schema.')
    validate_nodes(d['filesystem']);require(len(d['filesystem'])<=64,'At most 64 initial nodes.')
    fs=VirtualFS(d['filesystem']);require(canonical(d['cwd'])==d['cwd'],'Canonical cwd required.');fs.directory(d['cwd'],'/','learner')
    outputs=d['output_files'];require(isinstance(outputs,list) and len(outputs)<=16 and all(isinstance(p,str) for p in outputs) and len(set(outputs))==len(outputs),'Expected up to 16 unique output files.')
    for p in outputs:
        require(p.startswith('/') and canonical(p)==p,'Canonical output path required.');fs.directory(parent(p),'/','learner')
        require(p not in fs.nodes or fs.nodes[p]['kind']=='file','Output must be a regular file.')
    objectives=value['objectives'];require(isinstance(objectives,list) and 1<=len(objectives)<=16,'Expected 1–16 objectives.');ids=set()
    for o in objectives:
        keys(o,{'id','label','points','predicate','params'},'text objective');text(o['id'],'objective ID',64);text(o['label'],'label',512)
        require(o['id'] not in ids,'Duplicate objective.');ids.add(o['id']);kind=o['predicate'];p=o['params']
        require(kind in ('stream_observed','file_content','original_preserved','cwd_equals'),'Unsupported text predicate.')
        keys(p,{'tool','source','output'} if kind=='stream_observed' else {'path','content'} if kind=='file_content' else {'path'},'text predicate params')
        path=p.get('source',p.get('path'));require(isinstance(path,str) and path.startswith('/') and canonical(path)==path,'Canonical predicate path required.')
        if kind=='stream_observed':
            require(p['tool'] in EVIDENCE_TOOLS,'Unknown inspection tool.');content_text(p['output'],'expected output')
            require(path in fs.nodes or path in outputs,'Unknown inspection source.')
        elif kind=='file_content':require(path in outputs,'Report must be a declared output.');content_text(p['content'],'report text')
        elif kind=='original_preserved':require(path in fs.nodes and path not in outputs,'Original must be pinned outside outputs.')
        else:fs.directory(path,'/','learner')
        require(type(o['points']) is int and 1<=o['points']<=100,'Invalid points.')
    require(sum(o['points'] for o in objectives)==100,'Rubric must total 100.')
    lesson=d['lesson'];keys(lesson,{'goal','steps'},'text lesson');text(lesson['goal'],'goal',240)
    require(isinstance(lesson['steps'],list) and len(lesson['steps'])==len(objectives),'One Learn step per objective.');seen=set()
    for s in lesson['steps']:
        keys(s,{'objective','command','explanation','expected'},'guided step');require(s['objective'] in ids and s['objective'] not in seen,'Unknown/duplicate Learn objective.');seen.add(s['objective'])
        text(s['command'],'command',512);parse(s['command']);text(s['explanation'],'explanation',512);text(s['expected'],'expected',512)
    pack={'domain':d,'objectives':objectives};state=initial_state(pack);validate_state(pack,state)
    for _ in range(64):
        engine=TextEngine(pack,state)
        if engine.grade()['complete']:return
        proposed,result=engine.run(guide(pack,state)['command']);require(proposed!=state,'Learn route cannot progress: '+str(result.errors));state=proposed
    raise ValidationError('Learn route cannot meet goals within 64 actions.')
