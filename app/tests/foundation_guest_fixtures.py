"""Trusted, fixed developer fixtures; never imported by learner runtime.

The generated lesson resources display these commands. Native acceptance uses
these static Python literals, not commands obtained from imported lesson JSON.
"""

def workspace(prefix):
    return ('w=$(mktemp -d "$HOME/'+prefix+'.XXXXXX") && cd "$w" && '
            'saved_umask=$(umask) && umask 077 && pwd && '
            'here() { case "$w" in "$HOME"/'+prefix+'.??????) ;; *) return 19;; esac; '
            'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
            'test "$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700 && '
            'test "$(pwd -P)" = "$w"; }; '
            'dir_ok() { test -d "$1" && test ! -L "$1" && test "$(realpath -e -- "$1")" = "$w/$1"; }; '
            'fresh() { for f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; '
            'here && test "$(df --output=avail -k . | tail -1)" -gt 65536')

def cleanup(files, directories=(), before=''):
    names=list(files)+list(directories)
    # find -path receives a pattern, even when the shell quotes it. Escape the
    # literal backslash in the awkward-name fixture rather than weakening the
    # exact-member guard or accidentally matching another pathname.
    allowed=' -o '.join('-path '+quote('./'+n.replace('\\','\\\\')) for n in names)
    checks='; '.join('test -'+('d' if n in directories else 'f')+' '+quote(n)+
                     ' && test ! -L '+quote(n)+' || return 19' for n in names)
    remove='rm -- '+' '.join(quote(n) for n in files)+' || return 19; '
    if directories:remove+='rmdir -- '+' '.join(quote(n) for n in sorted(directories,key=lambda n:n.count('/'),reverse=True))+' || return 19; '
    return ('clean_family() { here || return 19; '+before+
            'extra=$(find -P . -mindepth 1 ! \\( '+allowed+' \\) -print -quit) || return 19; '
            'test -z "$extra" || return 19; '+checks+'; '+remove+
            'cd "$HOME" && rmdir -- "$w" && umask "$saved_umask"; }; clean_family')

def quote(value):
    return "'"+value.replace("'","'\\''")+"'"

def lesson(family, slug, title, goal, challenge, steps, files, directories=(),
           assertions=(), negative=(), hints=(), mistakes=(), objectives=(),
           admin=False, materials=(), cleanup_before='', limitations=()):
    ident='real-linux-'+family+'-'+slug
    setup=workspace(family+'-'+slug)
    commands=[setup]+[step[0] for step in steps]
    clean=cleanup(files,directories,cleanup_before)
    content={'id':ident,'content_version':'1.0.0','title':title,'goal':goal,
             'challenge':challenge,
             'steps':[{'command':setup,'explanation':'Create and record a new private guest workspace. Stop on any failed guard; the free-space check is an observation, not a guaranteed reserve. Do not use the host terminal.',
                       'expected':'A unique learner-owned mode0700 directory; no originals overwritten.'}]+[
                        {'command':c,'explanation':e,'expected':x} for c,e,x in steps],
             'hints':list(hints),'review':['I retained actual statuses, bytes and relevant identities, including the incorrect case; successful command exit alone is not my evidence.',
                                        'I can explain the stated limitations and independently meet the Challenge outcomes. Completion records my self-review, not an automatic assessment.',
                                        'I preserved originals and inspected the exact cleanup inventory before deleting only this recorded practice workspace.'],
             'coverage':'LPIC-1 v5.0 '+', '.join(objectives)+'. Self-reviewed and unscored; no complete-objective, exam-readiness or LPI-endorsement claim.'}
    entry={'id':ident,'resource':ident+'.json','description':goal,'objectives':list(objectives),
           'troubleshooting':list(mistakes),'cleanup':['Stop any declared finite practice work first. Re-establish this recorded workspace and its guards after reopening; do not create a new workspace and pretend it is the old one.',clean,
                                                     'Refuse unexpected members/types or failed enumeration. Retain evidence on refusal; never use recursive deletion or adopt another path.'],
           'materials':['Create the isolated fixture and guard: '+setup]+list(materials),
           'observations':['Retain exact outputs, statuses, contents and identity/metadata comparisons before cleanup.'],
           'questions':['Which observation proves the required outcome, and what does it leave uncertain?', 'How would the stated incorrect approach fail or mislead?'],
           'limitations':['Display-only instructions; no learner command is executed by Learning Lab. Guest practice only; VM disks and records are excluded from profile backups. Resume boots disk, not RAM, jobs or shell variables.',
                          'These are cooperative practice guards, not race-resistant containment against guest root. Existing guest root can override guest-side limits.']+list(limitations)}
    return {'slug':slug,'id':ident,'admin':admin,'content':content,'entry':entry,
            'commands':commands,'challenge_commands':commands,
            'assertions':list(assertions),'negative':list(negative),'files':list(files),
            'directories':list(directories),'cleanup_command':clean}
