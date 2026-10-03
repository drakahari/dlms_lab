"""A dictionary-backed filesystem. Paths are virtual names, never host paths."""
import re
from ..domain.validation import ValidationError, require, keys

MAX_NODES = 128
MAX_FILE = 8192


def parts(path):
    require(isinstance(path,str) and 0<len(path)<=256 and re.fullmatch(r'[A-Za-z0-9_./-]+',path),
            'Virtual paths use letters, digits, /, ., _, and - (at most 256 characters).')
    return path.split('/')


def canonical(path, cwd='/'):
    tokens=parts(path); stack=[] if path.startswith('/') else [x for x in cwd.split('/') if x]
    for token in tokens:
        if token in ('','.'): continue
        if token=='..':
            require(bool(stack),'Path would escape the virtual root; traversal rejected.')
            stack.pop()
        else: stack.append(token)
    return '/'+ '/'.join(stack)


def parent(path): return path.rsplit('/',1)[0] or '/'


def permitted(node, user, bits):
    shift=6 if node['owner']==user else 3 if node['group']==user else 0
    return ((int(node['mode'],8)>>shift)&bits)==bits


def validate_nodes(nodes):
    require(isinstance(nodes,dict) and 1<=len(nodes)<=MAX_NODES,'Virtual filesystem must contain 1–128 nodes.')
    total=0
    for path,node in nodes.items():
        require(isinstance(path,str) and path.startswith('/') and canonical(path)==path,'Filesystem paths must be canonical absolute virtual paths.')
        keys(node,{'kind','owner','group','mode','content'},'virtual node')
        require(node['kind'] in ('file','directory'),'Only regular virtual files/directories are supported; no links or devices.')
        require(node['owner'] in ('root','learner','www-data') and node['group'] in ('root','learner','www-data'),'Unknown virtual identity.')
        require(isinstance(node['mode'],str) and re.fullmatch(r'0[0-7]{3}',node['mode']),'Only ordinary rwx permission bits are modeled.')
        content=node['content']
        require(isinstance(content,str) and len(content.encode('utf-8'))<=MAX_FILE and not any(ord(c)<32 and c not in '\n\t' for c in content),'Virtual file text is limited to 8 KiB; control characters are unsupported.')
        require(node['kind']=='file' or not content,'Directories cannot contain text.')
        total+=len(content.encode('utf-8'))
    require(total<=65536,'Virtual file contents exceed 64 KiB.')
    require('/' in nodes and nodes['/']['kind']=='directory','Virtual root directory is required.')
    for path in nodes:
        if path!='/': require(parent(path) in nodes and nodes[parent(path)]['kind']=='directory','Missing or non-directory virtual parent.')


class VirtualFS:
    def __init__(self,nodes): self.nodes=nodes

    def resolve(self,path,cwd,user):
        # Check search permission while walking, including before '..'. A lexical
        # normalization alone must not bypass an inaccessible ancestor.
        tokens=parts(path); current='/' if path.startswith('/') else cwd
        for token in tokens:
            node=self.nodes.get(current)
            require(node is not None and node['kind']=='directory','Not a virtual directory: '+current)
            require(permitted(node,user,1),'Permission denied (search): '+current)
            if token in ('','.'): continue
            if token=='..':
                require(current!='/','Path would escape the virtual root; traversal rejected.')
                current=parent(current)
            else:
                current=current.rstrip('/')+'/'+token
                require(current in self.nodes,'No such virtual file or directory: '+current)
        return current

    def directory(self,path,cwd,user,bits=1):
        result=self.resolve(path,cwd,user); node=self.nodes[result]
        require(node['kind']=='directory','Not a virtual directory: '+result)
        require(permitted(node,user,bits),'Permission denied: '+result)
        return result

    def read(self,path,cwd,user):
        result=self.resolve(path,cwd,user);node=self.nodes[result]
        require(node['kind']=='file','Is a virtual directory: '+result)
        require(permitted(node,user,4),'Permission denied (read): '+result)
        return node['content']

    def write(self,path,text,user):
        result=self.resolve(path,'/',user);node=self.nodes[result]
        require(node['kind']=='file' and permitted(node,user,2),'Permission denied (write): '+result)
        require(isinstance(text,str) and len(text.encode('utf-8'))<=MAX_FILE and not any(ord(c)<32 and c not in '\n\t' for c in text),'Virtual file text must be at most 8 KiB without control characters.')
        node['content']=text

    def mkdir(self,path,cwd,user,parents=False):
        tokens=parts(path);current='/' if path.startswith('/') else cwd
        meaningful=[t for t in tokens if t!='']
        if not meaningful:
            self.directory(current,'/',user)
            require(parents,'Directory already exists.')
            return current
        for i,token in enumerate(meaningful):
            self.directory(current,'/',user)
            if token in ('.','..'):
                if token=='..':
                    require(current!='/','Path would escape the virtual root; traversal rejected.')
                    current=parent(current)
                require(parents or i!=len(meaningful)-1,'Directory already exists: '+current)
                continue
            dest=current.rstrip('/')+'/'+token
            if dest in self.nodes:
                require(self.nodes[dest]['kind']=='directory','Not a virtual directory: '+dest)
                if i==len(meaningful)-1 and not parents:raise ValidationError('Directory already exists: '+dest)
            else:
                require(parents or i==len(meaningful)-1,'No such virtual parent directory: '+dest)
                require(permitted(self.nodes[current],user,3),'Permission denied (create): '+current)
                require(len(self.nodes)<MAX_NODES,'Virtual filesystem node limit reached.')
                self.nodes[dest]={'kind':'directory','owner':user,'group':user,'mode':'0755','content':''}
            current=dest
        return current

    def listing(self,path,cwd,user,long=False):
        result=self.resolve(path,cwd,user);node=self.nodes[result]
        if node['kind']=='directory':
            self.directory(result,'/',user,5)
            names=[p for p in sorted(self.nodes) if p!=result and parent(p)==result]
        else: names=[result]
        if not names:return '(empty virtual directory)'
        def row(name):
            n=self.nodes[name]
            mode=int(n['mode'],8);rwx=''.join(c if mode&(1<<bit) else '-' for bit,c in zip(range(8,-1,-1),'rwxrwxrwx'))
            return (('d' if n['kind']=='directory' else '-')+rwx+' '+n['owner']+' '+n['group']+' ' if long else '')+name
        return '\n'.join(row(p) for p in names)
