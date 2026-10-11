"""Fixed developer guest fixtures, never an application command executor."""
UNIT='lpic-local-shell-filesystem'
DATA=[{'slug': 'startup',
  'id': 'real-linux-local-startup',
  'admin': False,
  'content': {'id': 'real-linux-local-startup',
              'content_version': '1.0.0',
              'title': 'Trace shell startup without changing your account',
              'goal': 'Distinguish login, interactive non-login and noninteractive child startup '
                      'using an isolated HOME.',
              'challenge': 'In an isolated HOME, prove which startup marker each shell reads and '
                           'record login_shell plus interactive flags. Show first-readable profile '
                           'precedence; do not change real learner dotfiles.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-startup.XXXXXX") && cd "$w" && pwd '
                                    '&& here() { case "$w" in "$HOME"/local-startup.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = '
                                    '"$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" '
                                    '|| return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && fresh .bash_profile .profile .bashrc && { printf '
                                    "'echo PROFILE\\n' > .bash_profile; printf 'echo FALLBACK\\n' "
                                    "> .profile; printf 'echo RC\\n' > .bashrc; }",
                         'explanation': 'Use harmless markers. Bash reads the first available user '
                                        'login profile, not every profile. This profile '
                                        'deliberately does not source .bashrc.',
                         'expected': 'Three small files inside this workspace.'},
                        {'command': 'here && { env -i HOME="$w" PATH=/usr/bin:/bin bash --login -c '
                                    '\'echo "HOME=$HOME flags=$-"; shopt login_shell\' > '
                                    'login.txt; cat login.txt; }',
                         'explanation': 'A login shell reads /etc/profile and then its first '
                                        'readable user profile. Verify HOME remains the isolated '
                                        'path; stop if the system profile changes it.',
                         'expected': 'PROFILE, login_shell on, and no FALLBACK or RC.'},
                        {'command': 'here && { env -i HOME="$w" PATH=/usr/bin:/bin TERM=linux bash '
                                    '--noprofile --rcfile "$w/.bashrc" -ic \'echo "HOME=$HOME '
                                    'flags=$-"; shopt login_shell; :\' > interactive.txt; cat '
                                    'interactive.txt; }',
                         'explanation': 'Explicitly use this rc file for the interactive non-login '
                                        'child. -i appears in shell flags; login_shell is off.',
                         'expected': 'RC only; no profile marker.'},
                        {'command': 'here && { env -i HOME="$w" PATH=/usr/bin:/bin bash -c \'echo '
                                    '"HOME=$HOME flags=$-"; shopt login_shell; :\' > child.txt; '
                                    'cat child.txt; }',
                         'explanation': 'A noninteractive child does not automatically read '
                                        '.bashrc. BASH_ENV is intentionally absent from this clean '
                                        'environment.',
                         'expected': 'No user startup marker; no interactive i flag.'}],
              'hints': ['Which user login file wins?',
                        'Compare the i flag with login_shell; they are separate.',
                        'Do not edit ~/.bashrc or ~/.profile outside the workspace.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 105.1. Self-reviewed and unscored: the application '
                          'does not inspect guest results. No full-objective or exam-readiness '
                          'claim.'},
  'entry': {'id': 'real-linux-local-startup',
            'resource': 'real-linux-local-startup.json',
            'description': 'Distinguish login, interactive non-login and noninteractive child '
                           'startup using an isolated HOME.',
            'objectives': ['105.1 — narrow real-guest practice; completion is self-reviewed.'],
            'troubleshooting': ['HOME alone does not prove which shell mode ran; retain shopt and '
                                'flags.',
                                'A real .bash_profile may source .bashrc; our isolated one does '
                                'not.',
                                'shopt login_shell reports off with status 1; the observation '
                                'command ends in : deliberately.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        "-path './.bash_profile' -o -path './.profile' -o -path './.bashrc' -o "
                        "-path './login.txt' -o -path './interactive.txt' -o -path './child.txt' "
                        '\\) -print -quit) || return 19; test -z "$extra" || return 19; test -f '
                        '.bash_profile && test ! -L .bash_profile || return 19; test -f .profile '
                        '&& test ! -L .profile || return 19; test -f .bashrc && test ! -L .bashrc '
                        '|| return 19; test -f login.txt && test ! -L login.txt || return 19; test '
                        '-f interactive.txt && test ! -L interactive.txt || return 19; test -f '
                        'child.txt && test ! -L child.txt || return 19; rm -- .bash_profile '
                        '.profile .bashrc login.txt interactive.txt child.txt || return 19; cd '
                        '"$HOME" && rmdir -- "$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-startup.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
                          'in "$HOME"/local-startup.??????) ;; *) return 19;; esac; test "${w%/*}" '
                          '= "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e '
                          '"$w")" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700 && test '
                          '"$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L '
                          '"$f" || return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Trusted initial exercise fixture (not the repair): here && fresh '
                          ".bash_profile .profile .bashrc && { printf 'echo PROFILE\\n' > "
                          ".bash_profile; printf 'echo FALLBACK\\n' > .profile; printf 'echo "
                          "RC\\n' > .bashrc; }"],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 105.1. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-startup.XXXXXX") && cd "$w" && pwd && here() { case '
               '"$w" in "$HOME"/local-startup.??????) ;; *) return 19;; esac; test "${w%/*}" = '
               '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
               'test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() '
               '{ for f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               "here && fresh .bash_profile .profile .bashrc && { printf 'echo PROFILE\\n' > "
               ".bash_profile; printf 'echo FALLBACK\\n' > .profile; printf 'echo RC\\n' > "
               '.bashrc; }',
               'here && { env -i HOME="$w" PATH=/usr/bin:/bin bash --login -c \'echo "HOME=$HOME '
               'flags=$-"; shopt login_shell\' > login.txt; cat login.txt; }',
               'here && { env -i HOME="$w" PATH=/usr/bin:/bin TERM=linux bash --noprofile --rcfile '
               '"$w/.bashrc" -ic \'echo "HOME=$HOME flags=$-"; shopt login_shell; :\' > '
               'interactive.txt; cat interactive.txt; }',
               'here && { env -i HOME="$w" PATH=/usr/bin:/bin bash -c \'echo "HOME=$HOME '
               'flags=$-"; shopt login_shell; :\' > child.txt; cat child.txt; }'],
  'assertions': ['grep -qx PROFILE login.txt && ! grep -Eq "FALLBACK|RC" login.txt && grep -q '
                 '"login_shell.*on" login.txt',
                 'grep -qx RC interactive.txt && grep -q "flags=.*i" interactive.txt && grep -q '
                 '"login_shell.*off" interactive.txt',
                 '! grep -Eq "PROFILE|FALLBACK|RC" child.txt && grep -q "login_shell.*off" '
                 'child.txt',
                 'grep -q "^HOME=$w flags=[^i]*$" login.txt',
                 'grep -q "^HOME=$w flags=.*i" interactive.txt',
                 'grep -q "^HOME=$w flags=[^i]*$" child.txt'],
  'negative': [],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     "'./.bash_profile' -o -path './.profile' -o -path './.bashrc' -o -path "
                     "'./login.txt' -o -path './interactive.txt' -o -path './child.txt' \\) -print "
                     '-quit) || return 19; test -z "$extra" || return 19; test -f .bash_profile && '
                     'test ! -L .bash_profile || return 19; test -f .profile && test ! -L .profile '
                     '|| return 19; test -f .bashrc && test ! -L .bashrc || return 19; test -f '
                     'login.txt && test ! -L login.txt || return 19; test -f interactive.txt && '
                     'test ! -L interactive.txt || return 19; test -f child.txt && test ! -L '
                     'child.txt || return 19; rm -- .bash_profile .profile .bashrc login.txt '
                     'interactive.txt child.txt || return 19; cd "$HOME" && rmdir -- "$w"; }; '
                     'clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-startup.XXXXXX") && cd "$w" && pwd && here() '
                         '{ case "$w" in "$HOME"/local-startup.??????) ;; *) return 19;; esac; '
                         'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         "here && fresh .bash_profile .profile .bashrc && { printf 'echo "
                         "PROFILE\\n' > .bash_profile; printf 'echo FALLBACK\\n' > .profile; "
                         "printf 'echo RC\\n' > .bashrc; }",
                         'here && { env -i HOME="$w" PATH=/usr/bin:/bin bash --login -c \'echo '
                         '"HOME=$HOME flags=$-"; shopt login_shell\' > login.txt; cat login.txt; }',
                         'here && { env -i HOME="$w" PATH=/usr/bin:/bin TERM=linux bash '
                         '--noprofile --rcfile "$w/.bashrc" -ic \'echo "HOME=$HOME flags=$-"; '
                         "shopt login_shell; :' > interactive.txt; cat interactive.txt; }",
                         'here && { env -i HOME="$w" PATH=/usr/bin:/bin bash -c \'echo "HOME=$HOME '
                         'flags=$-"; shopt login_shell; :\' > child.txt; cat child.txt; }']},
 {'slug': 'history',
  'id': 'real-linux-local-history',
  'admin': False,
  'content': {'id': 'real-linux-local-history',
              'content_version': '1.0.0',
              'title': 'Edit isolated history and verify persistence',
              'goal': 'Separate in-memory command history from its on-disk record without touching '
                      'learner history.',
              'challenge': 'Create an isolated history containing two harmless commands, remove '
                           'only the obsolete entry, persist the result and reopen it in a '
                           'separate child. Demonstrate that clearing memory alone does not clear '
                           'disk.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-history.XXXXXX") && cd "$w" && pwd '
                                    '&& here() { case "$w" in "$HOME"/local-history.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = '
                                    '"$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" '
                                    '|| return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && fresh history.txt && { env -i HOME="$w" '
                                    'PATH=/usr/bin:/bin HISTFILE="$w/history.txt" HISTSIZE=20 '
                                    "HISTFILESIZE=20 bash --noprofile --norc -c 'set -o history; "
                                    'history -c; history -s "printf obsolete"; history -s "printf '
                                    'retained"; history -w; unset HISTFILE; history\' ; }',
                         'explanation': 'These are inserted history strings, not executed '
                                        'commands. History is enabled explicitly in a '
                                        'noninteractive child for a reproducible demonstration. '
                                        'After the explicit save, unset HISTFILE only inside this '
                                        'child so its exit cannot save the list again.',
                         'expected': 'Two entries persisted; parent history unchanged.'},
                        {'command': 'here && { env -i HOME="$w" PATH=/usr/bin:/bin '
                                    'HISTFILE="$w/history.txt" bash --noprofile --norc -c '
                                    "'history -c; history -r; history -d 1; history -w; unset "
                                    "HISTFILE; history' ; }",
                         'explanation': 'Read the isolated file, inspect indexes, delete the '
                                        'observed obsolete entry and write the revised list. Real '
                                        'interactive indexes need inspection; do not assume a '
                                        'global history number.',
                         'expected': 'Only printf retained remains in this fixture.'},
                        {'command': 'here && { env -i HOME="$w" PATH=/usr/bin:/bin '
                                    'HISTFILE="$w/history.txt" bash --noprofile --norc -c '
                                    "'history -c; history -r; history; history -c; test -s "
                                    '"$HISTFILE"\' && cat history.txt; }',
                         'explanation': 'Reopen in a new process. history -c affects memory; '
                                        'history -w is what rewrites the file. Default interactive '
                                        'exit behavior is separate from this explicitly written '
                                        'example.',
                         'expected': 'Disk still contains the retained command after memory '
                                     'clear.'}],
              'hints': ['Inspect before choosing an index.',
                        'Writing and appending history differ; this lesson uses -w deliberately.',
                        'Disk Resume does not restore a shell history list in RAM.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 103.1. Self-reviewed and unscored: the application '
                          'does not inspect guest results. No full-objective or exam-readiness '
                          'claim.'},
  'entry': {'id': 'real-linux-local-history',
            'resource': 'real-linux-local-history.json',
            'description': 'Separate in-memory command history from its on-disk record without '
                           'touching learner history.',
            'objectives': ['103.1 — narrow real-guest practice; completion is self-reviewed.'],
            'troubleshooting': ['History strings are not evidence that commands ran.',
                                'Clearing memory does not erase the file; concurrent interactive '
                                'shells can overwrite or append history.',
                                'Do not store secrets in history; this exercise uses no '
                                'credentials.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        '-path \'./history.txt\' \\) -print -quit) || return 19; test -z "$extra" '
                        '|| return 19; test -f history.txt && test ! -L history.txt || return 19; '
                        'rm -- history.txt || return 19; cd "$HOME" && rmdir -- "$w"; }; '
                        'clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-history.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
                          'in "$HOME"/local-history.??????) ;; *) return 19;; esac; test "${w%/*}" '
                          '= "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e '
                          '"$w")" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700 && test '
                          '"$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L '
                          '"$f" || return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.'],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 103.1. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-history.XXXXXX") && cd "$w" && pwd && here() { case '
               '"$w" in "$HOME"/local-history.??????) ;; *) return 19;; esac; test "${w%/*}" = '
               '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
               'test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() '
               '{ for f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               'here && fresh history.txt && { env -i HOME="$w" PATH=/usr/bin:/bin '
               'HISTFILE="$w/history.txt" HISTSIZE=20 HISTFILESIZE=20 bash --noprofile --norc -c '
               '\'set -o history; history -c; history -s "printf obsolete"; history -s "printf '
               'retained"; history -w; unset HISTFILE; history\' ; }',
               'here && { env -i HOME="$w" PATH=/usr/bin:/bin HISTFILE="$w/history.txt" bash '
               "--noprofile --norc -c 'history -c; history -r; history -d 1; history -w; unset "
               "HISTFILE; history' ; }",
               'here && { env -i HOME="$w" PATH=/usr/bin:/bin HISTFILE="$w/history.txt" bash '
               "--noprofile --norc -c 'history -c; history -r; history; history -c; test -s "
               '"$HISTFILE"\' && cat history.txt; }'],
  'assertions': ['test "$(cat history.txt)" = \'printf retained\''],
  'negative': ['env -i HOME="$w" PATH=/usr/bin:/bin HISTFILE="$w/history.txt" bash --noprofile '
               '--norc -c \'history -c; test -s "$HISTFILE"\''],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     '\'./history.txt\' \\) -print -quit) || return 19; test -z "$extra" || return '
                     '19; test -f history.txt && test ! -L history.txt || return 19; rm -- '
                     'history.txt || return 19; cd "$HOME" && rmdir -- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-history.XXXXXX") && cd "$w" && pwd && here() '
                         '{ case "$w" in "$HOME"/local-history.??????) ;; *) return 19;; esac; '
                         'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         'here && fresh history.txt && { env -i HOME="$w" PATH=/usr/bin:/bin '
                         'HISTFILE="$w/history.txt" HISTSIZE=20 HISTFILESIZE=20 bash --noprofile '
                         '--norc -c \'set -o history; history -c; history -s "printf obsolete"; '
                         'history -s "printf retained"; history -w; unset HISTFILE; history\' ; }',
                         'here && { env -i HOME="$w" PATH=/usr/bin:/bin HISTFILE="$w/history.txt" '
                         "bash --noprofile --norc -c 'history -c; history -r; history -d 1; "
                         "history -w; unset HISTFILE; history' ; }",
                         'here && { env -i HOME="$w" PATH=/usr/bin:/bin HISTFILE="$w/history.txt" '
                         "bash --noprofile --norc -c 'history -c; history -r; history; history -c; "
                         'test -s "$HISTFILE"\' && cat history.txt; }']},
 {'slug': 'editor',
  'id': 'real-linux-local-editor',
  'admin': False,
  'content': {'id': 'real-linux-local-editor',
              'content_version': '1.0.0',
              'title': 'Choose an editor through a real consumer',
              'goal': 'Verify temporary editor selection with sensible-editor, preserving a copy '
                      'before editing.',
              'challenge': 'Use a real editor-selecting command with temporary environment '
                           'settings. Demonstrate VISUAL precedence over EDITOR on this guest, '
                           'save one deliberate edit and preserve the original. Do not change '
                           'system alternatives.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-editor.XXXXXX") && cd "$w" && pwd '
                                    '&& here() { case "$w" in "$HOME"/local-editor.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = '
                                    '"$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" '
                                    '|| return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': "here && fresh note.txt original.txt && { printf 'original\\n' "
                                    '> note.txt; cp -p note.txt original.txt; command -v '
                                    'sensible-editor vi nano; vi --version | head -n 2; }',
                         'explanation': 'Inspect actual tools rather than assuming full Vim. The '
                                        'guest vi is Vim Tiny.',
                         'expected': 'A private original copy and installed tool paths.'},
                        {'command': 'here && { VISUAL=vi EDITOR=nano sensible-editor note.txt; }',
                         'explanation': 'This guest consumer chooses VISUAL before EDITOR. Inside '
                                        'vi: i, type edited-, Escape, :wq, Enter. These are editor '
                                        'keys, not shell commands. Environment assignments affect '
                                        'only this invocation.',
                         'expected': 'note.txt contains edited-original; nano was not selected.'},
                        {'command': 'here && { cat note.txt original.txt; cmp -s note.txt '
                                    'original.txt; printf "comparison status=%s\\n" "$?"; }',
                         'explanation': 'Verify bytes and the preserved copy. Not every '
                                        'application follows sensible-editor precedence.',
                         'expected': 'Changed note, unchanged original, comparison status 1.'}],
              'hints': ['Confirm which editor actually opened.',
                        'VISUAL takes precedence here; the variables are temporary.',
                        'Compare bytes, not just a zero editor exit status.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 103.8 /105.1. Self-reviewed and unscored: the '
                          'application does not inspect guest results. No full-objective or '
                          'exam-readiness claim.'},
  'entry': {'id': 'real-linux-local-editor',
            'resource': 'real-linux-local-editor.json',
            'description': 'Verify temporary editor selection with sensible-editor, preserving a '
                           'copy before editing.',
            'objectives': ['103.8 /105.1 — narrow real-guest practice; completion is '
                           'self-reviewed.'],
            'troubleshooting': ['EDITOR is not a universal system-wide default.',
                                'Escape leaves insert mode; :q! abandons unsaved edits, :wq saves.',
                                'An interrupted edit may leave a swap file: inspect it or retain '
                                'the workspace for recovery; never blindly delete unknown files.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        "-path './note.txt' -o -path './original.txt' \\) -print -quit) || return "
                        '19; test -z "$extra" || return 19; test -f note.txt && test ! -L note.txt '
                        '|| return 19; test -f original.txt && test ! -L original.txt || return '
                        '19; rm -- note.txt original.txt || return 19; cd "$HOME" && rmdir -- '
                        '"$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-editor.XXXXXX") && cd "$w" && pwd && here() { case "$w" in '
                          '"$HOME"/local-editor.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                          '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" '
                          '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                          '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" || '
                          'return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Trusted initial exercise fixture (not the repair): here && fresh '
                          "note.txt original.txt && { printf 'original\\n' > note.txt; cp -p "
                          'note.txt original.txt; command -v sensible-editor vi nano; vi --version '
                          '| head -n 2; }'],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 103.8 /105.1. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-editor.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
               'in "$HOME"/local-editor.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" '
               '&& test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
               '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for '
               'f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               "here && fresh note.txt original.txt && { printf 'original\\n' > note.txt; cp -p "
               'note.txt original.txt; command -v sensible-editor vi nano; vi --version | head -n '
               '2; }',
               'here && { VISUAL=vi EDITOR=nano sensible-editor note.txt; }',
               'here && { cat note.txt original.txt; cmp -s note.txt original.txt; printf '
               '"comparison status=%s\\n" "$?"; }'],
  'assertions': ['grep -qx edited-original note.txt && grep -qx original original.txt'],
  'negative': ['cp -p note.txt changed.txt && cp -p original.txt note.txt && cmp -s original.txt '
               'note.txt && ! cmp -s changed.txt note.txt && cp -p changed.txt note.txt && rm -- '
               'changed.txt'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     "'./note.txt' -o -path './original.txt' \\) -print -quit) || return 19; test "
                     '-z "$extra" || return 19; test -f note.txt && test ! -L note.txt || return '
                     '19; test -f original.txt && test ! -L original.txt || return 19; rm -- '
                     'note.txt original.txt || return 19; cd "$HOME" && rmdir -- "$w"; }; '
                     'clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-editor.XXXXXX") && cd "$w" && pwd && here() { '
                         'case "$w" in "$HOME"/local-editor.??????) ;; *) return 19;; esac; test '
                         '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         "here && fresh note.txt original.txt && { printf 'original\\n' > "
                         'note.txt; cp -p note.txt original.txt; command -v sensible-editor vi '
                         'nano; vi --version | head -n 2; }',
                         'here && { VISUAL=vi EDITOR=nano sensible-editor note.txt; }',
                         'here && { cat note.txt original.txt; cmp -s note.txt original.txt; '
                         'printf "comparison status=%s\\n" "$?"; }']},
 {'slug': 'hardlinks',
  'id': 'real-linux-local-hardlinks',
  'admin': False,
  'content': {'id': 'real-linux-local-hardlinks',
              'content_version': '1.0.0',
              'title': 'Prove hard-link identity and deletion semantics',
              'goal': 'Identify shared inode content and metadata, then remove an extra name '
                      'without losing the remaining file.',
              'challenge': 'Create a hard link to a small original, prove device/inode/link-count '
                           'identity, demonstrate shared edits and permissions, remove one name '
                           'and verify the remaining contents. Preserve an independent '
                           'before-copy.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-hardlinks.XXXXXX") && cd "$w" && '
                                    'pwd && here() { case "$w" in "$HOME"/local-hardlinks.??????) '
                                    ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d '
                                    '"$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                                    '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! '
                                    '-L "$f" || return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && fresh original.txt before.txt alias.txt && { printf '
                                    "'known\\n' > original.txt; chmod 0640 original.txt; cp -p "
                                    'original.txt before.txt; ln -- original.txt alias.txt; }',
                         'explanation': 'A hard link is a second directory entry for the same '
                                        'inode; before.txt is an independent copy. No directory or '
                                        'cross-filesystem hard linking is attempted.',
                         'expected': 'Two names share one inode; independent before-copy.'},
                        {'command': "here && { stat -c '%d:%i %h %a %n' original.txt alias.txt "
                                    'before.txt; cmp original.txt alias.txt; }',
                         'explanation': 'Equal bytes alone are insufficient: compare device plus '
                                        'inode and link count.',
                         'expected': 'original and alias have identical device/inode and link '
                                     'count 2; before differs.'},
                        {'command': "here && { printf 'added\\n' >> alias.txt; chmod 0600 "
                                    "alias.txt; cat original.txt; stat -c '%a' original.txt; cat "
                                    'before.txt; }',
                         'explanation': 'Writes and chmod act on the shared inode. This '
                                        'intentionally changes the teaching original; the '
                                        'independent before-copy retains its earlier state.',
                         'expected': 'Both names show known plus added and mode 600; before '
                                     'remains known.'},
                        {'command': 'here && { rm -- alias.txt; stat -c "%h" original.txt; cat '
                                    'original.txt; cmp -s before.txt original.txt; printf '
                                    '"comparison status=%s\\n" "$?"; }',
                         'explanation': 'Unlink one name, not an independently copied file. The '
                                        'data remains reachable through original.txt.',
                         'expected': 'Link count 1; modified data survives; before differs.'}],
              'hints': ['Check device:inode and nlink.',
                        'Which operation changes shared metadata?',
                        'Preserve an independent copy before deliberate shared edits.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 104.6. Self-reviewed and unscored: the application '
                          'does not inspect guest results. No full-objective or exam-readiness '
                          'claim.'},
  'entry': {'id': 'real-linux-local-hardlinks',
            'resource': 'real-linux-local-hardlinks.json',
            'description': 'Identify shared inode content and metadata, then remove an extra name '
                           'without losing the remaining file.',
            'objectives': ['104.6 — narrow real-guest practice; completion is self-reviewed.'],
            'troubleshooting': ['A hard link is not an independent backup.',
                                'Comparing inode numbers without the device is incomplete.',
                                'Removing a name is different from truncating the shared inode.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        "-path './original.txt' -o -path './before.txt' \\) -print -quit) || "
                        'return 19; test -z "$extra" || return 19; test -f original.txt && test ! '
                        '-L original.txt || return 19; test -f before.txt && test ! -L before.txt '
                        '|| return 19; rm -- original.txt before.txt || return 19; cd "$HOME" && '
                        'rmdir -- "$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-hardlinks.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
                          'in "$HOME"/local-hardlinks.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                          'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! '
                          '-e "$f" && test ! -L "$f" || return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Trusted initial exercise fixture (not the repair): here && fresh '
                          "original.txt before.txt alias.txt && { printf 'known\\n' > "
                          'original.txt; chmod 0640 original.txt; cp -p original.txt before.txt; '
                          '}'],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 104.6. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-hardlinks.XXXXXX") && cd "$w" && pwd && here() { case '
               '"$w" in "$HOME"/local-hardlinks.??????) ;; *) return 19;; esac; test "${w%/*}" = '
               '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
               'test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() '
               '{ for f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               "here && fresh original.txt before.txt alias.txt && { printf 'known\\n' > "
               'original.txt; chmod 0640 original.txt; cp -p original.txt before.txt; ln -- '
               'original.txt alias.txt; }',
               "here && { stat -c '%d:%i %h %a %n' original.txt alias.txt before.txt; cmp "
               'original.txt alias.txt; }',
               "here && { printf 'added\\n' >> alias.txt; chmod 0600 alias.txt; cat original.txt; "
               "stat -c '%a' original.txt; cat before.txt; }",
               'here && { rm -- alias.txt; stat -c "%h" original.txt; cat original.txt; cmp -s '
               'before.txt original.txt; printf "comparison status=%s\\n" "$?"; }'],
  'assertions': ['test "$(stat -c %h original.txt)" = 1 && test "$(stat -c %a original.txt)" = 600',
                 'test "$(cat before.txt)" = known && test "$(cat original.txt)" = '
                 "$'known\\nadded'"],
  'negative': ['cp -p original.txt wrong-copy.txt && test "$(stat -c %i original.txt)" != "$(stat '
               '-c %i wrong-copy.txt)" && printf "mistaken\\n" >> wrong-copy.txt && ! cmp -s '
               'original.txt wrong-copy.txt && rm -- wrong-copy.txt'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     "'./original.txt' -o -path './before.txt' \\) -print -quit) || return 19; "
                     'test -z "$extra" || return 19; test -f original.txt && test ! -L '
                     'original.txt || return 19; test -f before.txt && test ! -L before.txt || '
                     'return 19; rm -- original.txt before.txt || return 19; cd "$HOME" && rmdir '
                     '-- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-hardlinks.XXXXXX") && cd "$w" && pwd && '
                         'here() { case "$w" in "$HOME"/local-hardlinks.??????) ;; *) return 19;; '
                         'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         "here && fresh original.txt before.txt alias.txt && { printf 'known\\n' > "
                         'original.txt; chmod 0640 original.txt; cp -p original.txt before.txt; }',
                         'here && fresh alias.txt && ln -- original.txt alias.txt',
                         "here && { stat -c '%d:%i %h %a %n' original.txt alias.txt before.txt; "
                         'cmp original.txt alias.txt; }',
                         "here && { printf 'added\\n' >> alias.txt; chmod 0600 alias.txt; cat "
                         "original.txt; stat -c '%a' original.txt; cat before.txt; }",
                         'here && { rm -- alias.txt; stat -c "%h" original.txt; cat original.txt; '
                         'cmp -s before.txt original.txt; printf "comparison status=%s\\n" "$?"; '
                         '}']},
 {'slug': 'symlinks',
  'id': 'real-linux-local-symlinks',
  'admin': False,
  'content': {'id': 'real-linux-local-symlinks',
              'content_version': '1.0.0',
              'title': 'Repair a relative dangling link',
              'goal': 'Resolve a relative link from its containing directory and repair only the '
                      'link.',
              'challenge': 'Repair a dangling link in a nested directory while preserving the '
                           'original bytes and metadata. Verify access from two different current '
                           'directories and retain the relative target string.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-symlinks.XXXXXX") && cd "$w" && '
                                    'pwd && here() { case "$w" in "$HOME"/local-symlinks.??????) '
                                    ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d '
                                    '"$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                                    '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! '
                                    '-L "$f" || return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && fresh docs links before.sha256 before.meta && { mkdir '
                                    "docs links; printf 'handover\\n' > docs/note.txt; chmod 0640 "
                                    'docs/note.txt; sha256sum docs/note.txt > before.sha256; stat '
                                    "-c '%a %h' docs/note.txt > before.meta; ln -s "
                                    '../missing/note.txt links/current; }',
                         'explanation': 'The fault is a wrong relative target. A dangling link '
                                        'exists even when test -e is false.',
                         'expected': 'test -L succeeds; dereferenced access fails.'},
                        {'command': 'here && { readlink links/current; test -L links/current && '
                                    'test ! -e links/current; cat links/current; printf "read '
                                    'status=%s\\n" "$?"; }',
                         'explanation': 'Relative targets resolve from links/, not the current '
                                        'shell directory. Capture the failed read without claiming '
                                        'the original is missing.',
                         'expected': 'Known wrong target and a failed read.'},
                        {'command': 'here && { test -L links/current && rm -- links/current && ln '
                                    '-s ../docs/note.txt links/current; }',
                         'explanation': 'Replace only the verified link. Do not overwrite '
                                        'docs/note.txt or use ln -sf on an ambiguous path.',
                         'expected': 'Correct relative target; original preserved.'},
                        {'command': 'here && { readlink links/current; cat links/current; (cd '
                                    'links && cat current); sha256sum -c before.sha256; test '
                                    '"$(stat -c \'%a %h\' docs/note.txt)" = "$(cat before.meta)"; '
                                    '}',
                         'explanation': 'Verify resolution from both directories, independent '
                                        'bytes and metadata.',
                         'expected': 'Both reads handover; unchanged original bytes/mode/link '
                                     'count.'}],
              'hints': ['Where is the link stored?',
                        'Read the link before changing it.',
                        'Change the link, then verify the original independently.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 104.6. Self-reviewed and unscored: the application '
                          'does not inspect guest results. No full-objective or exam-readiness '
                          'claim.'},
  'entry': {'id': 'real-linux-local-symlinks',
            'resource': 'real-linux-local-symlinks.json',
            'description': 'Resolve a relative link from its containing directory and repair only '
                           'the link.',
            'objectives': ['104.6 — narrow real-guest practice; completion is self-reviewed.'],
            'troubleshooting': ['A symlink target is not relative to pwd.',
                                'A dangling link must be considered a collision by test -L as well '
                                'as -e.',
                                'A checksum detects changed bytes; it is not authenticity '
                                'evidence.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        "-path './links/current' -o -path './docs/note.txt' -o -path "
                        "'./before.sha256' -o -path './before.meta' -o -path './links' -o -path "
                        '\'./docs\' \\) -print -quit) || return 19; test -z "$extra" || return 19; '
                        'test -d links && test ! -L links || return 19; test -d docs && test ! -L '
                        'docs || return 19; test -L links/current || return 19; test -f '
                        'docs/note.txt && test ! -L docs/note.txt || return 19; test -f '
                        'before.sha256 && test ! -L before.sha256 || return 19; test -f '
                        'before.meta && test ! -L before.meta || return 19; rm -- links/current '
                        'docs/note.txt before.sha256 before.meta || return 19; rmdir -- links docs '
                        '|| return 19; cd "$HOME" && rmdir -- "$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-symlinks.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
                          'in "$HOME"/local-symlinks.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                          'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! '
                          '-e "$f" && test ! -L "$f" || return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Trusted initial exercise fixture (not the repair): here && fresh docs '
                          'links before.sha256 before.meta && { mkdir docs links; printf '
                          "'handover\\n' > docs/note.txt; chmod 0640 docs/note.txt; sha256sum "
                          "docs/note.txt > before.sha256; stat -c '%a %h' docs/note.txt > "
                          'before.meta; ln -s ../missing/note.txt links/current; }'],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 104.6. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-symlinks.XXXXXX") && cd "$w" && pwd && here() { case '
               '"$w" in "$HOME"/local-symlinks.??????) ;; *) return 19;; esac; test "${w%/*}" = '
               '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
               'test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() '
               '{ for f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               'here && fresh docs links before.sha256 before.meta && { mkdir docs links; printf '
               "'handover\\n' > docs/note.txt; chmod 0640 docs/note.txt; sha256sum docs/note.txt > "
               "before.sha256; stat -c '%a %h' docs/note.txt > before.meta; ln -s "
               '../missing/note.txt links/current; }',
               'here && { readlink links/current; test -L links/current && test ! -e '
               'links/current; cat links/current; printf "read status=%s\\n" "$?"; }',
               'here && { test -L links/current && rm -- links/current && ln -s ../docs/note.txt '
               'links/current; }',
               'here && { readlink links/current; cat links/current; (cd links && cat current); '
               'sha256sum -c before.sha256; test "$(stat -c \'%a %h\' docs/note.txt)" = "$(cat '
               'before.meta)"; }'],
  'assertions': ['test "$(readlink links/current)" = ../docs/note.txt && (cd links && grep -qx '
                 'handover current) && sha256sum -c before.sha256'],
  'negative': ['ln -s ../missing links/dangling && test -L links/dangling && test ! -e '
               'links/dangling && ! (test ! -e links/dangling && test ! -L links/dangling) && rm '
               '-- links/dangling'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     "'./links/current' -o -path './docs/note.txt' -o -path './before.sha256' -o "
                     "-path './before.meta' -o -path './links' -o -path './docs' \\) -print -quit) "
                     '|| return 19; test -z "$extra" || return 19; test -d links && test ! -L '
                     'links || return 19; test -d docs && test ! -L docs || return 19; test -L '
                     'links/current || return 19; test -f docs/note.txt && test ! -L docs/note.txt '
                     '|| return 19; test -f before.sha256 && test ! -L before.sha256 || return 19; '
                     'test -f before.meta && test ! -L before.meta || return 19; rm -- '
                     'links/current docs/note.txt before.sha256 before.meta || return 19; rmdir -- '
                     'links docs || return 19; cd "$HOME" && rmdir -- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-symlinks.XXXXXX") && cd "$w" && pwd && here() '
                         '{ case "$w" in "$HOME"/local-symlinks.??????) ;; *) return 19;; esac; '
                         'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         'here && fresh docs links before.sha256 before.meta && { mkdir docs '
                         "links; printf 'handover\\n' > docs/note.txt; chmod 0640 docs/note.txt; "
                         "sha256sum docs/note.txt > before.sha256; stat -c '%a %h' docs/note.txt > "
                         'before.meta; ln -s ../missing/note.txt links/current; }',
                         'here && { readlink links/current; test -L links/current && test ! -e '
                         'links/current; cat links/current; printf "read status=%s\\n" "$?"; }',
                         'here && { test -L links/current && rm -- links/current && ln -s '
                         '../docs/note.txt links/current; }',
                         'here && { readlink links/current; cat links/current; (cd links && cat '
                         'current); sha256sum -c before.sha256; test "$(stat -c \'%a %h\' '
                         'docs/note.txt)" = "$(cat before.meta)"; }']},
 {'slug': 'copies',
  'id': 'real-linux-local-copies',
  'admin': False,
  'content': {'id': 'real-linux-local-copies',
              'content_version': '1.0.0',
              'title': 'Choose independent copies instead of shared names',
              'goal': 'Compare copies, hard links and symbolic links by type, inode, contents and '
                      'metadata.',
              'challenge': 'Preserve an independent before-copy; the teaching original is '
                           'deliberately changed through its hard link. Create an independent '
                           'metadata-preserving copy, a hard link and a symlink; demonstrate which '
                           'objects change when editing the copy and when editing through the hard '
                           'link. Explain why none replaces versioned backup policy.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-copies.XXXXXX") && cd "$w" && pwd '
                                    '&& here() { case "$w" in "$HOME"/local-copies.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = '
                                    '"$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" '
                                    '|| return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && fresh original.txt before.txt copy.txt alias.txt '
                                    "pointer && { printf 'baseline\\n' > original.txt; chmod 0640 "
                                    'original.txt; cp -p original.txt before.txt; cp -p '
                                    'original.txt copy.txt; ln original.txt alias.txt; ln -s '
                                    'original.txt pointer; }',
                         'explanation': 'Small known regular file; cp -p preserves relevant mode '
                                        'and timestamps, not all possible Linux metadata.',
                         'expected': 'Independent copy versus shared inode versus link text.'},
                        {'command': "here && { stat -c '%F %d:%i %h %a %n' original.txt copy.txt "
                                    "alias.txt pointer; stat -Lc '%d:%i %n' pointer; readlink "
                                    'pointer; }',
                         'explanation': 'stat without -L inspects the symlink itself; -L follows '
                                        'it. Do not confuse the two types.',
                         'expected': 'Copy inode differs; alias shares; pointer is a symbolic '
                                     'link.'},
                        {'command': "here && { printf 'copy-only\\n' >> copy.txt; cmp original.txt "
                                    "before.txt; printf 'shared\\n' >> alias.txt; cat original.txt "
                                    'pointer copy.txt before.txt; }',
                         'explanation': 'First change only the copy; then deliberately demonstrate '
                                        'a shared write. Keep the independent before-copy.',
                         'expected': 'Original and pointer show baseline/shared; copy shows '
                                     'baseline/copy-only; before stays baseline.'},
                        {'command': 'here && { cp -P pointer pointer-copy; test -L pointer-copy; '
                                    'readlink pointer-copy; test "$(stat -c %a copy.txt)" = 640; }',
                         'explanation': 'GNU cp -P copies the symlink object; ordinary cp of a '
                                        'command-line symlink normally follows it. This fixture '
                                        'uses -P explicitly.',
                         'expected': 'Two symlinks with target original.txt; copy mode retained.'}],
              'hints': ['Inspect file type before interpreting inode output.',
                        'Which bytes changed through which name?',
                        'Keep a separate before-copy.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 103.3 /104.6. Self-reviewed and unscored: the '
                          'application does not inspect guest results. No full-objective or '
                          'exam-readiness claim.'},
  'entry': {'id': 'real-linux-local-copies',
            'resource': 'real-linux-local-copies.json',
            'description': 'Compare copies, hard links and symbolic links by type, inode, contents '
                           'and metadata.',
            'objectives': ['103.3 /104.6 — narrow real-guest practice; completion is '
                           'self-reviewed.'],
            'troubleshooting': ['Shared inode means shared edits; it is not a backup.',
                                'cp -P and a dereferenced regular-file copy produce different '
                                'objects.',
                                'cp -p is not an ACL/xattr/archive preservation claim.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        "-path './original.txt' -o -path './before.txt' -o -path './copy.txt' -o "
                        "-path './alias.txt' -o -path './pointer' -o -path './pointer-copy' \\) "
                        '-print -quit) || return 19; test -z "$extra" || return 19; test -f '
                        'original.txt && test ! -L original.txt || return 19; test -f before.txt '
                        '&& test ! -L before.txt || return 19; test -f copy.txt && test ! -L '
                        'copy.txt || return 19; test -f alias.txt && test ! -L alias.txt || return '
                        '19; test -L pointer || return 19; test -L pointer-copy || return 19; rm '
                        '-- original.txt before.txt copy.txt alias.txt pointer pointer-copy || '
                        'return 19; cd "$HOME" && rmdir -- "$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-copies.XXXXXX") && cd "$w" && pwd && here() { case "$w" in '
                          '"$HOME"/local-copies.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                          '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" '
                          '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                          '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" || '
                          'return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Trusted initial exercise fixture (not the repair): here && fresh '
                          'original.txt before.txt copy.txt alias.txt pointer && { printf '
                          "'baseline\\n' > original.txt; chmod 0640 original.txt; cp -p "
                          'original.txt before.txt; }'],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 103.3 /104.6. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-copies.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
               'in "$HOME"/local-copies.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" '
               '&& test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
               '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for '
               'f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               'here && fresh original.txt before.txt copy.txt alias.txt pointer && { printf '
               "'baseline\\n' > original.txt; chmod 0640 original.txt; cp -p original.txt "
               'before.txt; cp -p original.txt copy.txt; ln original.txt alias.txt; ln -s '
               'original.txt pointer; }',
               "here && { stat -c '%F %d:%i %h %a %n' original.txt copy.txt alias.txt pointer; "
               "stat -Lc '%d:%i %n' pointer; readlink pointer; }",
               "here && { printf 'copy-only\\n' >> copy.txt; cmp original.txt before.txt; printf "
               "'shared\\n' >> alias.txt; cat original.txt pointer copy.txt before.txt; }",
               'here && { cp -P pointer pointer-copy; test -L pointer-copy; readlink pointer-copy; '
               'test "$(stat -c %a copy.txt)" = 640; }'],
  'assertions': ['test "$(stat -c %i original.txt)" = "$(stat -c %i alias.txt)" && test "$(stat -c '
                 '%i original.txt)" != "$(stat -c %i copy.txt)" && test -L pointer-copy',
                 'test "$(cat before.txt)" = baseline && test "$(cat copy.txt)" = '
                 "$'baseline\\ncopy-only'"],
  'negative': ['cp pointer dereferenced.txt && test -f dereferenced.txt && test ! -L '
               'dereferenced.txt && rm -- dereferenced.txt'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     "'./original.txt' -o -path './before.txt' -o -path './copy.txt' -o -path "
                     "'./alias.txt' -o -path './pointer' -o -path './pointer-copy' \\) -print "
                     '-quit) || return 19; test -z "$extra" || return 19; test -f original.txt && '
                     'test ! -L original.txt || return 19; test -f before.txt && test ! -L '
                     'before.txt || return 19; test -f copy.txt && test ! -L copy.txt || return '
                     '19; test -f alias.txt && test ! -L alias.txt || return 19; test -L pointer '
                     '|| return 19; test -L pointer-copy || return 19; rm -- original.txt '
                     'before.txt copy.txt alias.txt pointer pointer-copy || return 19; cd "$HOME" '
                     '&& rmdir -- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-copies.XXXXXX") && cd "$w" && pwd && here() { '
                         'case "$w" in "$HOME"/local-copies.??????) ;; *) return 19;; esac; test '
                         '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         'here && fresh original.txt before.txt copy.txt alias.txt pointer && { '
                         "printf 'baseline\\n' > original.txt; chmod 0640 original.txt; cp -p "
                         'original.txt before.txt; }',
                         'here && fresh copy.txt alias.txt pointer && cp -p original.txt copy.txt '
                         '&& ln -- original.txt alias.txt && ln -s original.txt pointer',
                         "here && { stat -c '%F %d:%i %h %a %n' original.txt copy.txt alias.txt "
                         "pointer; stat -Lc '%d:%i %n' pointer; readlink pointer; }",
                         "here && { printf 'copy-only\\n' >> copy.txt; cmp original.txt "
                         "before.txt; printf 'shared\\n' >> alias.txt; cat original.txt pointer "
                         'copy.txt before.txt; }',
                         'here && { cp -P pointer pointer-copy; test -L pointer-copy; readlink '
                         'pointer-copy; test "$(stat -c %a copy.txt)" = 640; }']},
 {'slug': 'search',
  'id': 'real-linux-local-search',
  'admin': False,
  'content': {'id': 'real-linux-local-search',
              'content_version': '1.0.0',
              'title': 'Find files and justify filesystem placement',
              'goal': 'Use bounded name/type/size/time searches and explain configuration, logs '
                      'and local data placement.',
              'challenge': 'In the model tree locate the current log, old log and configuration by '
                           'verified predicates. Record sizes/time criteria and explain where '
                           'configuration, changing logs and local static data belong on real '
                           'Linux. Do not modify actual system paths.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-search.XXXXXX") && cd "$w" && pwd '
                                    '&& here() { case "$w" in "$HOME"/local-search.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = '
                                    '"$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" '
                                    '|| return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && fresh etc var usr placement.txt && { mkdir etc var '
                                    'usr; mkdir var/log usr/local; mkdir usr/local/share; printf '
                                    "'setting=on\\n' > etc/app.conf; printf 'current "
                                    "observation\\n' > var/log/current.log; printf 'old\\n' > "
                                    "var/log/old.log; touch -d '3 days ago' var/log/old.log; "
                                    "printf 'reference\\n' > usr/local/share/readme.txt; }",
                         'explanation': 'This is a small model tree inside your home, not the real '
                                        'root filesystem. touch changes only a fixture timestamp, '
                                        'never the clock.',
                         'expected': 'Separate configuration, variable logs and local static '
                                     'data.'},
                        {'command': "here && { find -P . -maxdepth 4 -type f -name '*.log' -print; "
                                    'find -P . -maxdepth 4 -type f -size +10c -print; }',
                         'explanation': 'Quote the glob so find receives it. c means bytes; other '
                                        'size units have rounding. -P does not follow symbolic '
                                        'links.',
                         'expected': 'Two logs; configuration/current log satisfy the byte-size '
                                     'condition.'},
                        {'command': 'here && { find -P var/log -maxdepth 1 -type f -mtime +1 '
                                    '-print; find -P var/log -maxdepth 1 -type f -mmin -5 -print; '
                                    '}',
                         'explanation': 'mtime counts whole 24-hour periods; +1 selects more than '
                                        'one completed period. mmin uses minutes. Read/retain '
                                        'timestamps and avoid assuming exact age from a filename.',
                         'expected': 'old.log versus recently created current.log; may need to '
                                     'recreate only this fixture after a long pause.'},
                        {'command': "here && { stat -c '%n %s %y' etc/app.conf var/log/current.log "
                                    "var/log/old.log usr/local/share/readme.txt; printf '%s\\n' "
                                    "'CONFIG etc/app.conf' 'VARIABLE var/log/current.log' 'STATIC "
                                    "usr/local/share/readme.txt' > placement.txt; cat "
                                    'placement.txt; }',
                         'explanation': 'Explain /etc, /var/log and /usr/local/share roles. This '
                                        'narrow model does not cover the entire FHS or '
                                        'locate/updatedb databases.',
                         'expected': 'Evidence and placement rationale; no real system change.'}],
              'hints': ['Combine type with quoted name.',
                        'Record units, not just a number.',
                        'Use explicit root and maxdepth; do not search the whole disk.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 103.3 /104.7. Self-reviewed and unscored: the '
                          'application does not inspect guest results. No full-objective or '
                          'exam-readiness claim.'},
  'entry': {'id': 'real-linux-local-search',
            'resource': 'real-linux-local-search.json',
            'description': 'Use bounded name/type/size/time searches and explain configuration, '
                           'logs and local data placement.',
            'objectives': ['103.3 /104.7 — narrow real-guest practice; completion is '
                           'self-reviewed.'],
            'troubleshooting': ['Do not let the shell expand an unquoted pattern.',
                                '-mtime +1 does not mean older than one minute or an exact '
                                'timestamp.',
                                'A model path is not evidence that you administered the real FHS.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        "-path './etc/app.conf' -o -path './var/log/current.log' -o -path "
                        "'./var/log/old.log' -o -path './usr/local/share/readme.txt' -o -path "
                        "'./placement.txt' -o -path './etc' -o -path './var/log' -o -path './var' "
                        "-o -path './usr/local/share' -o -path './usr/local' -o -path './usr' \\) "
                        '-print -quit) || return 19; test -z "$extra" || return 19; test -d etc && '
                        'test ! -L etc || return 19; test -d var/log && test ! -L var/log || '
                        'return 19; test -d var && test ! -L var || return 19; test -d '
                        'usr/local/share && test ! -L usr/local/share || return 19; test -d '
                        'usr/local && test ! -L usr/local || return 19; test -d usr && test ! -L '
                        'usr || return 19; test -f etc/app.conf && test ! -L etc/app.conf || '
                        'return 19; test -f var/log/current.log && test ! -L var/log/current.log '
                        '|| return 19; test -f var/log/old.log && test ! -L var/log/old.log || '
                        'return 19; test -f usr/local/share/readme.txt && test ! -L '
                        'usr/local/share/readme.txt || return 19; test -f placement.txt && test ! '
                        '-L placement.txt || return 19; rm -- etc/app.conf var/log/current.log '
                        'var/log/old.log usr/local/share/readme.txt placement.txt || return 19; '
                        'rmdir -- etc var/log var usr/local/share usr/local usr || return 19; cd '
                        '"$HOME" && rmdir -- "$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-search.XXXXXX") && cd "$w" && pwd && here() { case "$w" in '
                          '"$HOME"/local-search.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                          '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" '
                          '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                          '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" || '
                          'return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Trusted initial exercise fixture (not the repair): here && fresh etc '
                          'var usr placement.txt && { mkdir etc var usr; mkdir var/log usr/local; '
                          "mkdir usr/local/share; printf 'setting=on\\n' > etc/app.conf; printf "
                          "'current observation\\n' > var/log/current.log; printf 'old\\n' > "
                          "var/log/old.log; touch -d '3 days ago' var/log/old.log; printf "
                          "'reference\\n' > usr/local/share/readme.txt; }"],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 103.3 /104.7. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-search.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
               'in "$HOME"/local-search.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" '
               '&& test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
               '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for '
               'f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               'here && fresh etc var usr placement.txt && { mkdir etc var usr; mkdir var/log '
               "usr/local; mkdir usr/local/share; printf 'setting=on\\n' > etc/app.conf; printf "
               "'current observation\\n' > var/log/current.log; printf 'old\\n' > var/log/old.log; "
               "touch -d '3 days ago' var/log/old.log; printf 'reference\\n' > "
               'usr/local/share/readme.txt; }',
               "here && { find -P . -maxdepth 4 -type f -name '*.log' -print; find -P . -maxdepth "
               '4 -type f -size +10c -print; }',
               'here && { find -P var/log -maxdepth 1 -type f -mtime +1 -print; find -P var/log '
               '-maxdepth 1 -type f -mmin -5 -print; }',
               "here && { stat -c '%n %s %y' etc/app.conf var/log/current.log var/log/old.log "
               "usr/local/share/readme.txt; printf '%s\\n' 'CONFIG etc/app.conf' 'VARIABLE "
               "var/log/current.log' 'STATIC usr/local/share/readme.txt' > placement.txt; cat "
               'placement.txt; }'],
  'assertions': ['test "$(find -P var/log -maxdepth 1 -type f -mtime +1 -print)" = var/log/old.log',
                 'test "$(find -P . -maxdepth 4 -type f -name \'*.log\' | wc -l)" = 2'],
  'negative': ['ln -s /etc external && test -z "$(find -P external -maxdepth 1 -type f -print)" && '
               'rm -- external'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     "'./etc/app.conf' -o -path './var/log/current.log' -o -path "
                     "'./var/log/old.log' -o -path './usr/local/share/readme.txt' -o -path "
                     "'./placement.txt' -o -path './etc' -o -path './var/log' -o -path './var' -o "
                     "-path './usr/local/share' -o -path './usr/local' -o -path './usr' \\) -print "
                     '-quit) || return 19; test -z "$extra" || return 19; test -d etc && test ! -L '
                     'etc || return 19; test -d var/log && test ! -L var/log || return 19; test -d '
                     'var && test ! -L var || return 19; test -d usr/local/share && test ! -L '
                     'usr/local/share || return 19; test -d usr/local && test ! -L usr/local || '
                     'return 19; test -d usr && test ! -L usr || return 19; test -f etc/app.conf '
                     '&& test ! -L etc/app.conf || return 19; test -f var/log/current.log && test '
                     '! -L var/log/current.log || return 19; test -f var/log/old.log && test ! -L '
                     'var/log/old.log || return 19; test -f usr/local/share/readme.txt && test ! '
                     '-L usr/local/share/readme.txt || return 19; test -f placement.txt && test ! '
                     '-L placement.txt || return 19; rm -- etc/app.conf var/log/current.log '
                     'var/log/old.log usr/local/share/readme.txt placement.txt || return 19; rmdir '
                     '-- etc var/log var usr/local/share usr/local usr || return 19; cd "$HOME" && '
                     'rmdir -- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-search.XXXXXX") && cd "$w" && pwd && here() { '
                         'case "$w" in "$HOME"/local-search.??????) ;; *) return 19;; esac; test '
                         '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         'here && fresh etc var usr placement.txt && { mkdir etc var usr; mkdir '
                         "var/log usr/local; mkdir usr/local/share; printf 'setting=on\\n' > "
                         "etc/app.conf; printf 'current observation\\n' > var/log/current.log; "
                         "printf 'old\\n' > var/log/old.log; touch -d '3 days ago' "
                         "var/log/old.log; printf 'reference\\n' > usr/local/share/readme.txt; }",
                         "here && { find -P . -maxdepth 4 -type f -name '*.log' -print; find -P . "
                         '-maxdepth 4 -type f -size +10c -print; }',
                         'here && { find -P var/log -maxdepth 1 -type f -mtime +1 -print; find -P '
                         'var/log -maxdepth 1 -type f -mmin -5 -print; }',
                         "here && { stat -c '%n %s %y' etc/app.conf var/log/current.log "
                         "var/log/old.log usr/local/share/readme.txt; printf '%s\\n' 'CONFIG "
                         "etc/app.conf' 'VARIABLE var/log/current.log' 'STATIC "
                         "usr/local/share/readme.txt' > placement.txt; cat placement.txt; }"]},
 {'slug': 'sticky',
  'id': 'real-linux-local-sticky',
  'admin': True,
  'content': {'id': 'real-linux-local-sticky',
              'content_version': '1.0.0',
              'title': 'Separate shared-directory writing from deletion',
              'goal': 'Prove sticky-bit deletion restrictions with two existing locked guest '
                      'identities.',
              'challenge': 'Use the existing ll-service and nobody identities only for files in a '
                           'unique shared practice directory. Demonstrate cross-user writing to a '
                           'deliberately writable file but refusal to unlink it; demonstrate owner '
                           'and directory-owner exceptions. Do not change accounts.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-sticky.XXXXXX") && cd "$w" && pwd '
                                    '&& here() { case "$w" in "$HOME"/local-sticky.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = '
                                    '"$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" '
                                    '|| return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && s=$(mktemp -d /tmp/ll-sticky.XXXXXX) && chmod 1777 '
                                    '"$s" && sg() { case "$s" in /tmp/ll-sticky.??????) ;; *) '
                                    'return 19;; esac; test "${s%/*}" = /tmp && test -d "$s" && '
                                    'test ! -L "$s" && test "$(realpath -e "$s")" = "$s" && test '
                                    '"$(stat -c %U:%a "$s")" = learner:1777 || return 19; for n in '
                                    'a b; do if test -e "$s/$n" || test -L "$s/$n"; then test ! -L '
                                    '"$s/$n" && test -f "$s/$n" && test "$(stat -c %h "$s/$n")" = '
                                    '1 && test "$(stat -c %s "$s/$n")" -le 1024 || return 19; fi; '
                                    'done; members=$(find -P "$s" -mindepth 1 -maxdepth 1 ! -name '
                                    'a ! -name b -print) || return 19; test -z "$members"; }; here '
                                    '&& sg && getent passwd ll-service nobody',
                         'explanation': 'Existing locked/non-login identities are invoked by '
                                        'approved guest sudo, not authenticated with credentials. '
                                        'Retain this exact generated path. Refuse setup failure.',
                         'expected': 'A unique directory owned by learner, mode 1777.'},
                        {'command': 'here && sg && fresh "$s/a" "$s/b" && { sudo runuser -u '
                                    'll-service -- sh -c \'printf "service\\n" > "$1/a" && chmod '
                                    '0666 "$1/a"\' sh "$s" && sudo runuser -u nobody -- sh -c '
                                    '\'printf "nobody\\n" > "$1/b"\' sh "$s"; }',
                         'explanation': 'Create files as the actual identities. The writable a '
                                        'file separates content permissions from directory '
                                        'deletion restrictions.',
                         'expected': 'a owned ll-service, b owned nobody.'},
                        {'command': "here && sg && { sudo runuser -u nobody -- sh -c 'printf "
                                    '"append\\n" | dd of="$1/a" oflag=append,nofollow '
                                    'conv=notrunc,nocreat status=none\' sh "$s" && printf '
                                    '\'service\\nappend\\n\' | cmp - "$s/a" && test "$(stat -c '
                                    '%U:%a "$s/a")" = ll-service:666 && { sudo runuser -u nobody '
                                    '-- rm -f -- "$s/a"; unlink_rc=$?; test "$unlink_rc" -ne 0 && '
                                    'test -f "$s/a" && printf \'service\\nappend\\n\' | cmp - '
                                    '"$s/a" && test "$(stat -c %U "$s/b")" = nobody && stat -c '
                                    '\'%U %a %n\' "$s" "$s/a" "$s/b"; }; }',
                         'explanation': 'Sticky restricts unlink/rename, not ordinary writes to an '
                                        'existing writable file. This guest also has '
                                        'protected_regular=2: shell >> uses O_CREAT and can be '
                                        'refused independently. The bounded GNU dd command opens '
                                        'only the known existing file: nocreat refuses a missing '
                                        'target, nofollow refuses a final symlink, notrunc '
                                        'preserves bytes, and append writes at the end. Do not '
                                        'change kernel policy. -f avoids an rm prompt; it cannot '
                                        'bypass sticky permission checks.',
                         'expected': 'Append succeeds, cross-owner unlink fails and a remains.'},
                        {'command': 'here && sg && { sudo runuser -u ll-service -- rm -f -- "$s/a" '
                                    '&& rm -f -- "$s/b" && rmdir -- "$s"; }',
                         'explanation': 'File owner may unlink a; learner, as directory owner, may '
                                        'unlink b. Root is also an exception, but using root alone '
                                        'would not test ordinary-user restrictions.',
                         'expected': 'Both exact files and shared directory removed.'}],
              'hints': ['Use actual identities and immediate status.',
                        'Compare file writing with directory entry removal.',
                        'Directory owner and file owner are exceptions.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 104.5. Self-reviewed and unscored: the application '
                          'does not inspect guest results. No full-objective or exam-readiness '
                          'claim.'},
  'entry': {'id': 'real-linux-local-sticky',
            'resource': 'real-linux-local-sticky.json',
            'description': 'Prove sticky-bit deletion restrictions with two existing locked guest '
                           'identities.',
            'objectives': ['104.5 — narrow real-guest practice; completion is self-reviewed.'],
            'troubleshooting': ['Sticky does not make a shared file private or read-only.',
                                'Shell >> may be refused by protected_regular even when mode bits '
                                'permit writing. Use the documented existing-file operation; never '
                                'change kernel policy. GNU dd flags are not a portable-shell '
                                'promise.',
                                'Root success does not demonstrate ordinary-user access.',
                                'Refuse an ambiguous or substituted practice directory; never use '
                                'rm -rf.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 -print '
                        '-quit) || return 19; test -z "$extra" || return 19; if test -e "$s" || '
                        'test -L "$s"; then sg && rm -f -- "$s/a" "$s/b" && rmdir -- "$s" || '
                        'return 19; fi; cd "$HOME" && rmdir -- "$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-sticky.XXXXXX") && cd "$w" && pwd && here() { case "$w" in '
                          '"$HOME"/local-sticky.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                          '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" '
                          '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                          '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! -L "$f" || '
                          'return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Unique shared-directory setup and exact-path guard: here && s=$(mktemp '
                          '-d /tmp/ll-sticky.XXXXXX) && chmod 1777 "$s" && sg() { case "$s" in '
                          '/tmp/ll-sticky.??????) ;; *) return 19;; esac; test "${s%/*}" = /tmp && '
                          'test -d "$s" && test ! -L "$s" && test "$(realpath -e "$s")" = "$s" && '
                          'test "$(stat -c %U:%a "$s")" = learner:1777 || return 19; for n in a b; '
                          'do if test -e "$s/$n" || test -L "$s/$n"; then test ! -L "$s/$n" && '
                          'test -f "$s/$n" && test "$(stat -c %h "$s/$n")" = 1 && test "$(stat -c '
                          '%s "$s/$n")" -le 1024 || return 19; fi; done; members=$(find -P "$s" '
                          '-mindepth 1 -maxdepth 1 ! -name a ! -name b -print) || return 19; test '
                          '-z "$members"; }; here && sg && getent passwd ll-service nobody'],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 104.5. Self-reviewed and unscored: the '
                            'application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-sticky.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
               'in "$HOME"/local-sticky.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" '
               '&& test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
               '"$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for '
               'f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               'here && s=$(mktemp -d /tmp/ll-sticky.XXXXXX) && chmod 1777 "$s" && sg() { case '
               '"$s" in /tmp/ll-sticky.??????) ;; *) return 19;; esac; test "${s%/*}" = /tmp && '
               'test -d "$s" && test ! -L "$s" && test "$(realpath -e "$s")" = "$s" && test '
               '"$(stat -c %U:%a "$s")" = learner:1777 || return 19; for n in a b; do if test -e '
               '"$s/$n" || test -L "$s/$n"; then test ! -L "$s/$n" && test -f "$s/$n" && test '
               '"$(stat -c %h "$s/$n")" = 1 && test "$(stat -c %s "$s/$n")" -le 1024 || return 19; '
               'fi; done; members=$(find -P "$s" -mindepth 1 -maxdepth 1 ! -name a ! -name b '
               '-print) || return 19; test -z "$members"; }; here && sg && getent passwd '
               'll-service nobody',
               'here && sg && fresh "$s/a" "$s/b" && { sudo runuser -u ll-service -- sh -c '
               '\'printf "service\\n" > "$1/a" && chmod 0666 "$1/a"\' sh "$s" && sudo runuser -u '
               'nobody -- sh -c \'printf "nobody\\n" > "$1/b"\' sh "$s"; }',
               'here && sg && { sudo runuser -u nobody -- sh -c \'printf "append\\n" | dd '
               'of="$1/a" oflag=append,nofollow conv=notrunc,nocreat status=none\' sh "$s" && '
               'printf \'service\\nappend\\n\' | cmp - "$s/a" && test "$(stat -c %U:%a "$s/a")" = '
               'll-service:666 && { sudo runuser -u nobody -- rm -f -- "$s/a"; unlink_rc=$?; test '
               '"$unlink_rc" -ne 0 && test -f "$s/a" && printf \'service\\nappend\\n\' | cmp - '
               '"$s/a" && test "$(stat -c %U "$s/b")" = nobody && stat -c \'%U %a %n\' "$s" "$s/a" '
               '"$s/b"; }; }',
               'here && sg && { sudo runuser -u ll-service -- rm -f -- "$s/a" && rm -f -- "$s/b" '
               '&& rmdir -- "$s"; }'],
  'assertions': ['test ! -e "$s" && test ! -L "$s"', 'test "$unlink_rc" -ne 0'],
  'negative': ['test "$(getent passwd ll-service | cut -d : -f 7)" = /usr/sbin/nologin && test '
               '"$(id -un)" = learner',
               'here && fresh missing && { if dd of=missing oflag=append,nofollow '
               'conv=notrunc,nocreat status=none </dev/null; then false; else test ! -e missing && '
               'test ! -L missing; fi; }'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 -print '
                     '-quit) || return 19; test -z "$extra" || return 19; if test -e "$s" || test '
                     '-L "$s"; then sg && rm -f -- "$s/a" "$s/b" && rmdir -- "$s" || return 19; '
                     'fi; cd "$HOME" && rmdir -- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-sticky.XXXXXX") && cd "$w" && pwd && here() { '
                         'case "$w" in "$HOME"/local-sticky.??????) ;; *) return 19;; esac; test '
                         '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         'here && s=$(mktemp -d /tmp/ll-sticky.XXXXXX) && chmod 1777 "$s" && sg() '
                         '{ case "$s" in /tmp/ll-sticky.??????) ;; *) return 19;; esac; test '
                         '"${s%/*}" = /tmp && test -d "$s" && test ! -L "$s" && test "$(realpath '
                         '-e "$s")" = "$s" && test "$(stat -c %U:%a "$s")" = learner:1777 || '
                         'return 19; for n in a b; do if test -e "$s/$n" || test -L "$s/$n"; then '
                         'test ! -L "$s/$n" && test -f "$s/$n" && test "$(stat -c %h "$s/$n")" = 1 '
                         '&& test "$(stat -c %s "$s/$n")" -le 1024 || return 19; fi; done; '
                         'members=$(find -P "$s" -mindepth 1 -maxdepth 1 ! -name a ! -name b '
                         '-print) || return 19; test -z "$members"; }; here && sg && getent passwd '
                         'll-service nobody',
                         'here && sg && fresh "$s/a" "$s/b" && { sudo runuser -u ll-service -- sh '
                         '-c \'printf "service\\n" > "$1/a" && chmod 0666 "$1/a"\' sh "$s" && sudo '
                         'runuser -u nobody -- sh -c \'printf "nobody\\n" > "$1/b"\' sh "$s"; }',
                         'here && sg && { sudo runuser -u nobody -- sh -c \'printf "append\\n" | '
                         'dd of="$1/a" oflag=append,nofollow conv=notrunc,nocreat status=none\' sh '
                         '"$s" && printf \'service\\nappend\\n\' | cmp - "$s/a" && test "$(stat -c '
                         '%U:%a "$s/a")" = ll-service:666 && { sudo runuser -u nobody -- rm -f -- '
                         '"$s/a"; unlink_rc=$?; test "$unlink_rc" -ne 0 && test -f "$s/a" && '
                         'printf \'service\\nappend\\n\' | cmp - "$s/a" && test "$(stat -c %U '
                         '"$s/b")" = nobody && stat -c \'%U %a %n\' "$s" "$s/a" "$s/b"; }; }',
                         'here && sg && { sudo runuser -u ll-service -- rm -f -- "$s/a" && rm -f '
                         '-- "$s/b" && rmdir -- "$s"; }']},
 {'slug': 'priority',
  'id': 'real-linux-local-priority',
  'admin': True,
  'content': {'id': 'real-linux-local-priority',
              'content_version': '1.0.0',
              'title': 'Audit special bits and verify a scoped priority change',
              'goal': 'Inspect privileged bits read-only, then change niceness only for your '
                      'bounded owned task.',
              'challenge': 'Record a bounded read-only special-bit audit and explain why mode '
                           'alone does not prove safety. On an owned sleep task raise niceness, '
                           'demonstrate an unprivileged decrease is denied, then use approved '
                           'guest sudo to restore it. Retain actual PID/UID/start time and '
                           'niceness.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-priority.XXXXXX") && cd "$w" && '
                                    'pwd && here() { case "$w" in "$HOME"/local-priority.??????) '
                                    ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d '
                                    '"$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                                    '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! '
                                    '-L "$f" || return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && { find /usr/bin -maxdepth 1 -type f -perm /6000 '
                                    "-printf '%m %u %g %f\\n' | head -n 10; }",
                         'explanation': 'Read-only audit of setuid/setgid bits on this image. Do '
                                        'not create or execute a new setuid helper. This is '
                                        'neither a security verdict nor a full recursive system '
                                        'audit.',
                         'expected': 'At most ten rows; ownership/mode require context.'},
                        {'command': "here && { sleep 120 & task=$!; task_start=$(awk '{print $22}' "
                                    '/proc/"$task"/stat); owned() { test -n "$task" && test -f '
                                    '/proc/"$task"/stat && test "$(awk \'{print $22}\' '
                                    '/proc/"$task"/stat)" = "$task_start" && test "$(ps -o user= '
                                    '-p "$task" | xargs)" = learner && test "$(ps -o comm= -p '
                                    '"$task" | xargs)" = sleep; }; owned && ps -o '
                                    'pid=,user=,ni=,args= -p "$task"; }',
                         'explanation': 'One negligible-load task exits on its own within 120 '
                                        'seconds. Record PID/start time/owner, not a fixed PID. If '
                                        'it expires before testing, begin again; never control a '
                                        'reused PID.',
                         'expected': 'Owned learner sleep task and actual niceness.'},
                        {'command': 'here && owned && renice 5 -p "$task" && test "$(ps -o ni= -p '
                                    '"$task" | xargs)" = 5 && ps -o pid=,ni= -p "$task"',
                         'explanation': 'This verified util-linux renice form sets absolute '
                                        'niceness. Higher niceness lowers scheduling preference; '
                                        'it is not a guaranteed CPU percentage.',
                         'expected': 'Actual niceness 5.'},
                        {'command': 'here && owned && { renice 0 -p "$task"; denied_rc=$?; printf '
                                    '"unprivileged status=%s\\n" "$denied_rc"; test "$denied_rc" '
                                    '-ne 0 && test "$(ps -o ni= -p "$task" | xargs)" = 5; }',
                         'explanation': 'An ordinary user cannot normally decrease niceness. A '
                                        'failure message must be followed by actual state '
                                        'inspection.',
                         'expected': 'Denied request; task remains at 5.'},
                        {'command': 'here && owned && sudo renice 0 -p "$task" && test "$(ps -o '
                                    'ni= -p "$task" | xargs)" = 0 && ps -o pid=,ni= -p "$task"',
                         'explanation': 'Guest-only approved administrator privilege. Recheck the '
                                        'exact owned task immediately before requesting a change. '
                                        'No host priority is touched.',
                         'expected': 'Actual niceness returns to 0.'},
                        {'command': 'here && { if test -e /proc/"$task"/stat; then owned && kill '
                                    '-TERM "$task"; fi; wait "$task"; test ! -e /proc/"$task"; }',
                         'explanation': 'Signal only this matching owned bounded task. wait may '
                                        'return a signal status; final absence is the intended '
                                        'result. No broad kill command.',
                         'expected': 'Task has exited; no leftover workload.'}],
              'hints': ['Inspect state after denied renice.',
                        'Use only your recorded task and recheck owner/start.',
                        'Do not create special-bit executables or alter other processes.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 104.5 /103.6 /110.1. Self-reviewed and unscored: '
                          'the application does not inspect guest results. No full-objective or '
                          'exam-readiness claim.'},
  'entry': {'id': 'real-linux-local-priority',
            'resource': 'real-linux-local-priority.json',
            'description': 'Inspect privileged bits read-only, then change niceness only for your '
                           'bounded owned task.',
            'objectives': ['104.5 /103.6 /110.1 — narrow real-guest practice; completion is '
                           'self-reviewed.'],
            'troubleshooting': ['Niceness is not CPU utilization or a realtime priority guarantee.',
                                'A stale PID is not authority to signal a process.',
                                'A privileged-bit match does not prove the executable is '
                                'vulnerable or trustworthy.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 -print '
                        '-quit) || return 19; test -z "$extra" || return 19; if test -e '
                        '/proc/"$task"/stat; then owned && kill -TERM "$task" || return 19; wait '
                        '"$task"; fi; cd "$HOME" && rmdir -- "$w"; }; clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-priority.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
                          'in "$HOME"/local-priority.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                          'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! '
                          '-e "$f" && test ! -L "$f" || return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Bounded task setup and identity guard: here && { sleep 120 & task=$!; '
                          'task_start=$(awk \'{print $22}\' /proc/"$task"/stat); owned() { test -n '
                          '"$task" && test -f /proc/"$task"/stat && test "$(awk \'{print $22}\' '
                          '/proc/"$task"/stat)" = "$task_start" && test "$(ps -o user= -p "$task" '
                          '| xargs)" = learner && test "$(ps -o comm= -p "$task" | xargs)" = '
                          'sleep; }; owned && ps -o pid=,user=,ni=,args= -p "$task"; }'],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 104.5 /103.6 /110.1. Self-reviewed and unscored: '
                            'the application does not inspect guest results. No full-objective or '
                            'exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-priority.XXXXXX") && cd "$w" && pwd && here() { case '
               '"$w" in "$HOME"/local-priority.??????) ;; *) return 19;; esac; test "${w%/*}" = '
               '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
               'test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() '
               '{ for f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               "here && { find /usr/bin -maxdepth 1 -type f -perm /6000 -printf '%m %u %g %f\\n' | "
               'head -n 10; }',
               "here && { sleep 120 & task=$!; task_start=$(awk '{print $22}' "
               '/proc/"$task"/stat); owned() { test -n "$task" && test -f /proc/"$task"/stat && '
               'test "$(awk \'{print $22}\' /proc/"$task"/stat)" = "$task_start" && test "$(ps -o '
               'user= -p "$task" | xargs)" = learner && test "$(ps -o comm= -p "$task" | xargs)" = '
               'sleep; }; owned && ps -o pid=,user=,ni=,args= -p "$task"; }',
               'here && owned && renice 5 -p "$task" && test "$(ps -o ni= -p "$task" | xargs)" = 5 '
               '&& ps -o pid=,ni= -p "$task"',
               'here && owned && { renice 0 -p "$task"; denied_rc=$?; printf "unprivileged '
               'status=%s\\n" "$denied_rc"; test "$denied_rc" -ne 0 && test "$(ps -o ni= -p '
               '"$task" | xargs)" = 5; }',
               'here && owned && sudo renice 0 -p "$task" && test "$(ps -o ni= -p "$task" | '
               'xargs)" = 0 && ps -o pid=,ni= -p "$task"',
               'here && { if test -e /proc/"$task"/stat; then owned && kill -TERM "$task"; fi; '
               'wait "$task"; test ! -e /proc/"$task"; }'],
  'assertions': ['test ! -e /proc/"$task"', 'test "$denied_rc" -ne 0'],
  'negative': ['test "$(id -un)" = learner && ! owned && test "$denied_rc" -ne 0'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 -print '
                     '-quit) || return 19; test -z "$extra" || return 19; if test -e '
                     '/proc/"$task"/stat; then owned && kill -TERM "$task" || return 19; wait '
                     '"$task"; fi; cd "$HOME" && rmdir -- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-priority.XXXXXX") && cd "$w" && pwd && here() '
                         '{ case "$w" in "$HOME"/local-priority.??????) ;; *) return 19;; esac; '
                         'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         "here && { find /usr/bin -maxdepth 1 -type f -perm /6000 -printf '%m %u "
                         "%g %f\\n' | head -n 10; }",
                         "here && { sleep 120 & task=$!; task_start=$(awk '{print $22}' "
                         '/proc/"$task"/stat); owned() { test -n "$task" && test -f '
                         '/proc/"$task"/stat && test "$(awk \'{print $22}\' /proc/"$task"/stat)" = '
                         '"$task_start" && test "$(ps -o user= -p "$task" | xargs)" = learner && '
                         'test "$(ps -o comm= -p "$task" | xargs)" = sleep; }; owned && ps -o '
                         'pid=,user=,ni=,args= -p "$task"; }',
                         'here && owned && renice 5 -p "$task" && test "$(ps -o ni= -p "$task" | '
                         'xargs)" = 5 && ps -o pid=,ni= -p "$task"',
                         'here && owned && { renice 0 -p "$task"; denied_rc=$?; printf '
                         '"unprivileged status=%s\\n" "$denied_rc"; test "$denied_rc" -ne 0 && '
                         'test "$(ps -o ni= -p "$task" | xargs)" = 5; }',
                         'here && owned && sudo renice 0 -p "$task" && test "$(ps -o ni= -p '
                         '"$task" | xargs)" = 0 && ps -o pid=,ni= -p "$task"',
                         'here && { if test -e /proc/"$task"/stat; then owned && kill -TERM '
                         '"$task"; fi; wait "$task"; test ! -e /proc/"$task"; }']},
 {'slug': 'handover',
  'id': 'real-linux-local-handover',
  'admin': False,
  'content': {'id': 'real-linux-local-handover',
              'content_version': '1.0.0',
              'title': 'Repair links and deliver an independent handover',
              'goal': 'Transfer startup, link and search skills to an incident while preserving '
                      'the source.',
              'challenge': 'Repair the relative current link, make an independent readable '
                           'handover copy with mode 0640, find the supplied stale reference and '
                           'explain isolated startup versus persistent disk state. Preserve source '
                           'bytes/mode and record facts separately from hypotheses. Use any valid '
                           'scoped approach.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/local-handover.XXXXXX") && cd "$w" && '
                                    'pwd && here() { case "$w" in "$HOME"/local-handover.??????) '
                                    ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d '
                                    '"$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd '
                                    '-P)" = "$w"; }; fresh() { for f; do test ! -e "$f" && test ! '
                                    '-L "$f" || return 19; done; }; here',
                         'explanation': 'Create a unique learner-owned guest workspace; stop on '
                                        'error and record its absolute path. Reopening boots the '
                                        'disk, not these shell variables. Never use the host '
                                        'terminal.',
                         'expected': 'A new private directory; no pre-existing files are changed.'},
                        {'command': 'here && fresh records links original.sha256 original.meta '
                                    'unsafe-copy.txt stale.txt && { mkdir records links; printf '
                                    "'approved handover\\n' > records/source.txt; chmod 0640 "
                                    'records/source.txt; sha256sum records/source.txt > '
                                    "original.sha256; stat -c '%a %h' records/source.txt > "
                                    'original.meta; ln -s ../missing.txt links/current; ln '
                                    "records/source.txt unsafe-copy.txt; printf 'obsolete path: "
                                    "missing.txt\\n' > stale.txt; }",
                         'explanation': 'Initial wrong link and incorrectly shared copy. The '
                                        'independent checks describe the original. Do not edit '
                                        'source or unsafe-copy contents.',
                         'expected': 'Source, wrong relative link, shared inode and stale '
                                     'reference.'},
                        {'command': 'here && { readlink links/current; stat -c "%d:%i %h %a %n" '
                                    'records/source.txt unsafe-copy.txt; find -P . -maxdepth 2 '
                                    '-type f -name "*.txt" -print; }',
                         'explanation': 'Investigate before mutation. Challenge supplies only the '
                                        'first fixture step plus outcomes; these following '
                                        'commands are Learn suggestions, not a required '
                                        'transcript.',
                         'expected': 'Evidence identifies the wrong target and shared copy.'},
                        {'command': 'here && { test -L links/current && rm -- links/current && ln '
                                    '-s ../records/source.txt links/current && rm -- '
                                    'unsafe-copy.txt && cp -p records/source.txt handover.txt; }',
                         'explanation': 'Remove only verified faulty names, then make an '
                                        'independent copy. Removing unsafe-copy restores the '
                                        'source link count to the initial reference before that '
                                        'link was created.',
                         'expected': 'Correct link and independent copy; source preserved.'},
                        {'command': 'here && { cat links/current handover.txt; sha256sum -c '
                                    'original.sha256; test "$(stat -c \'%a %h\' '
                                    'records/source.txt)" = "$(cat original.meta)"; stat -c "%d:%i '
                                    '%a %n" records/source.txt handover.txt; }',
                         'explanation': 'Verify bytes, original metadata and independent inode. A '
                                        'successful ln/cp alone is not enough.',
                         'expected': 'Correct contents, mode 640 and different copy inode.'},
                        {'command': "here && { printf '%s\\n' 'FACT: current resolves to preserved "
                                    "source' 'FACT: handover has independent inode and mode 640' "
                                    "'FACT: stale reference still retained for review' 'LIMIT: "
                                    "shell variables and jobs do not survive disk Resume' 'NEXT: "
                                    "review consumers before removing stale reference' > "
                                    'report.txt; cat report.txt; }',
                         'explanation': 'Your report may use different words. Review factual '
                                        'accuracy against actual output; the app records '
                                        'self-review only, not a keyword score.',
                         'expected': 'Concise factual handover and uncertainty, with original '
                                     'retained.'}],
              'hints': ['Find which names share an inode before editing.',
                        'Repair only the wrong link; preserve the independent expectations.',
                        'Separate demonstrated facts from causal hypotheses.'],
              'review': ['I retained actual output and checked the required contents, metadata or '
                         'identity, not just command success.',
                         'I can explain the stated limitations, demonstrate the incorrect case, '
                         'preserve originals and clean up only my recorded workspace.'],
              'coverage': 'LPIC-1 v5.0 partial 104.6 /104.7 /105.1 reinforcement. Self-reviewed '
                          'and unscored: the application does not inspect guest results. No '
                          'full-objective or exam-readiness claim.'},
  'entry': {'id': 'real-linux-local-handover',
            'resource': 'real-linux-local-handover.json',
            'description': 'Transfer startup, link and search skills to an incident while '
                           'preserving the source.',
            'objectives': ['104.6 /104.7 /105.1 reinforcement — narrow real-guest practice; '
                           'completion is self-reviewed.'],
            'troubleshooting': ['Editing the initial hard link would alter the protected source.',
                                'A checksum passing does not prove independent inode or narrow '
                                'mode.',
                                'Do not delete stale evidence merely to make the directory look '
                                'clean.'],
            'cleanup': ['Re-establish only the recorded lesson workspace/identity variables and '
                        'guards after reopening. This command checks exact members and expected '
                        'types before deleting known files. It is a cooperative practice guard, '
                        'not protection against guest root or concurrent hostile substitution.',
                        'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( '
                        "-path './links/current' -o -path './records/source.txt' -o -path "
                        "'./original.sha256' -o -path './original.meta' -o -path './stale.txt' -o "
                        "-path './handover.txt' -o -path './report.txt' -o -path './links' -o "
                        '-path \'./records\' \\) -print -quit) || return 19; test -z "$extra" || '
                        'return 19; test -d links && test ! -L links || return 19; test -d records '
                        '&& test ! -L records || return 19; test -L links/current || return 19; '
                        'test -f records/source.txt && test ! -L records/source.txt || return 19; '
                        'test -f original.sha256 && test ! -L original.sha256 || return 19; test '
                        '-f original.meta && test ! -L original.meta || return 19; test -f '
                        'stale.txt && test ! -L stale.txt || return 19; test -f handover.txt && '
                        'test ! -L handover.txt || return 19; test -f report.txt && test ! -L '
                        'report.txt || return 19; rm -- links/current records/source.txt '
                        'original.sha256 original.meta stale.txt handover.txt report.txt || return '
                        '19; rmdir -- links records || return 19; cd "$HOME" && rmdir -- "$w"; }; '
                        'clean_local',
                        'If refusal occurs, inspect and retain the workspace. Confirmed Reset '
                        'retains the old disk; never use recursive deletion or adopt a foreign '
                        'path.'],
            'materials': ['Start a unique workspace and define accident guards: w=$(mktemp -d '
                          '"$HOME/local-handover.XXXXXX") && cd "$w" && pwd && here() { case "$w" '
                          'in "$HOME"/local-handover.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                          'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! '
                          '-e "$f" && test ! -L "$f" || return 19; done; }; here',
                          'Mutations stay inside the recorded w; sticky additionally permits its '
                          'unique /tmp/ll-sticky.* directory. Priority includes read-only /usr/bin '
                          'audit and /proc identity queries for its owned bounded task. No '
                          'account, authentication, sudo policy or package changes.',
                          'Challenge has independent outcomes, not an automatically scored '
                          'transcript. Record the workspace before closing; Resume does not '
                          'preserve RAM, shell variables or jobs.',
                          'Trusted initial exercise fixture (not the repair): here && fresh '
                          'records links original.sha256 original.meta unsafe-copy.txt stale.txt '
                          "&& { mkdir records links; printf 'approved handover\\n' > "
                          'records/source.txt; chmod 0640 records/source.txt; sha256sum '
                          "records/source.txt > original.sha256; stat -c '%a %h' "
                          'records/source.txt > original.meta; ln -s ../missing.txt links/current; '
                          "ln records/source.txt unsafe-copy.txt; printf 'obsolete path: "
                          "missing.txt\\n' > stale.txt; }"],
            'observations': ['Retain actual commands, exit status and output for the Challenge '
                             'outcomes.',
                             'Record what an incorrect attempt demonstrates and what remains '
                             'uncertain.'],
            'questions': ['Which observations prove the requested outcome rather than merely '
                          'successful execution?',
                          'What would change outside this bounded exercise?'],
            'limitations': ['LPIC-1 v5.0 partial 104.6 /104.7 /105.1 reinforcement. Self-reviewed '
                            'and unscored: the application does not inspect guest results. No '
                            'full-objective or exam-readiness claim.',
                            'No automatic guest assessment, credentials, networking or image '
                            'changes.',
                            'Guest-only cooperative guards prevent common accidents, not '
                            'hostile-root actions. History/editor settings are child-local; shell '
                            'variables are not recorded by the app.']},
  'commands': ['w=$(mktemp -d "$HOME/local-handover.XXXXXX") && cd "$w" && pwd && here() { case '
               '"$w" in "$HOME"/local-handover.??????) ;; *) return 19;; esac; test "${w%/*}" = '
               '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
               'test "$(stat -c %U:%a "$w")" = learner:700 && test "$(pwd -P)" = "$w"; }; fresh() '
               '{ for f; do test ! -e "$f" && test ! -L "$f" || return 19; done; }; here',
               'here && fresh records links original.sha256 original.meta unsafe-copy.txt '
               "stale.txt && { mkdir records links; printf 'approved handover\\n' > "
               'records/source.txt; chmod 0640 records/source.txt; sha256sum records/source.txt > '
               "original.sha256; stat -c '%a %h' records/source.txt > original.meta; ln -s "
               '../missing.txt links/current; ln records/source.txt unsafe-copy.txt; printf '
               "'obsolete path: missing.txt\\n' > stale.txt; }",
               'here && { readlink links/current; stat -c "%d:%i %h %a %n" records/source.txt '
               'unsafe-copy.txt; find -P . -maxdepth 2 -type f -name "*.txt" -print; }',
               'here && { test -L links/current && rm -- links/current && ln -s '
               '../records/source.txt links/current && rm -- unsafe-copy.txt && cp -p '
               'records/source.txt handover.txt; }',
               'here && { cat links/current handover.txt; sha256sum -c original.sha256; test '
               '"$(stat -c \'%a %h\' records/source.txt)" = "$(cat original.meta)"; stat -c "%d:%i '
               '%a %n" records/source.txt handover.txt; }',
               "here && { printf '%s\\n' 'FACT: current resolves to preserved source' 'FACT: "
               "handover has independent inode and mode 640' 'FACT: stale reference still retained "
               "for review' 'LIMIT: shell variables and jobs do not survive disk Resume' 'NEXT: "
               "review consumers before removing stale reference' > report.txt; cat report.txt; }"],
  'assertions': ['sha256sum -c original.sha256 && test "$(stat -c %i records/source.txt)" != '
                 '"$(stat -c %i handover.txt)" && test "$(stat -c %a handover.txt)" = 640 && grep '
                 '-qx "approved handover" links/current && test -f stale.txt',
                 'test "$(stat -c \'%a %h\' records/source.txt)" = "$(cat original.meta)"'],
  'negative': ['chmod 0644 handover.txt && test "$(stat -c %a handover.txt)" != 640 && chmod 0640 '
               'handover.txt'],
  'cleanup_command': 'clean_local() { here || return 19; extra=$(find -P . -mindepth 1 ! \\( -path '
                     "'./links/current' -o -path './records/source.txt' -o -path "
                     "'./original.sha256' -o -path './original.meta' -o -path './stale.txt' -o "
                     "-path './handover.txt' -o -path './report.txt' -o -path './links' -o -path "
                     '\'./records\' \\) -print -quit) || return 19; test -z "$extra" || return 19; '
                     'test -d links && test ! -L links || return 19; test -d records && test ! -L '
                     'records || return 19; test -L links/current || return 19; test -f '
                     'records/source.txt && test ! -L records/source.txt || return 19; test -f '
                     'original.sha256 && test ! -L original.sha256 || return 19; test -f '
                     'original.meta && test ! -L original.meta || return 19; test -f stale.txt && '
                     'test ! -L stale.txt || return 19; test -f handover.txt && test ! -L '
                     'handover.txt || return 19; test -f report.txt && test ! -L report.txt || '
                     'return 19; rm -- links/current records/source.txt original.sha256 '
                     'original.meta stale.txt handover.txt report.txt || return 19; rmdir -- links '
                     'records || return 19; cd "$HOME" && rmdir -- "$w"; }; clean_local',
  'challenge_commands': ['w=$(mktemp -d "$HOME/local-handover.XXXXXX") && cd "$w" && pwd && here() '
                         '{ case "$w" in "$HOME"/local-handover.??????) ;; *) return 19;; esac; '
                         'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                         '"$(realpath -e "$w")" = "$w" && test "$(stat -c %U:%a "$w")" = '
                         'learner:700 && test "$(pwd -P)" = "$w"; }; fresh() { for f; do test ! -e '
                         '"$f" && test ! -L "$f" || return 19; done; }; here',
                         'here && fresh records links original.sha256 original.meta '
                         "unsafe-copy.txt stale.txt && { mkdir records links; printf 'approved "
                         "handover\\n' > records/source.txt; chmod 0640 records/source.txt; "
                         "sha256sum records/source.txt > original.sha256; stat -c '%a %h' "
                         'records/source.txt > original.meta; ln -s ../missing.txt links/current; '
                         "ln records/source.txt unsafe-copy.txt; printf 'obsolete path: "
                         "missing.txt\\n' > stale.txt; }",
                         'here && { readlink links/current; stat -c "%d:%i %h %a %n" '
                         'records/source.txt unsafe-copy.txt; find -P . -maxdepth 2 -type f -name '
                         '"*.txt" -print; }',
                         'here && { test -L links/current && rm -- links/current && ln -s '
                         '../records/source.txt links/current && rm -- unsafe-copy.txt && cp -p '
                         'records/source.txt handover.txt; }',
                         'here && { cat links/current handover.txt; sha256sum -c original.sha256; '
                         'test "$(stat -c \'%a %h\' records/source.txt)" = "$(cat original.meta)"; '
                         'stat -c "%d:%i %a %n" records/source.txt handover.txt; }',
                         "here && { printf '%s\\n' 'FACT: current resolves to preserved source' "
                         "'FACT: handover has independent inode and mode 640' 'FACT: stale "
                         "reference still retained for review' 'LIMIT: shell variables and jobs do "
                         "not survive disk Resume' 'NEXT: review consumers before removing stale "
                         "reference' > report.txt; cat report.txt; }"]}]
COMMANDS={x["id"]:x["commands"] for x in DATA}
