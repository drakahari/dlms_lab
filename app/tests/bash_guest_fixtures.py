"""Static developer guest input. Never imported by application code or read from lesson JSON."""
UNIT = 'lpic-bash-regex-safe-files'
COMMANDS = {'real-linux-bash-files': ['work=$(mktemp -d "$HOME/bash-files.XXXXXX") && cd "$work" && pwd',
                           "mkdir input picked; printf '%s\\n' red > 'input/red note.txt'; printf "
                           "'%s\\n' blue > 'input/blue\\path.txt'; printf '%s\\n' keep > "
                           'input/keep.log',
                           "find input -maxdepth 1 -type f -name '*.txt' -print; printf '<%s>\\n' "
                           'input/*.txt',
                           "cp -p -- 'input/red note.txt' picked/; cp -p -- 'input/blue\\path.txt' "
                           'picked/',
                           "cmp -- 'input/red note.txt' 'picked/red note.txt'; cmp -- "
                           "'input/blue\\path.txt' 'picked/blue\\path.txt'; cat input/keep.log"],
 'real-linux-bash-environment': ['work=$(mktemp -d "$HOME/bash-environment.XXXXXX") && cd "$work" '
                                 '&& pwd',
                                 "saved_path=$PATH; note='local value'; unset LAB_NOTE; type "
                                 'printf; printf \'<%s>\\n\' "$note"',
                                 'bash -c \'printf "child note=<%s>\\n" "${note-unset}"\'',
                                 "LAB_NOTE='child value'; export LAB_NOTE; bash -c 'printf "
                                 '"child LAB_NOTE=<%s>\\n" "$LAB_NOTE"\'',
                                 'PATH=/usr/bin:/bin; export PATH; type -a printf; command -v '
                                 "bash; /usr/bin/printf '%s\\n' absolute",
                                 "PATH=$saved_path; export PATH; unset LAB_NOTE note; printf 'PATH "
                                 'restored=%s\\n\' "$PATH"'],
 'real-linux-bash-quoting': ['work=$(mktemp -d "$HOME/bash-quoting.XXXXXX") && cd "$work" && pwd',
                             "value='two words'; printf '%s\\n' alpha > 'red note.txt'; printf "
                             "'%s\\n' beta > 'back\\slash.txt'",
                             'printf \'<%s>\\n\' \'$value\' "$value" \'*.txt\' > quoted.txt; cat '
                             'quoted.txt',
                             "printf '<%s>\\n' ./*.txt",
                             'here=$(pwd); printf \'<%s>\\n\' "$here" > location.txt; printf '
                             "'%s\\n' 'literal $(touch surprise)' > literal.txt",
                             "cat literal.txt; test ! -e surprise; printf 'literal status=%s\\n' "
                             '"$?"'],
 'real-linux-bash-streams': ['work=$(mktemp -d "$HOME/bash-streams.XXXXXX") && cd "$work" && pwd',
                             "printf '%s\\n' alpha beta > input.txt; printf '%s\\n' retained > "
                             'empty.txt',
                             'cat < input.txt > copy.txt; cat missing.txt > empty.txt 2> '
                             'errors.txt; failed=$?; printf \'failed=%s\\n\' "$failed" > '
                             'status.txt',
                             'set +o pipefail; cat missing.txt 2> pipe-errors.txt | wc -l > '
                             'count.txt; printf \'default=%s\\n\' "$?" >> status.txt',
                             'set -o pipefail; cat missing.txt 2>> pipe-errors.txt | wc -l > '
                             'count.txt; printf \'pipefail=%s\\n\' "$?" >> status.txt; set +o '
                             'pipefail',
                             "printf '%s\\n' observed | tee observed.txt; cat status.txt; cmp "
                             'input.txt copy.txt'],
 'real-linux-bash-regex': ['work=$(mktemp -d "$HOME/bash-regex.XXXXXX") && cd "$work" && pwd',
                           "printf '%s\\n' 'app-01 ok' 'app-02 fail' 'backup-3 fail' 'app-001 "
                           "fail' 'literal.a' 'literalXa' '' > records.txt",
                           "LC_ALL=C grep '^app-[0-9][0-9] ' records.txt > bre.txt; LC_ALL=C grep "
                           "-E '^app-[0-9]{2} (ok|fail)$' records.txt > ere.txt; cmp bre.txt "
                           'ere.txt',
                           "grep -F 'literal.a' records.txt > fixed.txt; grep 'literal.a' "
                           'records.txt > wildcard.txt; cat fixed.txt wildcard.txt',
                           "grep -E '^$' records.txt > blank.txt; grep -E '^db-' records.txt > "
                           'none.txt; printf \'none=%s\\n\' "$?" > status.txt',
                           "grep -E '[' records.txt > invalid-output.txt 2> invalid.txt; printf "
                           '\'invalid=%s\\n\' "$?" >> status.txt; cat status.txt'],
 'real-linux-bash-transform': ['work=$(mktemp -d "$HOME/bash-transform.XXXXXX") && cd "$work" && '
                               'pwd',
                               "printf '%s\\n' '# label=old' 'port=8080' 'label=old' > "
                               'original.conf; cp -p original.conf working.conf; sha256sum '
                               'original.conf > original.sha256',
                               "sed 's/^label=old$/label=new/' working.conf",
                               "sed 's/^label=old$/label=new/' working.conf > candidate.conf; diff "
                               '-u original.conf candidate.conf',
                               "grep -Fx 'port=8080' candidate.conf; grep -Fx 'label=new' "
                               'candidate.conf; cp -p working.conf before.conf; cp -p '
                               'candidate.conf working.conf; cmp candidate.conf working.conf; '
                               'sha256sum -c original.sha256',
                               'cp -p before.conf working.conf; cmp original.conf working.conf; '
                               'printf \'rollback=%s\\n\' "$?"'],
 'real-linux-bash-vi': ['work=$(mktemp -d "$HOME/bash-vi.XXXXXX") && cd "$work" && pwd',
                        "printf '%s\\n' Alpha Beta Gamma > note.txt; cp -p note.txt original.txt",
                        'vi note.txt',
                        'cat note.txt; diff -u original.txt note.txt; command -v vi; vi --version '
                        '| head -2'],
 'real-linux-bash-rollback': ['work=$(mktemp -d "$HOME/bash-rollback.XXXXXX") && cd "$work" && pwd',
                              "printf '%s\\n' safe 'retained line' > note.txt; cp -p note.txt "
                              'original.txt; sha256sum original.txt > original.sha256',
                              'vi note.txt',
                              'cmp original.txt note.txt; vi note.txt',
                              'diff -u original.txt note.txt; cp -p note.txt saved-mistake.txt; cp '
                              '-p original.txt note.txt; cmp original.txt note.txt; sha256sum -c '
                              'original.sha256'],
 'real-linux-bash-script': ['work=$(mktemp -d "$HOME/bash-script.XXXXXX") && cd "$work" && pwd',
                            'nano check-note.sh',
                            'bash -n check-note.sh; printf \'syntax=%s\\n\' "$?"; bash '
                            "check-note.sh 'red note.txt'",
                            "./check-note.sh 'red note.txt'; printf 'direct before chmod=%s\\n' "
                            '"$?"; chmod u+x check-note.sh',
                            "timeout -k 2s 5s ./check-note.sh 'red note.txt' > target.txt; printf "
                            '\'run=%s\\n\' "$?" > status.txt; timeout -k 2s 5s ./check-note.sh > '
                            'bad-output.txt 2> usage.txt; printf \'usage=%s\\n\' "$?" >> '
                            'status.txt; cat target.txt status.txt'],
 'real-linux-bash-guards': ['work=$(mktemp -d "$HOME/bash-guards.XXXXXX") && cd "$work" && pwd',
                            "printf '%s\\n' READY > 'ready note.txt'; : > empty.txt; printf "
                            "'%s\\n' WAIT > wrong.txt",
                            'nano guarded.sh',
                            'bash -n guarded.sh; chmod u+x guarded.sh; timeout -k 2s 5s '
                            "./guarded.sh 'ready note.txt' > good.txt; printf 'good=%s\\n' "
                            '"$?" > status.txt',
                            'timeout -k 2s 5s ./guarded.sh missing.txt > failed.txt 2> errors.txt; '
                            'printf \'missing=%s\\n\' "$?" >> status.txt; timeout -k 2s 5s '
                            './guarded.sh empty.txt >> failed.txt 2>> errors.txt; printf '
                            '\'empty=%s\\n\' "$?" >> status.txt',
                            'timeout -k 2s 5s ./guarded.sh wrong.txt >> failed.txt 2>> errors.txt; '
                            'printf \'content=%s\\n\' "$?" >> status.txt; timeout -k 2s 5s '
                            './guarded.sh >> failed.txt 2>> errors.txt; printf \'args=%s\\n\' "$?" '
                            '>> status.txt; cat status.txt errors.txt'],
 'real-linux-bash-records': ['work=$(mktemp -d "$HOME/bash-records.XXXXXX") && cd "$work" && pwd',
                             "printf '%s\\n' 'two words' 'back\\slash' '' > records.txt; printf "
                             'tail >> records.txt; : > empty.txt',
                             'nano records.sh',
                             'bash -n records.sh; chmod u+x records.sh; timeout -k 2s 5s '
                             './records.sh records.txt > result.txt; timeout -k 2s 5s ./records.sh '
                             'empty.txt > empty-result.txt; cat result.txt empty-result.txt',
                             "printf '%s\\n' 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 "
                             '> too-many.txt; timeout -k 2s 5s ./records.sh too-many.txt > '
                             'partial.txt 2> errors.txt; printf \'bounded status=%s\\n\' "$?"'],
 'real-linux-bash-handover': ['work=$(mktemp -d "$HOME/bash-handover.XXXXXX") && cd "$work" && pwd',
                              "printf '%s\\n' 'app one|ok' 'store\\east|fail' 'cache|fail' > "
                              "checks.txt; printf '%s\\n' '#!/bin/bash' 'input=$1' 'grep -F "
                              '"|fail" "$input" | wc -l\' > report.sh',
                              'bash -n report.sh; bash report.sh checks.txt; cp -p report.sh '
                              'original.sh; sha256sum original.sh > original.sha256; nano '
                              'report.sh',
                              'bash -n report.sh; chmod u+x report.sh; timeout -k 2s 5s '
                              './report.sh checks.txt > report.candidate 2> errors.txt; rc=$?; if '
                              '[ "$rc" -eq 0 ]; then cp -p report.candidate report.txt; else '
                              'printf \'report refused: %s\\n\' "$rc"; fi; cat report.txt',
                              "printf '%s\\n' stray > bad.txt; timeout -k 2s 5s ./report.sh "
                              'bad.txt > report.candidate 2> errors.txt; rc=$?; if [ "$rc" -eq 0 '
                              "]; then cp -p report.candidate report.txt; else printf 'report "
                              'preserved, status=%s\\n\' "$rc"; fi; sha256sum -c original.sha256',
                              'nano handover.txt',
                              'cp -p report.sh corrected.sh; cp -p original.sh report.sh; cmp '
                              'original.sh report.sh; timeout -k 2s 5s ./corrected.sh checks.txt > '
                              'repeated.txt; cmp report.txt repeated.txt']}
