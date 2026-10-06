"""Trusted static developer commands; never loaded from lesson JSON at runtime."""
UNIT='linux-backup-safe-recovery'
COMMANDS={'real-linux-backup-requirements': ['w=/home/learner/ll-backup-1; test "$(id -un)" = learner && test ! -e '
                                    '"$w" && test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && test '
                                    '"$(df -Pk . | awk \'NR==2 {print $4}\')" -ge 65536',
                                    'guard() { test "$(pwd -P)" = /home/learner/ll-backup-1 && test ! -L '
                                    '/home/learner/ll-backup-1 && test "$(stat -c %U .)" = learner && test '
                                    '-z "$(find . -type l -print -quit)"; }; guard',
                                    "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                                    "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 "
                                    "source/note.txt && chmod 0600 'source/space name.txt' && touch -d "
                                    "'2026-01-01 00:00:00 UTC' source/note.txt 'source/space name.txt'",
                                    "guard && printf '%s\\n' 'Files: note.txt and space name.txt' 'Bytes: "
                                    "alpha and bravo, each ending in newline' 'Modes: 640 and 600; "
                                    "owner/group learner' 'mtime: 2026-01-01 UTC; recover within this "
                                    "practice session' 'RPO: this fixture snapshot; RTO: inspect and restore "
                                    "manually' > requirements.txt",
                                    "guard && (cd source && sha256sum -- note.txt 'space name.txt') > "
                                    "expected.sha256 && stat -c '%n %U:%G %a %Y %s' source/note.txt "
                                    "'source/space name.txt' > expected.metadata && cat requirements.txt "
                                    'expected.metadata'],
 'real-linux-backup-archive': ['w=/home/learner/ll-backup-2; test "$(id -un)" = learner && test ! -e "$w" && '
                               'test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && test "$(df -Pk . | '
                               'awk \'NR==2 {print $4}\')" -ge 65536',
                               'guard() { test "$(pwd -P)" = /home/learner/ll-backup-2 && test ! -L '
                               '/home/learner/ll-backup-2 && test "$(stat -c %U .)" = learner && test -z '
                               '"$(find . -type l -print -quit)"; }; guard',
                               "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                               "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 source/note.txt && "
                               "chmod 0600 'source/space name.txt' && touch -d '2026-01-01 00:00:00 UTC' "
                               "source/note.txt 'source/space name.txt'",
                               'guard && test ! -e v1.tar && test ! -L v1.tar && timeout -k 1s 10s tar -cf '
                               'v1.tar -C source -- note.txt \'space name.txt\' && test "$(stat -c %s '
                               'v1.tar)" -le 65536',
                               'guard && timeout -k 1s 10s tar -tf v1.tar && timeout -k 1s 10s tar -tvf '
                               'v1.tar'],
 'real-linux-backup-checksum': ['w=/home/learner/ll-backup-3; test "$(id -un)" = learner && test ! -e "$w" '
                                '&& test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && test "$(df -Pk '
                                '. | awk \'NR==2 {print $4}\')" -ge 65536',
                                'guard() { test "$(pwd -P)" = /home/learner/ll-backup-3 && test ! -L '
                                '/home/learner/ll-backup-3 && test "$(stat -c %U .)" = learner && test -z '
                                '"$(find . -type l -print -quit)"; }; guard',
                                "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                                "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 source/note.txt "
                                "&& chmod 0600 'source/space name.txt' && touch -d '2026-01-01 00:00:00 UTC' "
                                "source/note.txt 'source/space name.txt'",
                                'guard && test ! -e v1.tar && test ! -L v1.tar && timeout -k 1s 10s tar -cf '
                                'v1.tar -C source -- note.txt \'space name.txt\' && test "$(stat -c %s '
                                'v1.tar)" -le 65536',
                                'guard && test ! -e v1.tar.gz && test ! -L v1.tar.gz && timeout -k 1s 10s '
                                'gzip -c -- v1.tar > v1.tar.gz && test "$(stat -c %s v1.tar.gz)" -le 65536 '
                                '&& sha256sum -- v1.tar.gz > expected-backup.sha256',
                                'guard && timeout -k 1s 10s gzip -t -- v1.tar.gz && sha256sum -c -- '
                                'expected-backup.sha256'],
 'real-linux-backup-damage': ['w=/home/learner/ll-backup-4; test "$(id -un)" = learner && test ! -e "$w" && '
                              'test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && test "$(df -Pk . | '
                              'awk \'NR==2 {print $4}\')" -ge 65536',
                              'guard() { test "$(pwd -P)" = /home/learner/ll-backup-4 && test ! -L '
                              '/home/learner/ll-backup-4 && test "$(stat -c %U .)" = learner && test -z '
                              '"$(find . -type l -print -quit)"; }; guard',
                              "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                              "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 source/note.txt && "
                              "chmod 0600 'source/space name.txt' && touch -d '2026-01-01 00:00:00 UTC' "
                              "source/note.txt 'source/space name.txt'",
                              'guard && test ! -e v1.tar && test ! -L v1.tar && timeout -k 1s 10s tar -cf '
                              'v1.tar -C source -- note.txt \'space name.txt\' && test "$(stat -c %s '
                              'v1.tar)" -le 65536',
                              'guard && sha256sum -- v1.tar > expected-backup.sha256 && cp -- v1.tar '
                              'altered.tar && printf X | dd of=altered.tar bs=1 seek=512 conv=notrunc '
                              'status=none',
                              'guard && timeout -k 1s 10s tar -tf altered.tar && timeout -k 1s 10s gzip -c '
                              '-- altered.tar > altered.tar.gz && timeout -k 1s 10s gzip -t -- '
                              'altered.tar.gz; sha256sum -- v1.tar altered.tar',
                              'guard && cp -- altered.tar.gz truncated.gz && truncate -s -4 truncated.gz; '
                              'timeout -k 1s 10s gzip -t -- truncated.gz; printf \'gzip status=%s\\n\' "$?"',
                              'guard && mkdir -m 0700 restore && timeout -k 1s 10s tar -xf altered.tar -C '
                              'restore --no-same-owner --same-permissions; cmp -- source/note.txt '
                              'restore/note.txt; printf \'comparison status=%s\\n\' "$?"; sha256sum -c -- '
                              'expected-backup.sha256'],
 'real-linux-backup-restore': ['w=/home/learner/ll-backup-5; test "$(id -un)" = learner && test ! -e "$w" && '
                               'test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && test "$(df -Pk . | '
                               'awk \'NR==2 {print $4}\')" -ge 65536',
                               'guard() { test "$(pwd -P)" = /home/learner/ll-backup-5 && test ! -L '
                               '/home/learner/ll-backup-5 && test "$(stat -c %U .)" = learner && test -z '
                               '"$(find . -type l -print -quit)"; }; guard',
                               "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                               "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 source/note.txt && "
                               "chmod 0600 'source/space name.txt' && touch -d '2026-01-01 00:00:00 UTC' "
                               "source/note.txt 'source/space name.txt'",
                               'guard && test ! -e v1.tar && test ! -L v1.tar && timeout -k 1s 10s tar -cf '
                               'v1.tar -C source -- note.txt \'space name.txt\' && test "$(stat -c %s '
                               'v1.tar)" -le 65536',
                               'guard && test ! -e restore && test ! -L restore && mkdir -m 0700 restore && '
                               'timeout -k 1s 10s tar -xf v1.tar -C restore --no-same-owner '
                               '--same-permissions',
                               "guard && cmp -- source/note.txt restore/note.txt && cmp -- 'source/space "
                               "name.txt' 'restore/space name.txt' && stat -c '%n %U:%G %a %Y %s' "
                               "source/note.txt restore/note.txt 'source/space name.txt' 'restore/space "
                               "name.txt'",
                               'guard && timeout -k 1s 10s tar -cf incomplete.tar -C source -- note.txt && '
                               'mkdir -m 0700 incomplete && timeout -k 1s 10s tar -xf incomplete.tar -C '
                               "incomplete --no-same-owner --same-permissions; test -f 'incomplete/space "
                               'name.txt\'; printf \'required member status=%s\\n\' "$?"'],
 'real-linux-backup-access': ['w=/home/learner/ll-backup-6; test "$(id -un)" = learner && test ! -e "$w" && '
                              'test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && saved_umask=$(umask) '
                              '&& umask 077 && test "$(df -Pk . | awk \'NR==2 {print $4}\')" -ge 65536',
                              'guard() { test "$(pwd -P)" = /home/learner/ll-backup-6 && test ! -L '
                              '/home/learner/ll-backup-6 && test "$(stat -c %U .)" = learner && test -z '
                              '"$(find . -type l -print -quit)"; }; guard',
                              "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                              "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 source/note.txt && "
                              "chmod 0600 'source/space name.txt' && touch -d '2026-01-01 00:00:00 UTC' "
                              "source/note.txt 'source/space name.txt'",
                              'guard && ! getent passwd ll-b6 && ! getent group ll-b6 && sudo useradd -M -U '
                              '-s /usr/sbin/nologin ll-b6 && sudo passwd -S ll-b6',
                              'guard && test ! -e v1.tar && test ! -L v1.tar && chmod 0711 . source && sudo '
                              'chown ll-b6:ll-b6 source/note.txt && sudo chmod 0600 source/note.txt && sudo '
                              'timeout -k 1s 10s tar -cf v1.tar -C source -- note.txt && sudo chown '
                              'learner:learner v1.tar && sudo chmod 0600 v1.tar && mkdir -m 0711 restore && '
                              'timeout -k 1s 10s tar -xf v1.tar -C restore --no-same-owner '
                              '--same-permissions',
                              "guard && sudo runuser -u ll-b6 -- cat restore/note.txt; printf 'wrong owner "
                              'status=%s\\n\' "$?"; stat -c \'%U:%G %a\' restore/note.txt',
                              'guard && sudo chown ll-b6:ll-b6 restore/note.txt && sudo chmod 0600 '
                              'restore/note.txt && sudo runuser -u ll-b6 -- cat restore/note.txt; cat '
                              'restore/note.txt; printf \'learner status=%s\\n\' "$?"; sudo cmp -- '
                              'source/note.txt restore/note.txt'],
 'real-linux-backup-versions': ['w=/home/learner/ll-backup-7; test "$(id -un)" = learner && test ! -e "$w" '
                                '&& test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && test "$(df -Pk '
                                '. | awk \'NR==2 {print $4}\')" -ge 65536',
                                'guard() { test "$(pwd -P)" = /home/learner/ll-backup-7 && test ! -L '
                                '/home/learner/ll-backup-7 && test "$(stat -c %U .)" = learner && test -z '
                                '"$(find . -type l -print -quit)"; }; guard',
                                "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                                "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 source/note.txt "
                                "&& chmod 0600 'source/space name.txt' && touch -d '2026-01-01 00:00:00 UTC' "
                                "source/note.txt 'source/space name.txt'",
                                'guard && test ! -e v1.tar && test ! -L v1.tar && timeout -k 1s 10s tar -cf '
                                'v1.tar -C source -- note.txt \'space name.txt\' && test "$(stat -c %s '
                                'v1.tar)" -le 65536',
                                'guard && test ! -e v2.tar && test ! -L v2.tar && test ! -e versions.sha256 '
                                "&& test ! -L versions.sha256 && printf 'alpha-v2\\n' > source/note.txt && "
                                "timeout -k 1s 10s tar -cf v2.tar -C source -- note.txt 'space name.txt' && "
                                'sha256sum -- v1.tar v2.tar > versions.sha256',
                                'guard && mkdir -m 0700 wrong restore && timeout -k 1s 10s tar -xf v2.tar -C '
                                "wrong --no-same-owner --same-permissions && printf 'alpha\\n' | cmp - "
                                'wrong/note.txt; printf \'wrong version status=%s\\n\' "$?"',
                                'guard && timeout -k 1s 10s tar -xf v1.tar -C restore --no-same-owner '
                                "--same-permissions && printf 'alpha\\n' | cmp - restore/note.txt && printf "
                                "'alpha-v2\\n' | cmp - source/note.txt && sha256sum -c -- versions.sha256"],
 'real-linux-backup-assessment': ['w=/home/learner/ll-backup-8; test "$(id -un)" = learner && test ! -e "$w" '
                                  '&& test ! -L "$w" && mkdir -m 0700 -- "$w" && cd -- "$w" && '
                                  'saved_umask=$(umask) && umask 077 && test "$(df -Pk . | awk \'NR==2 '
                                  '{print $4}\')" -ge 65536',
                                  'guard() { test "$(pwd -P)" = /home/learner/ll-backup-8 && test ! -L '
                                  '/home/learner/ll-backup-8 && test "$(stat -c %U .)" = learner && test -z '
                                  '"$(find . -type l -print -quit)"; }; guard',
                                  "guard && mkdir -m 0700 source && printf 'alpha\\n' > source/note.txt && "
                                  "printf 'bravo\\n' > 'source/space name.txt' && chmod 0640 source/note.txt "
                                  "&& chmod 0600 'source/space name.txt' && touch -d '2026-01-01 00:00:00 "
                                  "UTC' source/note.txt 'source/space name.txt'",
                                  'guard && ! getent passwd ll-b8 && ! getent group ll-b8 && sudo useradd -M '
                                  '-U -s /usr/sbin/nologin ll-b8 && sudo passwd -S ll-b8',
                                  'guard && test ! -e v1.tar && test ! -L v1.tar && test ! -e v2.tar && test '
                                  '! -L v2.tar && test ! -e versions.sha256 && test ! -L versions.sha256 && '
                                  'chmod 0711 . && chmod 0600 source/note.txt && timeout -k 1s 10s tar -cf '
                                  "v1.tar -C source -- note.txt && printf 'alpha-v2\\n' > source/note.txt && "
                                  'timeout -k 1s 10s tar -cf v2.tar -C source -- note.txt && sha256sum -- '
                                  'v1.tar v2.tar > versions.sha256',
                                  'guard && mkdir -m 0711 restore && timeout -k 1s 10s tar -xf v1.tar -C '
                                  'restore --no-same-owner --same-permissions && sudo chown ll-b8:ll-b8 '
                                  'restore/note.txt && sudo chmod 0600 restore/note.txt',
                                  'guard && sudo runuser -u ll-b8 -- cat restore/note.txt && sudo runuser -u '
                                  "ll-b8 -- stat -c '%U:%G %a %Y' restore/note.txt && printf 'alpha\\n' | "
                                  "sudo cmp - restore/note.txt && printf 'alpha-v2\\n' | cmp - "
                                  'source/note.txt && sha256sum -c -- versions.sha256; cat restore/note.txt; '
                                  'printf \'wrong identity status=%s\\n\' "$?"',
                                  "guard && printf '%s\\n' 'POINT: v1; current v2 preserved' 'EVIDENCE: "
                                  "contents, owner/group/mode/mtime, actual user read' 'TRUST: local "
                                  "retained checksum, not signature' 'LIMIT: no ACLs or untrusted archive "
                                  "guarantees' 'CLEANUP: exact practice paths/account only after review' > "
                                  'handover.txt']}