SCRIPT_ROWS = {'script': ['#!/bin/bash',
            'if [ "$#" -ne 1 ]; then',
            "  printf 'usage: check-note FILE\\n' >&2",
            '  exit 2',
            'fi',
            'printf \'target=<%s>\\n\' "$1"'],
 'guards': ['#!/bin/bash',
            'if [ "$#" -ne 1 ]; then printf \'usage: guarded FILE\\n\' >&2; exit 2; fi',
            'input=$1',
            'if [ ! -f "$input" ] || [ ! -r "$input" ]; then',
            "  printf 'unreadable file\\n' >&2; exit 3",
            'fi',
            'if [ ! -s "$input" ]; then',
            "  printf 'empty file\\n' >&2; exit 4",
            'fi',
            'grep -qx -- READY < "$input"; status=$?',
            'if [ "$status" -ne 0 ]; then',
            '  printf \'READY check failed, grep status=%s\\n\' "$status" >&2; exit 5',
            'fi',
            'printf \'ready: %s\\n\' "$input"'],
 'records': ['#!/bin/bash',
             'if [ "$#" -ne 1 ] || [ ! -f "$1" ] || [ ! -r "$1" ]; then exit 2; fi',
             '[ "$(wc -c < "$1")" -le 2048 ] || exit 3',
             'show() { printf \'<%s>\\n\' "$1"; }',
             'n=0',
             'while IFS= read -r line || [ -n "$line" ]; do',
             '  n=$((n+1))',
             '  [ "$n" -le 20 ] || { printf \'too many records\\n\' >&2; exit 4; }',
             '  show "$line"',
             'done < "$1"',
             'printf \'records=%s\\n\' "$n"'],
 'handover': ['#!/bin/bash',
              'if [ "$#" -ne 1 ] || [ ! -f "$1" ] || [ ! -r "$1" ]; then exit 2; fi',
              '[ "$(wc -c < "$1")" -le 2048 ] || exit 2',
              'ok=0; failed=0; n=0',
              'while IFS= read -r line || [ -n "$line" ]; do',
              '  n=$((n+1)); [ "$n" -le 20 ] || exit 4',
              '  case "$line" in *\'|\'*) ;; *) printf \'missing delimiter\\n\' >&2; exit 3;; esac',
              '  name=${line%|*}; state=${line##*|}',
              '  case "$name" in \'\'|*\'|\'*) printf \'invalid name\\n\' >&2; exit 3;; esac',
              '  case "$state" in',
              '    ok) ok=$((ok+1));;',
              '    fail) failed=$((failed+1)); printf \'FAIL %s\\n\' "$name";;',
              '    *) printf "invalid record\\n" >&2; exit 3;;',
              '  esac',
              'done < "$1"',
              'printf \'ok=%s fail=%s\\n\' "$ok" "$failed"']}
