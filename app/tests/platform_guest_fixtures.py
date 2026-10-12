"""Reviewed STATIC developer fixtures; not packaged/imported."""
DATA = [{'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-inventory',
              'content_version': '1.0.0',
              'title': 'Identify RPM package state and file providers',
              'goal': 'Query installed NEVRA, architecture, ownership and package/source/license '
                      'fields; distinguish RPM from its dependency frontend.',
              'challenge': 'Find the installed provider of /usr/bin/sh and record its installed '
                           'name/version/release/architecture, source/license metadata and one '
                           'listed installed path. Distinguish this provider from ownership of the '
                           'retained ll-rpm-data-1.0-1.noarch.rpm archive file. Do not install '
                           'anything; retain factual output and unchanged package state.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-inventory.XXXXXX") && cd "$w" && '
                                    'umask 077; here() { case "$w" in '
                                    '"$HOME"/rpm-inventory.??????) ;; *) return 19;; esac; test '
                                    '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                                    '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && '
                                    'test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here '
                                    '|| return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test '
                                    '! -L "$1"; }; cfg() { case "$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'here && fresh "$w/metadata.txt" && fresh "$w/files.txt" && '
                                    'timeout -k 1s 20s rpm --version && timeout -k 1s 20s dnf '
                                    '--version && rpm -q bash rpm dnf && rpm -qf /usr/bin/sh && '
                                    'rpm -qi bash > metadata.txt && rpm -ql bash > files.txt && '
                                    'head -n 12 metadata.txt && head -n 12 files.txt',
                         'explanation': 'Query actual installed metadata. Complete output stays '
                                        'private; only a short excerpt is displayed.',
                         'expected': 'Native versions, installed NEVRA and bash as /usr/bin/sh '
                                     'provider.'},
                        {'command': 'rpm_step() { here || return 19; fresh "$w/archive-owner.txt" '
                                    '|| return 19; if rpm -qf "$f/ll-rpm-data-1.0-1.noarch.rpm" > '
                                    'archive-owner.txt 2>&1; then return 1; else rc=$?; test "$rc" '
                                    '= 1 && grep -F "is not owned by any package" '
                                    'archive-owner.txt; fi; }; rpm_step',
                         'explanation': 'A retained archive is not an installed package. Require '
                                        'the actual specific failure, not any nonzero status.',
                         'expected': 'Archive unowned; installed fixtures still absent.'}],
              'hints': ['Missing package differs from unowned file; DNF-compatible yum does not '
                        'demonstrate legacy YUM; Zypper is absent.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5 102.5 installed '
                          'metadata/file-provider; DNF awareness. DNF4 awareness, not original '
                          'YUM, DNF5 or Zypper proficiency. No complete-objective or LPI '
                          'endorsement claim.'},
  'entry': {'id': 'real-linux-rpm-inventory',
            'resource': 'real-linux-rpm-inventory.json',
            'description': 'Query installed NEVRA, architecture, ownership and '
                           'package/source/license fields; distinguish RPM from its dependency '
                           'frontend.',
            'objectives': ['102.5 installed metadata/file-provider; DNF awareness'],
            'troubleshooting': ['Missing package differs from unowned file; DNF-compatible yum '
                                'does not demonstrate legacy YUM; Zypper is absent.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-inventory.XXXXXX") && cd "$w" && umask 077; here() { case '
                          '"$w" in "$HOME"/rpm-inventory.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here || return 19; test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                          '"$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Challenge starting fixture: Fixture packages absent; use only the '
                          'protected archives and read-only queries. Do not execute transactions '
                          'for inventory/archive/dependencies.',
                          'Challenge outcome: Find the installed provider of /usr/bin/sh and '
                          'record its installed name/version/release/architecture, source/license '
                          'metadata and one listed installed path. Distinguish this provider from '
                          'ownership of the retained ll-rpm-data-1.0-1.noarch.rpm archive file. Do '
                          'not install anything; retain factual output and unchanged package '
                          'state. Expected data 2.0 SHA-256 when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['Actual tool versions, NEVRA, file ownership/provider and metadata; '
                             'unrelated package list unchanged.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          'Missing package differs from unowned file; DNF-compatible yum does not '
                          'demonstrate legacy YUM; Zypper is absent.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': '00cd4983c9e13911fd686794b516b4688af2b9446a70feeeb4b048546ec7644f',
  'entry_sha256': 'da7bc7937cb720f6189cfdfd82b8230454dd4ae83c1fbb7490071cf010f59a43',
  'learn': ['w=$(mktemp -d "$HOME/rpm-inventory.XXXXXX") && cd "$w" && umask 077; here() { case '
            '"$w" in "$HOME"/rpm-inventory.??????) ;; *) return 19;; esac; test "${w%/*}" = '
            '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
            'test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
            'here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'cfg() { case "$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'here && fresh "$w/metadata.txt" && fresh "$w/files.txt" && timeout -k 1s 20s rpm '
            '--version && timeout -k 1s 20s dnf --version && rpm -q bash rpm dnf && rpm -qf '
            '/usr/bin/sh && rpm -qi bash > metadata.txt && rpm -ql bash > files.txt && head -n 12 '
            'metadata.txt && head -n 12 files.txt',
            'rpm_step() { here || return 19; fresh "$w/archive-owner.txt" || return 19; if rpm -qf '
            '"$f/ll-rpm-data-1.0-1.noarch.rpm" > archive-owner.txt 2>&1; then return 1; else '
            'rc=$?; test "$rc" = 1 && grep -F "is not owned by any package" archive-owner.txt; fi; '
            '}; rpm_step'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-inventory.XXXXXX") && cd "$w" && umask 077; here() { '
                'case "$w" in "$HOME"/rpm-inventory.??????) ;; *) return 19;; esac; test "${w%/*}" '
                '= "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" '
                '&& test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                'fresh() { here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L '
                '"$1"; }; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'here && fresh "$w/metadata.txt" && fresh "$w/files.txt" && timeout -k 1s 20s rpm '
                '--version && timeout -k 1s 20s dnf --version && rpm -q bash rpm dnf && rpm -qf '
                '/usr/bin/sh && rpm -qi bash > metadata.txt && rpm -ql bash > files.txt && head -n '
                '12 metadata.txt && head -n 12 files.txt',
                'rpm_step() { here || return 19; fresh "$w/archive-owner.txt" || return 19; if rpm '
                '-qf "$f/ll-rpm-data-1.0-1.noarch.rpm" > archive-owner.txt 2>&1; then return 1; '
                'else rc=$?; test "$rc" = 1 && grep -F "is not owned by any package" '
                'archive-owner.txt; fi; }; rpm_step'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-archive',
              'content_version': '1.0.0',
              'title': 'Inspect an offline RPM before admitting it',
              'goal': 'Inspect trusted uninstalled RPM metadata, dependencies, payload modes and '
                      'digests; distinguish internal integrity from publisher authenticity.',
              'challenge': 'Inspect the three protected unsigned RPM archives, record their exact '
                           'hashes, declared files/modes/owners, requirements and absence of '
                           'scripts/triggers. Reject the supplied truncated private copy without '
                           'installing it. Explain internal digest checking versus publisher '
                           'authenticity; do not claim verified signatures or rpm2cpio practice.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-archive.XXXXXX") && cd "$w" && umask '
                                    '077; here() { case "$w" in "$HOME"/rpm-archive.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                                    'learner:700; }; fresh() { here || return 19; test "${1%/*}" = '
                                    '"$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                                    '"$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'here && fresh "$w/archive-hashes.txt" && fresh '
                                    '"$w/metadata.txt" && fresh "$w/files.txt" && fresh '
                                    '"$w/requires.txt" && sha256sum "$f"/*.rpm > '
                                    'archive-hashes.txt && rpm -qpi '
                                    '"$f/ll-rpm-report-1.0-1.noarch.rpm" > metadata.txt && rpm '
                                    '-qpl "$f/ll-rpm-report-1.0-1.noarch.rpm" > files.txt && rpm '
                                    '-qpR "$f/ll-rpm-report-1.0-1.noarch.rpm" > requires.txt && '
                                    'cat archive-hashes.txt metadata.txt files.txt requires.txt',
                         'explanation': 'Inspect only the three reviewed teaching archives. '
                                        'Compare whole-file hashes with the retained fixture '
                                        'manifest, not an arbitrary download. Source/specs are '
                                        'protected from ordinary users, not guest root.',
                         'expected': 'Exact report dependency on data 2.0-1 and /usr/bin/sh; two '
                                     'declared ordinary files.'},
                        {'command': 'here && fresh "$w/scripts.txt" && fresh "$w/triggers.txt" && '
                                    'rpm -qp --scripts "$f/ll-rpm-report-1.0-1.noarch.rpm" > '
                                    'scripts.txt && rpm -qp --triggers '
                                    '"$f/ll-rpm-report-1.0-1.noarch.rpm" > triggers.txt && test ! '
                                    '-s scripts.txt && test ! -s triggers.txt && rpm -qp --qf '
                                    '"[%{FILENAMES} %{FILEMODES:perms} '
                                    '%{FILEUSERNAME}:%{FILEGROUPNAME}\\n]" '
                                    '"$f/ll-rpm-report-1.0-1.noarch.rpm"',
                         'explanation': 'Read-only metadata inspection complements the retained '
                                        'build admission. Do not extract unknown RPMs or claim '
                                        'these queries safely sandbox arbitrary packages.',
                         'expected': 'Root-owned 0755 report script and 0644 license; no scripts '
                                     'or triggers.'},
                        {'command': 'rpm_step() { here || return 19; fresh "$w/signature.txt" || '
                                    'return 19; if rpm -K "$f/ll-rpm-report-1.0-1.noarch.rpm" > '
                                    'signature.txt 2>&1; then cat signature.txt && grep -F '
                                    '"digests OK" signature.txt; else return 1; fi; }; rpm_step',
                         'explanation': 'The original project archive is intentionally unsigned. '
                                        'Digest validity detects internal damage, not publisher '
                                        'authenticity; official vendor authentication was '
                                        'performed in preparation, not this lesson.',
                         'expected': 'Digest check succeeds; no signature-authentication claim.'},
                        {'command': 'rpm_step() { here && fresh "$w/truncated-report.rpm" && fresh '
                                    '"$w/rejected.txt" && head -c 64 '
                                    '"$f/ll-rpm-report-1.0-1.noarch.rpm" > truncated-report.rpm || '
                                    'return 19; if rpm -K truncated-report.rpm > rejected.txt '
                                    '2>&1; then return 1; else test $? -ne 0 && test -s '
                                    'rejected.txt && test "$(stat -c %s truncated-report.rpm)" = '
                                    '64; fi; }; rpm_step',
                         'explanation': 'Retain and reject a deliberately truncated private copy '
                                        'using read-only inspection. Never install it. A failed '
                                        'check detects this damage, not authenticity of the '
                                        'unsigned original.',
                         'expected': 'Rejected 64-byte private candidate; protected original '
                                     'unchanged.'}],
              'hints': ['Unsigned local fixture is not authenticated; rpm digest verification is '
                        'not publisher trust; no scripts, links or unsafe extraction.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5: uninstalled metadata, contents, '
                          'requirements and digest inspection. Signature trust explained only; no '
                          'rpm2cpio extraction, repository, YUM or Zypper practice. Self-reviewed, '
                          'not automatic assessment.'},
  'entry': {'id': 'real-linux-rpm-archive',
            'resource': 'real-linux-rpm-archive.json',
            'description': 'Inspect trusted uninstalled RPM metadata, dependencies, payload modes '
                           'and digests; distinguish internal integrity from publisher '
                           'authenticity.',
            'objectives': ['102.5 uninstalled contents/dependencies/digests; signature distinction '
                           'conceptual, no rpm2cpio practice claim'],
            'troubleshooting': ['Unsigned local fixture is not authenticated; rpm digest '
                                'verification is not publisher trust; no scripts, links or unsafe '
                                'extraction.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-archive.XXXXXX") && cd "$w" && umask 077; here() { case "$w" '
                          'in "$HOME"/rpm-archive.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                          '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" '
                          '= "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                          'learner:700; }; fresh() { here || return 19; test "${1%/*}" = "$w" && '
                          'test ! -e "$1" && test ! -L "$1"; }; cfg() { case "$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Challenge starting fault, after fresh workspace setup: rpm_step() { '
                          'here && fresh "$w/truncated-report.rpm" && fresh "$w/rejected.txt" && '
                          'head -c 64 "$f/ll-rpm-report-1.0-1.noarch.rpm" > truncated-report.rpm '
                          '|| return 19; if rpm -K truncated-report.rpm > rejected.txt 2>&1; then '
                          'return 1; else test $? -ne 0 && test -s rejected.txt && test "$(stat -c '
                          '%s truncated-report.rpm)" = 64; fi; }; rpm_step',
                          'Challenge outcome: Inspect the three protected unsigned RPM archives, '
                          'record their exact hashes, declared files/modes/owners, requirements '
                          'and absence of scripts/triggers. Reject the supplied truncated private '
                          'copy without installing it. Explain internal digest checking versus '
                          'publisher authenticity; do not claim verified signatures or rpm2cpio '
                          'practice. Expected data 2.0 SHA-256 when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['Inspected payload paths/modes/owners, absence of '
                             'scripts/triggers/services/accounts/privileged bits, hashes and '
                             'signature result.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          'Unsigned local fixture is not authenticated; rpm digest verification is '
                          'not publisher trust; no scripts, links or unsafe extraction.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': 'fcf222c2b050d431b2c1c0f8cb1d3c3e4c335d1d6b2853db88d699690426406a',
  'entry_sha256': 'a5f3b21b34b8004a47fef918ece3c936a9d83bc9bb2366573aa7edee184c24c1',
  'learn': ['w=$(mktemp -d "$HOME/rpm-archive.XXXXXX") && cd "$w" && umask 077; here() { case "$w" '
            'in "$HOME"/rpm-archive.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" && '
            'test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd '
            '-P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here || '
            'return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
            '"$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'here && fresh "$w/archive-hashes.txt" && fresh "$w/metadata.txt" && fresh '
            '"$w/files.txt" && fresh "$w/requires.txt" && sha256sum "$f"/*.rpm > '
            'archive-hashes.txt && rpm -qpi "$f/ll-rpm-report-1.0-1.noarch.rpm" > metadata.txt && '
            'rpm -qpl "$f/ll-rpm-report-1.0-1.noarch.rpm" > files.txt && rpm -qpR '
            '"$f/ll-rpm-report-1.0-1.noarch.rpm" > requires.txt && cat archive-hashes.txt '
            'metadata.txt files.txt requires.txt',
            'here && fresh "$w/scripts.txt" && fresh "$w/triggers.txt" && rpm -qp --scripts '
            '"$f/ll-rpm-report-1.0-1.noarch.rpm" > scripts.txt && rpm -qp --triggers '
            '"$f/ll-rpm-report-1.0-1.noarch.rpm" > triggers.txt && test ! -s scripts.txt && test ! '
            '-s triggers.txt && rpm -qp --qf "[%{FILENAMES} %{FILEMODES:perms} '
            '%{FILEUSERNAME}:%{FILEGROUPNAME}\\n]" "$f/ll-rpm-report-1.0-1.noarch.rpm"',
            'rpm_step() { here || return 19; fresh "$w/signature.txt" || return 19; if rpm -K '
            '"$f/ll-rpm-report-1.0-1.noarch.rpm" > signature.txt 2>&1; then cat signature.txt && '
            'grep -F "digests OK" signature.txt; else return 1; fi; }; rpm_step',
            'rpm_step() { here && fresh "$w/truncated-report.rpm" && fresh "$w/rejected.txt" && '
            'head -c 64 "$f/ll-rpm-report-1.0-1.noarch.rpm" > truncated-report.rpm || return 19; '
            'if rpm -K truncated-report.rpm > rejected.txt 2>&1; then return 1; else test $? -ne 0 '
            '&& test -s rejected.txt && test "$(stat -c %s truncated-report.rpm)" = 64; fi; }; '
            'rpm_step'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-archive.XXXXXX") && cd "$w" && umask 077; here() { case '
                '"$w" in "$HOME"/rpm-archive.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
                'test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() '
                '{ here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; '
                '}; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'rpm_step() { here && fresh "$w/truncated-report.rpm" && fresh "$w/rejected.txt" '
                '&& head -c 64 "$f/ll-rpm-report-1.0-1.noarch.rpm" > truncated-report.rpm || '
                'return 19; if rpm -K truncated-report.rpm > rejected.txt 2>&1; then return 1; '
                'else test $? -ne 0 && test -s rejected.txt && test "$(stat -c %s '
                'truncated-report.rpm)" = 64; fi; }; rpm_step',
                'here && fresh "$w/archive-hashes.txt" && fresh "$w/metadata.txt" && fresh '
                '"$w/files.txt" && fresh "$w/requires.txt" && sha256sum "$f"/*.rpm > '
                'archive-hashes.txt && rpm -qpi "$f/ll-rpm-report-1.0-1.noarch.rpm" > metadata.txt '
                '&& rpm -qpl "$f/ll-rpm-report-1.0-1.noarch.rpm" > files.txt && rpm -qpR '
                '"$f/ll-rpm-report-1.0-1.noarch.rpm" > requires.txt && cat archive-hashes.txt '
                'metadata.txt files.txt requires.txt',
                'here && fresh "$w/scripts.txt" && fresh "$w/triggers.txt" && rpm -qp --scripts '
                '"$f/ll-rpm-report-1.0-1.noarch.rpm" > scripts.txt && rpm -qp --triggers '
                '"$f/ll-rpm-report-1.0-1.noarch.rpm" > triggers.txt && test ! -s scripts.txt && '
                'test ! -s triggers.txt && rpm -qp --qf "[%{FILENAMES} %{FILEMODES:perms} '
                '%{FILEUSERNAME}:%{FILEGROUPNAME}\\n]" "$f/ll-rpm-report-1.0-1.noarch.rpm"',
                'rpm_step() { here || return 19; fresh "$w/signature.txt" || return 19; if rpm -K '
                '"$f/ll-rpm-report-1.0-1.noarch.rpm" > signature.txt 2>&1; then cat signature.txt '
                '&& grep -F "digests OK" signature.txt; else return 1; fi; }; rpm_step'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-dependencies',
              'content_version': '1.0.0',
              'title': 'Observe a dependency failure without forcing installation',
              'goal': 'Demonstrate strict local rpm dependency checking and leave unrelated state '
                      'intact.',
              'challenge': 'With both fixtures absent, inspect report 1.0-1’s exact data '
                           'dependency; retain both the root-context --test refusal and actual '
                           'refused install using only the protected report archive. Preview, but '
                           'do not apply, the compatible pair. Compare final full package state; '
                           'never use force or nodeps.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-dependencies.XXXXXX") && cd "$w" && '
                                    'umask 077; here() { case "$w" in '
                                    '"$HOME"/rpm-dependencies.??????) ;; *) return 19;; esac; test '
                                    '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                                    '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && '
                                    'test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here '
                                    '|| return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test '
                                    '! -L "$1"; }; cfg() { case "$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'here && fresh "$w/requires.txt" && rpm -qpR '
                                    '"$f/ll-rpm-report-1.0-1.noarch.rpm" > requires.txt && cat '
                                    'requires.txt',
                         'explanation': 'Inspect the exact version requirement before a '
                                        'root-context transaction test.',
                         'expected': 'll-rpm-data = 2.0-1.'},
                        {'command': 'rpm_step() { here || return 19; fresh "$w/dependency.txt" || '
                                    'return 19; if timeout -k 1s 20s sudo rpm -i --test '
                                    '"$f/ll-rpm-report-1.0-1.noarch.rpm" > dependency.txt 2>&1; '
                                    'then return 1; else rc=$?; test "$rc" = 1 && grep -F '
                                    '"ll-rpm-data = 2.0-1 is needed" dependency.txt; fi; }; '
                                    'rpm_step',
                         'explanation': '--test reports an unsatisfied dependency without '
                                        'installation. This lesson does not apply raw rpm installs '
                                        'or use force/nodeps. An unrelated failure is not '
                                        'evidence.',
                         'expected': 'Specific dependency refusal; no package changes.'},
                        {'command': 'rpm_step() { here && fresh "$w/install-refused.txt" || return '
                                    '19; if timeout -k 1s 20s sudo rpm -i '
                                    '"$f/ll-rpm-report-1.0-1.noarch.rpm" > install-refused.txt '
                                    '2>&1; then return 1; else test $? = 1 && grep -F "ll-rpm-data '
                                    '= 2.0-1 is needed" install-refused.txt; fi; }; rpm_step',
                         'explanation': 'For this exact inspected script-free archive with both '
                                        'fixtures absent, observe actual installation refusal in '
                                        'the same sudo context as --test. Do not use force or '
                                        'nodeps. The final package comparison must still match.',
                         'expected': 'Actual dependency refusal, not merely a simulated plan; no '
                                     'applied fixture.'},
                        {'command': 'here && fresh "$w/plan.txt" && sudo "$h" preview pair > '
                                    'plan.txt && cat plan.txt',
                         'explanation': 'Resolve both explicit archives through the fixed '
                                        'frontend; this previews without applying.',
                         'expected': 'Only data 2.0-1 and report 1.0-1.'}],
              'hints': ['--nodeps hides the issue; matching a name is not matching required '
                        'version/architecture.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5 102.5 RPM install/dependencies. DNF4 '
                          'awareness, not original YUM, DNF5 or Zypper proficiency. No '
                          'complete-objective or LPI endorsement claim.'},
  'entry': {'id': 'real-linux-rpm-dependencies',
            'resource': 'real-linux-rpm-dependencies.json',
            'description': 'Demonstrate strict local rpm dependency checking and leave unrelated '
                           'state intact.',
            'objectives': ['102.5 RPM install/dependencies'],
            'troubleshooting': ['--nodeps hides the issue; matching a name is not matching '
                                'required version/architecture.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-dependencies.XXXXXX") && cd "$w" && umask 077; here() { case '
                          '"$w" in "$HOME"/rpm-dependencies.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here || return 19; test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                          '"$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Challenge starting fixture: Fixture packages absent; use only the '
                          'protected archives and read-only queries. Do not execute transactions '
                          'for inventory/archive/dependencies.',
                          'Challenge outcome: With both fixtures absent, inspect report 1.0-1’s '
                          'exact data dependency; retain both the root-context --test refusal and '
                          'actual refused install using only the protected report archive. '
                          'Preview, but do not apply, the compatible pair. Compare final full '
                          'package state; never use force or nodeps. Expected data 2.0 SHA-256 '
                          'when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['Solver/transaction errors, unchanged full unrelated RPM inventory '
                             'and fixture state, exact required version.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          '--nodeps hides the issue; matching a name is not matching required '
                          'version/architecture.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': '5e7f59cd2645f4bb823060c66a2dafe826ea5e5ed47a0ad12c6cf18cb19629f0',
  'entry_sha256': '42b1210f196158e2529d295286d40d9c215ca43cb5bbec7e2f2d23f7e43b0bb5',
  'learn': ['w=$(mktemp -d "$HOME/rpm-dependencies.XXXXXX") && cd "$w" && umask 077; here() { case '
            '"$w" in "$HOME"/rpm-dependencies.??????) ;; *) return 19;; esac; test "${w%/*}" = '
            '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
            'test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
            'here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'cfg() { case "$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'here && fresh "$w/requires.txt" && rpm -qpR "$f/ll-rpm-report-1.0-1.noarch.rpm" > '
            'requires.txt && cat requires.txt',
            'rpm_step() { here || return 19; fresh "$w/dependency.txt" || return 19; if timeout -k '
            '1s 20s sudo rpm -i --test "$f/ll-rpm-report-1.0-1.noarch.rpm" > dependency.txt 2>&1; '
            'then return 1; else rc=$?; test "$rc" = 1 && grep -F "ll-rpm-data = 2.0-1 is needed" '
            'dependency.txt; fi; }; rpm_step',
            'rpm_step() { here && fresh "$w/install-refused.txt" || return 19; if timeout -k 1s '
            '20s sudo rpm -i "$f/ll-rpm-report-1.0-1.noarch.rpm" > install-refused.txt 2>&1; then '
            'return 1; else test $? = 1 && grep -F "ll-rpm-data = 2.0-1 is needed" '
            'install-refused.txt; fi; }; rpm_step',
            'here && fresh "$w/plan.txt" && sudo "$h" preview pair > plan.txt && cat plan.txt'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-dependencies.XXXXXX") && cd "$w" && umask 077; here() { '
                'case "$w" in "$HOME"/rpm-dependencies.??????) ;; *) return 19;; esac; test '
                '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e '
                '"$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                'learner:700; }; fresh() { here || return 19; test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'here && fresh "$w/requires.txt" && rpm -qpR "$f/ll-rpm-report-1.0-1.noarch.rpm" > '
                'requires.txt && cat requires.txt',
                'rpm_step() { here || return 19; fresh "$w/dependency.txt" || return 19; if '
                'timeout -k 1s 20s sudo rpm -i --test "$f/ll-rpm-report-1.0-1.noarch.rpm" > '
                'dependency.txt 2>&1; then return 1; else rc=$?; test "$rc" = 1 && grep -F '
                '"ll-rpm-data = 2.0-1 is needed" dependency.txt; fi; }; rpm_step',
                'rpm_step() { here && fresh "$w/install-refused.txt" || return 19; if timeout -k '
                '1s 20s sudo rpm -i "$f/ll-rpm-report-1.0-1.noarch.rpm" > install-refused.txt '
                '2>&1; then return 1; else test $? = 1 && grep -F "ll-rpm-data = 2.0-1 is needed" '
                'install-refused.txt; fi; }; rpm_step',
                'here && fresh "$w/plan.txt" && sudo "$h" preview pair > plan.txt && cat plan.txt'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-dnf-transaction',
              'content_version': '1.0.0',
              'title': 'Resolve the offline fixture dependency explicitly',
              'goal': 'Install only the two approved fixture identities using explicit local files '
                      'and a checked DNF plan.',
              'challenge': 'Reject the named unsupported helper operation unapproved and retain '
                           'its specific refusal. Review and apply only the compatible pair from '
                           'the fixed helper; verify actual installed identities/versions and the '
                           'exact unprivileged report. Compare unrelated package state and perform '
                           'exact cleanup. This is not arbitrary DNF solver or repository '
                           'practice.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-dnf-transaction.XXXXXX") && cd "$w" '
                                    '&& umask 077; here() { case "$w" in '
                                    '"$HOME"/rpm-dnf-transaction.??????) ;; *) return 19;; esac; '
                                    'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                                    'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
                                    'here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && '
                                    'test ! -L "$1"; }; cfg() { case "$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'rpm_step() { here && fresh "$w/unapproved-operation.txt" || '
                                    'return 19; if sudo "$h" preview unapproved > '
                                    'unapproved-operation.txt 2>&1; then return 1; else test $? = '
                                    '1 && grep -F "Supported operations:" '
                                    'unapproved-operation.txt; fi; }; rpm_step',
                         'explanation': 'The helper rejects an unsupported operation before '
                                        'application. This is not the developer-only resolved '
                                        'foreign-package test.',
                         'expected': 'Explicit operation refusal, unchanged fixture state.'},
                        {'command': 'here && sudo "$h" preview pair',
                         'explanation': 'Inspect names, versions, architectures and actions. File '
                                        'names and --no-download alone do not bound solver '
                                        'effects.',
                         'expected': 'Exactly the two declared installations.'},
                        {'command': 'here && sudo "$h" apply pair',
                         'explanation': 'Type APPLY only after reviewing the displayed plan; '
                                        'another answer cancels. One DNF transaction object is '
                                        'validated and applied.',
                         'expected': 'Exact pair installed without unrelated changes or '
                                     'downloads.'},
                        {'command': 'here && fresh "$w/report.txt" && fresh '
                                    '"$w/expected-report.txt" && rpm -q ll-rpm-data ll-rpm-report '
                                    '&& /usr/bin/ll-rpm-report > report.txt && printf "%s\\n" '
                                    '"Learning Lab package report" header=inventory-2.0 "Learning '
                                    'Lab offline inventory" fixture_data_version=2.0 items=3 > '
                                    'expected-report.txt && cmp expected-report.txt report.txt && '
                                    'test "$(stat -c %U:%G:%a:%h '
                                    '/usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && '
                                    'cat report.txt',
                         'explanation': 'Verify actual unprivileged execution, full expected bytes '
                                        'and payload ownership. A solver exit status is '
                                        'insufficient.',
                         'expected': 'Data 2.0/report 1.0, exactly the expected report readable by '
                                     'learner.'}],
              'hints': ['No-download/repo disabling alone is not a boundary; unprivileged preview '
                        'need not match privileged execution.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5 102.5 DNF awareness/dependency '
                          'frontend; modern YUM compatibility limitation. DNF4 awareness, not '
                          'original YUM, DNF5 or Zypper proficiency. No complete-objective or LPI '
                          'endorsement claim.'},
  'entry': {'id': 'real-linux-rpm-dnf-transaction',
            'resource': 'real-linux-rpm-dnf-transaction.json',
            'description': 'Install only the two approved fixture identities using explicit local '
                           'files and a checked DNF plan.',
            'objectives': ['102.5 DNF awareness/dependency frontend; modern YUM compatibility '
                           'limitation'],
            'troubleshooting': ['No-download/repo disabling alone is not a boundary; unprivileged '
                                'preview need not match privileged execution.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-dnf-transaction.XXXXXX") && cd "$w" && umask 077; here() { '
                          'case "$w" in "$HOME"/rpm-dnf-transaction.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here || return 19; '
                          'test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { '
                          'case "$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Starting condition: both fixtures absent. Negative operation: '
                          'unapproved. Required pair: ll-rpm-data 2.0-1.noarch and ll-rpm-report '
                          '1.0-1.noarch. Required header=inventory-2.0.',
                          'Challenge outcome: Reject the named unsupported helper operation '
                          'unapproved and retain its specific refusal. Review and apply only the '
                          'compatible pair from the fixed helper; verify actual installed '
                          'identities/versions and the exact unprivileged report. Compare '
                          'unrelated package state and perform exact cleanup. This is not '
                          'arbitrary DNF solver or repository practice. Expected data 2.0 SHA-256 '
                          'when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['Exact versions/actions, plan refusal, execution status, expected '
                             'files and before/after all nonfixture packages and policy.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          'No-download/repo disabling alone is not a boundary; unprivileged '
                          'preview need not match privileged execution.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': 'eec6d3a8dc4ac38b596ca43ca7fadad7075a816a41a83ed69b4d7fd8cd8daf6d',
  'entry_sha256': 'a9ef9692781ab158c680d7d4871c239c52a8ce1c4059c4fab748c82ac9894c83',
  'learn': ['w=$(mktemp -d "$HOME/rpm-dnf-transaction.XXXXXX") && cd "$w" && umask 077; here() { '
            'case "$w" in "$HOME"/rpm-dnf-transaction.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L '
            '"$1"; }; cfg() { case "$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'rpm_step() { here && fresh "$w/unapproved-operation.txt" || return 19; if sudo "$h" '
            'preview unapproved > unapproved-operation.txt 2>&1; then return 1; else test $? = 1 '
            '&& grep -F "Supported operations:" unapproved-operation.txt; fi; }; rpm_step',
            'here && sudo "$h" preview pair',
            'here && printf \'APPLY\\n\' | sudo "$h" apply pair',
            'here && fresh "$w/report.txt" && fresh "$w/expected-report.txt" && rpm -q ll-rpm-data '
            'll-rpm-report && /usr/bin/ll-rpm-report > report.txt && printf "%s\\n" "Learning Lab '
            'package report" header=inventory-2.0 "Learning Lab offline inventory" '
            'fixture_data_version=2.0 items=3 > expected-report.txt && cmp expected-report.txt '
            'report.txt && test "$(stat -c %U:%G:%a:%h /usr/share/learning-lab-rpm/data.txt)" = '
            'root:root:644:1 && cat report.txt'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-dnf-transaction.XXXXXX") && cd "$w" && umask 077; here() '
                '{ case "$w" in "$HOME"/rpm-dnf-transaction.??????) ;; *) return 19;; esac; test '
                '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e '
                '"$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                'learner:700; }; fresh() { here || return 19; test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'rpm_step() { here && fresh "$w/unapproved-operation.txt" || return 19; if sudo '
                '"$h" preview unapproved > unapproved-operation.txt 2>&1; then return 1; else test '
                '$? = 1 && grep -F "Supported operations:" unapproved-operation.txt; fi; }; '
                'rpm_step',
                'here && sudo "$h" preview pair',
                'here && printf \'APPLY\\n\' | sudo "$h" apply pair',
                'here && fresh "$w/report.txt" && fresh "$w/expected-report.txt" && rpm -q '
                'll-rpm-data ll-rpm-report && /usr/bin/ll-rpm-report > report.txt && printf '
                '"%s\\n" "Learning Lab package report" header=inventory-2.0 "Learning Lab offline '
                'inventory" fixture_data_version=2.0 items=3 > expected-report.txt && cmp '
                'expected-report.txt report.txt && test "$(stat -c %U:%G:%a:%h '
                '/usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && cat report.txt'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-upgrade',
              'content_version': '1.0.0',
              'title': 'Retain edited configuration during an RPM upgrade',
              'goal': 'Practice %config(noreplace), installed version and actual .rpmnew/.rpmsave '
                      'behavior.',
              'challenge': 'Starting from data 1.0-1, preserve the original and set '
                           'header=owner-kept in only its declared configuration. Upgrade to data '
                           '2.0-1 without replacing that local value. Retain and inspect .rpmnew, '
                           'verify actual package contents/version and deliberate config '
                           'discrepancy, then clean up with candidates preserved first.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-upgrade.XXXXXX") && cd "$w" && umask '
                                    '077; here() { case "$w" in "$HOME"/rpm-upgrade.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                                    'learner:700; }; fresh() { here || return 19; test "${1%/*}" = '
                                    '"$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                                    '"$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'here && sudo "$h" preview data1 && sudo "$h" apply data1',
                         'explanation': 'Confirm initial data 1.0 installation.',
                         'expected': 'Only data 1.0-1 installed.'},
                        {'command': 'here && keepcfg /etc/learning-lab-rpm/report.conf '
                                    'original.conf && cfg /etc/learning-lab-rpm/report.conf && '
                                    'printf "%s\\n" header=owner-kept | sudo tee '
                                    '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                                    '/etc/learning-lab-rpm/report.conf edited.conf && sudo "$h" '
                                    'preview upgrade',
                         'explanation': 'Preserve original before changing only this declared '
                                        'config. Guard its type, ownership, mode, links and '
                                        'parent.',
                         'expected': 'Preserved original and edit; exact upgrade plan.'},
                        {'command': 'here && sudo "$h" apply upgrade',
                         'explanation': 'Confirm the exact upgrade. %config(noreplace) behavior is '
                                        'package-specific, not universal RPM policy.',
                         'expected': 'Data 2.0; edit retained and a .rpmnew candidate.'},
                        {'command': 'rpm_step() { here || return 19; cfg '
                                    '/etc/learning-lab-rpm/report.conf && cmp edited.conf '
                                    '/etc/learning-lab-rpm/report.conf && keepcfg '
                                    '/etc/learning-lab-rpm/report.conf.rpmnew candidate.conf && '
                                    'grep -Fx header=inventory-2.0 candidate.conf && fresh '
                                    '"$w/verification.txt" || return 19; if rpm -V ll-rpm-data > '
                                    'verification.txt; then return 1; else rc=$?; test "$rc" = 1 '
                                    '&& grep -F /etc/learning-lab-rpm/report.conf '
                                    'verification.txt; fi; }; rpm_step',
                         'explanation': 'Retain and inspect old/edit/new versions. Verification '
                                        'should report the deliberate configuration difference; '
                                        'earlier guard failure must not be accepted as rpm '
                                        'evidence.',
                         'expected': 'Actual config discrepancy, independent copies and upgraded '
                                     'payload.'}],
              'hints': ['Do not assume Debian conffile semantics or silently overwrite user '
                        'content; skipped/different-version transactions are not upgrades.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5 102.5 upgrade/reinstall lifecycle. '
                          'DNF4 awareness, not original YUM, DNF5 or Zypper proficiency. No '
                          'complete-objective or LPI endorsement claim.'},
  'entry': {'id': 'real-linux-rpm-upgrade',
            'resource': 'real-linux-rpm-upgrade.json',
            'description': 'Practice %config(noreplace), installed version and actual '
                           '.rpmnew/.rpmsave behavior.',
            'objectives': ['102.5 upgrade/reinstall lifecycle'],
            'troubleshooting': ['Do not assume Debian conffile semantics or silently overwrite '
                                'user content; skipped/different-version transactions are not '
                                'upgrades.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-upgrade.XXXXXX") && cd "$w" && umask 077; here() { case "$w" '
                          'in "$HOME"/rpm-upgrade.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                          '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" '
                          '= "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                          'learner:700; }; fresh() { here || return 19; test "${1%/*}" = "$w" && '
                          'test ! -e "$1" && test ! -L "$1"; }; cfg() { case "$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Challenge initial fixture (data1, no repair yet): here && sudo "$h" '
                          'preview data1 && sudo "$h" apply data1 Required local setting: '
                          'header=owner-kept. Preserve both original and local edit before '
                          'upgrading; retain the new-default candidate independently.',
                          'Challenge outcome: Starting from data 1.0-1, preserve the original and '
                          'set header=owner-kept in only its declared configuration. Upgrade to '
                          'data 2.0-1 without replacing that local value. Retain and inspect '
                          '.rpmnew, verify actual package contents/version and deliberate config '
                          'discrepancy, then clean up with candidates preserved first. Expected '
                          'data 2.0 SHA-256 when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['Versions, original/config/new candidate hashes, owners/modes and '
                             'expected package-owned contents.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          'Do not assume Debian conffile semantics or silently overwrite user '
                          'content; skipped/different-version transactions are not upgrades.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': 'edae6c32ecda46b161fc983dfed35170eb162a8b91090a844a6d50a255778838',
  'entry_sha256': '15011a88f4faf11bc9bf5d962e11c20a8af798650d6e11c02194f973eab541e7',
  'learn': ['w=$(mktemp -d "$HOME/rpm-upgrade.XXXXXX") && cd "$w" && umask 077; here() { case "$w" '
            'in "$HOME"/rpm-upgrade.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" && '
            'test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd '
            '-P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here || '
            'return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
            '"$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'here && sudo "$h" preview data1 && printf \'APPLY\\n\' | sudo "$h" apply data1',
            'here && keepcfg /etc/learning-lab-rpm/report.conf original.conf && cfg '
            '/etc/learning-lab-rpm/report.conf && printf "%s\\n" header=owner-kept | sudo tee '
            '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
            '/etc/learning-lab-rpm/report.conf edited.conf && sudo "$h" preview upgrade',
            'here && printf \'APPLY\\n\' | sudo "$h" apply upgrade',
            'rpm_step() { here || return 19; cfg /etc/learning-lab-rpm/report.conf && cmp '
            'edited.conf /etc/learning-lab-rpm/report.conf && keepcfg '
            '/etc/learning-lab-rpm/report.conf.rpmnew candidate.conf && grep -Fx '
            'header=inventory-2.0 candidate.conf && fresh "$w/verification.txt" || return 19; if '
            'rpm -V ll-rpm-data > verification.txt; then return 1; else rc=$?; test "$rc" = 1 && '
            'grep -F /etc/learning-lab-rpm/report.conf verification.txt; fi; }; rpm_step'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-upgrade.XXXXXX") && cd "$w" && umask 077; here() { case '
                '"$w" in "$HOME"/rpm-upgrade.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
                'test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() '
                '{ here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; '
                '}; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'here && sudo "$h" preview data1 && printf \'APPLY\\n\' | sudo "$h" apply data1',
                'here && keepcfg /etc/learning-lab-rpm/report.conf original.conf && cfg '
                '/etc/learning-lab-rpm/report.conf && printf "%s\\n" header=owner-kept | sudo tee '
                '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                '/etc/learning-lab-rpm/report.conf edited.conf && sudo "$h" preview upgrade',
                'here && printf \'APPLY\\n\' | sudo "$h" apply upgrade',
                'rpm_step() { here || return 19; cfg /etc/learning-lab-rpm/report.conf && cmp '
                'edited.conf /etc/learning-lab-rpm/report.conf && keepcfg '
                '/etc/learning-lab-rpm/report.conf.rpmnew candidate.conf && grep -Fx '
                'header=inventory-2.0 candidate.conf && fresh "$w/verification.txt" || return 19; '
                'if rpm -V ll-rpm-data > verification.txt; then return 1; else rc=$?; test "$rc" = '
                '1 && grep -F /etc/learning-lab-rpm/report.conf verification.txt; fi; }; rpm_step'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-integrity',
              'content_version': '1.0.0',
              'title': 'Repair package-owned contents with independent verification',
              'goal': 'Distinguish rpm -V flags, package-owned digest state and expected '
                      'application output; reinstall exact local archive.',
              'challenge': 'Repair the prepared damaged package-owned data 2.0-1 file without '
                           'changing configuration or unrelated packages. Retain the failed '
                           'verification, prove restored expected bytes against the supplied '
                           'SHA-256 and preserved original, and actually read it as learner. Do '
                           'not merely hide rpm -V output or regenerate a checksum from the '
                           'damaged file.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-integrity.XXXXXX") && cd "$w" && '
                                    'umask 077; here() { case "$w" in '
                                    '"$HOME"/rpm-integrity.??????) ;; *) return 19;; esac; test '
                                    '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                                    '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && '
                                    'test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here '
                                    '|| return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test '
                                    '! -L "$1"; }; cfg() { case "$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'here && sudo "$h" apply data1 && sudo "$h" apply upgrade && '
                                    'fresh "$w/verify-before.txt" && rpm -V ll-rpm-data > '
                                    'verify-before.txt && test ! -s verify-before.txt && fresh '
                                    '"$w/original-data.txt" && cp '
                                    '/usr/share/learning-lab-rpm/data.txt original-data.txt',
                         'explanation': 'Use only supported operations: data1 then upgrade. '
                                        'Preserve clean package-owned bytes independently.',
                         'expected': 'Clean verification and data 2.0.'},
                        {'command': 'rpm_step() { here || return 19; test -f '
                                    '/usr/share/learning-lab-rpm/data.txt && test ! -L '
                                    '/usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
                                    '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm '
                                    '&& test "$(stat -c %U:%G:%a:%h '
                                    '/usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && '
                                    'fresh "$w/verify-damaged.txt" || return 19; printf "%s\\n" '
                                    'damaged | sudo tee /usr/share/learning-lab-rpm/data.txt '
                                    '>/dev/null || return 19; if rpm -V ll-rpm-data > '
                                    'verify-damaged.txt; then return 1; else test $? = 1 && grep '
                                    '-F /usr/share/learning-lab-rpm/data.txt verify-damaged.txt; '
                                    'fi; }; rpm_step',
                         'explanation': 'Change only the approved regular payload and retain '
                                        'actual RPM verification output. A learner-generated '
                                        'checksum alone is different evidence.',
                         'expected': 'Verification detects changed package-owned data.'},
                        {'command': 'here && sudo "$h" preview reinstall && sudo "$h" apply '
                                    'reinstall && fresh "$w/verify-after.txt" && rpm -V '
                                    'll-rpm-data > verify-after.txt && test ! -s verify-after.txt '
                                    '&& cmp original-data.txt /usr/share/learning-lab-rpm/data.txt '
                                    '&& test "$(sha256sum /usr/share/learning-lab-rpm/data.txt | '
                                    'cut -d " " -f1)" = '
                                    'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4 '
                                    '&& cat /usr/share/learning-lab-rpm/data.txt',
                         'explanation': 'Reinstall the exact admitted archive and prove '
                                        'independent byte recovery plus actual learner read '
                                        'access.',
                         'expected': 'Correct content/access and clean package verification.'}],
              'hints': ['Listing files or a successful reinstall does not prove content/access; '
                        'configured files may legitimately differ and need policy.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5 102.5 integrity/reinstall. DNF4 '
                          'awareness, not original YUM, DNF5 or Zypper proficiency. No '
                          'complete-objective or LPI endorsement claim.'},
  'entry': {'id': 'real-linux-rpm-integrity',
            'resource': 'real-linux-rpm-integrity.json',
            'description': 'Distinguish rpm -V flags, package-owned digest state and expected '
                           'application output; reinstall exact local archive.',
            'objectives': ['102.5 integrity/reinstall'],
            'troubleshooting': ['Listing files or a successful reinstall does not prove '
                                'content/access; configured files may legitimately differ and need '
                                'policy.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-integrity.XXXXXX") && cd "$w" && umask 077; here() { case '
                          '"$w" in "$HOME"/rpm-integrity.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here || return 19; test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                          '"$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Challenge preparation (not repair): challenge_fixture() { here && sudo '
                          '"$h" apply data1 && sudo "$h" apply upgrade && fresh '
                          '"$w/verify-before.txt" && rpm -V ll-rpm-data > verify-before.txt && '
                          'test ! -s verify-before.txt && fresh "$w/original-data.txt" && cp '
                          '/usr/share/learning-lab-rpm/data.txt original-data.txt || return 19; '
                          'rpm_step() { here || return 19; test -f '
                          '/usr/share/learning-lab-rpm/data.txt && test ! -L '
                          '/usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
                          '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm && test '
                          '"$(stat -c %U:%G:%a:%h /usr/share/learning-lab-rpm/data.txt)" = '
                          'root:root:644:1 && fresh "$w/verify-damaged.txt" || return 19; printf '
                          '"%s\\n" damaged | sudo tee /usr/share/learning-lab-rpm/data.txt '
                          '>/dev/null || return 19; if rpm -V ll-rpm-data > verify-damaged.txt; '
                          'then return 1; else test $? = 1 && grep -F '
                          '/usr/share/learning-lab-rpm/data.txt verify-damaged.txt; fi; }; '
                          'rpm_step; }; challenge_fixture',
                          'Challenge outcome: Repair the prepared damaged package-owned data 2.0-1 '
                          'file without changing configuration or unrelated packages. Retain the '
                          'failed verification, prove restored expected bytes against the supplied '
                          'SHA-256 and preserved original, and actually read it as learner. Do not '
                          'merely hide rpm -V output or regenerate a checksum from the damaged '
                          'file. Expected data 2.0 SHA-256 when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['Actual rpm verification before/after, reference comparison, intended '
                             'unprivileged-user read/result, unchanged other packages.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          'Listing files or a successful reinstall does not prove content/access; '
                          'configured files may legitimately differ and need policy.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': '37de56a7ba76b7d5991b71850504a53eae1f58881d28732dbaca40dda7be12d9',
  'entry_sha256': 'c48cb5a1d163b3fb658d9de18215cf31b16505b9b546e30729f9e182f0fb3941',
  'learn': ['w=$(mktemp -d "$HOME/rpm-integrity.XXXXXX") && cd "$w" && umask 077; here() { case '
            '"$w" in "$HOME"/rpm-integrity.??????) ;; *) return 19;; esac; test "${w%/*}" = '
            '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
            'test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
            'here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'cfg() { case "$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'here && printf \'APPLY\\n\' | sudo "$h" apply data1 && printf \'APPLY\\n\' | sudo '
            '"$h" apply upgrade && fresh "$w/verify-before.txt" && rpm -V ll-rpm-data > '
            'verify-before.txt && test ! -s verify-before.txt && fresh "$w/original-data.txt" && '
            'cp /usr/share/learning-lab-rpm/data.txt original-data.txt',
            'rpm_step() { here || return 19; test -f /usr/share/learning-lab-rpm/data.txt && test '
            '! -L /usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
            '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm && test "$(stat -c '
            '%U:%G:%a:%h /usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && fresh '
            '"$w/verify-damaged.txt" || return 19; printf "%s\\n" damaged | sudo tee '
            '/usr/share/learning-lab-rpm/data.txt >/dev/null || return 19; if rpm -V ll-rpm-data > '
            'verify-damaged.txt; then return 1; else test $? = 1 && grep -F '
            '/usr/share/learning-lab-rpm/data.txt verify-damaged.txt; fi; }; rpm_step',
            'here && sudo "$h" preview reinstall && printf \'APPLY\\n\' | sudo "$h" apply '
            'reinstall && fresh "$w/verify-after.txt" && rpm -V ll-rpm-data > verify-after.txt && '
            'test ! -s verify-after.txt && cmp original-data.txt '
            '/usr/share/learning-lab-rpm/data.txt && test "$(sha256sum '
            '/usr/share/learning-lab-rpm/data.txt | cut -d " " -f1)" = '
            'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4 && cat '
            '/usr/share/learning-lab-rpm/data.txt'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-integrity.XXXXXX") && cd "$w" && umask 077; here() { '
                'case "$w" in "$HOME"/rpm-integrity.??????) ;; *) return 19;; esac; test "${w%/*}" '
                '= "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" '
                '&& test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                'fresh() { here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L '
                '"$1"; }; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'challenge_fixture() { here && printf \'APPLY\\n\' | sudo "$h" apply data1 && '
                'printf \'APPLY\\n\' | sudo "$h" apply upgrade && fresh "$w/verify-before.txt" && '
                'rpm -V ll-rpm-data > verify-before.txt && test ! -s verify-before.txt && fresh '
                '"$w/original-data.txt" && cp /usr/share/learning-lab-rpm/data.txt '
                'original-data.txt || return 19; rpm_step() { here || return 19; test -f '
                '/usr/share/learning-lab-rpm/data.txt && test ! -L '
                '/usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
                '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm && test "$(stat -c '
                '%U:%G:%a:%h /usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && fresh '
                '"$w/verify-damaged.txt" || return 19; printf "%s\\n" damaged | sudo tee '
                '/usr/share/learning-lab-rpm/data.txt >/dev/null || return 19; if rpm -V '
                'll-rpm-data > verify-damaged.txt; then return 1; else test $? = 1 && grep -F '
                '/usr/share/learning-lab-rpm/data.txt verify-damaged.txt; fi; }; rpm_step; }; '
                'challenge_fixture',
                'here && sudo "$h" preview reinstall && printf \'APPLY\\n\' | sudo "$h" apply '
                'reinstall && fresh "$w/verify-after.txt" && rpm -V ll-rpm-data > verify-after.txt '
                '&& test ! -s verify-after.txt && cmp original-data.txt '
                '/usr/share/learning-lab-rpm/data.txt && test "$(sha256sum '
                '/usr/share/learning-lab-rpm/data.txt | cut -d " " -f1)" = '
                'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4 && cat '
                '/usr/share/learning-lab-rpm/data.txt'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-remove',
              'content_version': '1.0.0',
              'title': 'Remove only intended packages and explain retained files',
              'goal': 'Distinguish rpm erase, dependency order and config retention from Debian '
                      'remove/purge.',
              'challenge': 'Starting from the declared pair with header=owner-kept and '
                           'notes.txt=owner-notes, retain the exact dependent-removal refusal. '
                           'Remove only report then data, preserve and explain .rpmsave, keep '
                           'original/edit/notes byte-identical and return to fixture-free package '
                           'state. RPM has no universal purge equivalent.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-remove.XXXXXX") && cd "$w" && umask '
                                    '077; here() { case "$w" in "$HOME"/rpm-remove.??????) ;; *) '
                                    'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                                    'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test '
                                    '"$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                                    'learner:700; }; fresh() { here || return 19; test "${1%/*}" = '
                                    '"$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                                    '"$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'here && sudo "$h" apply pair && keepcfg '
                                    '/etc/learning-lab-rpm/report.conf original.conf && cfg '
                                    '/etc/learning-lab-rpm/report.conf && printf "%s\\n" '
                                    'header=owner-kept | sudo tee '
                                    '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                                    '/etc/learning-lab-rpm/report.conf edited.conf && fresh '
                                    '"$w/notes.txt" && printf "%s\\n" owner-notes > notes.txt',
                         'explanation': 'Prepare only declared fixtures; retain original/edit and '
                                        'unrelated user notes.',
                         'expected': 'Exact pair and protected user data.'},
                        {'command': 'rpm_step() { here || return 19; fresh "$w/dependency.txt" || '
                                    'return 19; if sudo "$h" preview remove-data > dependency.txt '
                                    '2>&1; then return 1; else test $? = 1 && grep -F "Remove '
                                    'report first" dependency.txt; fi; }; rpm_step',
                         'explanation': 'Do not implicitly remove a dependent package. Require the '
                                        'specific refusal, not any error.',
                         'expected': 'Both packages retained.'},
                        {'command': 'here && sudo "$h" apply remove-report && sudo "$h" apply '
                                    'remove-data && cfg /etc/learning-lab-rpm/report.conf.rpmsave '
                                    '&& cmp edited.conf /etc/learning-lab-rpm/report.conf.rpmsave '
                                    '&& keepcfg /etc/learning-lab-rpm/report.conf.rpmsave '
                                    'retained.conf && test "$(cat notes.txt)" = owner-notes',
                         'explanation': 'Confirm each exact removal. RPM has no universal '
                                        'Debian-style purge; this changed config survives as '
                                        '.rpmsave.',
                         'expected': 'No fixture package rows; owner edit and notes survive.'}],
              'hints': ['No universal RPM purge; --nodeps and autoremove can harm unrelated state; '
                        'absence of rpm row does not mean every user file vanished.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5 102.5 RPM removal. DNF4 awareness, not '
                          'original YUM, DNF5 or Zypper proficiency. No complete-objective or LPI '
                          'endorsement claim.'},
  'entry': {'id': 'real-linux-rpm-remove',
            'resource': 'real-linux-rpm-remove.json',
            'description': 'Distinguish rpm erase, dependency order and config retention from '
                           'Debian remove/purge.',
            'objectives': ['102.5 RPM removal'],
            'troubleshooting': ['No universal RPM purge; --nodeps and autoremove can harm '
                                'unrelated state; absence of rpm row does not mean every user file '
                                'vanished.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-remove.XXXXXX") && cd "$w" && umask 077; here() { case "$w" '
                          'in "$HOME"/rpm-remove.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                          '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" '
                          '= "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                          'learner:700; }; fresh() { here || return 19; test "${1%/*}" = "$w" && '
                          'test ! -e "$1" && test ! -L "$1"; }; cfg() { case "$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Challenge starting fixture: here && sudo "$h" apply pair && keepcfg '
                          '/etc/learning-lab-rpm/report.conf original.conf && cfg '
                          '/etc/learning-lab-rpm/report.conf && printf "%s\\n" header=owner-kept | '
                          'sudo tee /etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                          '/etc/learning-lab-rpm/report.conf edited.conf && fresh "$w/notes.txt" '
                          '&& printf "%s\\n" owner-notes > notes.txt',
                          'Challenge outcome: Starting from the declared pair with '
                          'header=owner-kept and notes.txt=owner-notes, retain the exact '
                          'dependent-removal refusal. Remove only report then data, preserve and '
                          'explain .rpmsave, keep original/edit/notes byte-identical and return to '
                          'fixture-free package state. RPM has no universal purge equivalent. '
                          'Expected data 2.0 SHA-256 when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['Dependency refusal, exact erased identities, retained '
                             'configuration/content and byte-identical nonfixture inventory.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          'No universal RPM purge; --nodeps and autoremove can harm unrelated '
                          'state; absence of rpm row does not mean every user file vanished.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': 'e849104ee8c62b8fd88b3166ef9ef1892b9362d3b1572622e010c0a6e60c292f',
  'entry_sha256': 'fa0722e294df61b4bf2fc8d71a646ea0f1d759db4adc439481ecafb8a7842e60',
  'learn': ['w=$(mktemp -d "$HOME/rpm-remove.XXXXXX") && cd "$w" && umask 077; here() { case "$w" '
            'in "$HOME"/rpm-remove.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" && '
            'test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd '
            '-P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here || '
            'return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
            '"$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'here && printf \'APPLY\\n\' | sudo "$h" apply pair && keepcfg '
            '/etc/learning-lab-rpm/report.conf original.conf && cfg '
            '/etc/learning-lab-rpm/report.conf && printf "%s\\n" header=owner-kept | sudo tee '
            '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
            '/etc/learning-lab-rpm/report.conf edited.conf && fresh "$w/notes.txt" && printf '
            '"%s\\n" owner-notes > notes.txt',
            'rpm_step() { here || return 19; fresh "$w/dependency.txt" || return 19; if sudo "$h" '
            'preview remove-data > dependency.txt 2>&1; then return 1; else test $? = 1 && grep -F '
            '"Remove report first" dependency.txt; fi; }; rpm_step',
            'here && printf \'APPLY\\n\' | sudo "$h" apply remove-report && printf \'APPLY\\n\' | '
            'sudo "$h" apply remove-data && cfg /etc/learning-lab-rpm/report.conf.rpmsave && cmp '
            'edited.conf /etc/learning-lab-rpm/report.conf.rpmsave && keepcfg '
            '/etc/learning-lab-rpm/report.conf.rpmsave retained.conf && test "$(cat notes.txt)" = '
            'owner-notes'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-remove.XXXXXX") && cd "$w" && umask 077; here() { case '
                '"$w" in "$HOME"/rpm-remove.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
                'test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() '
                '{ here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; '
                '}; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'here && printf \'APPLY\\n\' | sudo "$h" apply pair && keepcfg '
                '/etc/learning-lab-rpm/report.conf original.conf && cfg '
                '/etc/learning-lab-rpm/report.conf && printf "%s\\n" header=owner-kept | sudo tee '
                '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                '/etc/learning-lab-rpm/report.conf edited.conf && fresh "$w/notes.txt" && printf '
                '"%s\\n" owner-notes > notes.txt',
                'rpm_step() { here || return 19; fresh "$w/dependency.txt" || return 19; if sudo '
                '"$h" preview remove-data > dependency.txt 2>&1; then return 1; else test $? = 1 '
                '&& grep -F "Remove report first" dependency.txt; fi; }; rpm_step',
                'here && printf \'APPLY\\n\' | sudo "$h" apply remove-report && printf '
                '\'APPLY\\n\' | sudo "$h" apply remove-data && cfg '
                '/etc/learning-lab-rpm/report.conf.rpmsave && cmp edited.conf '
                '/etc/learning-lab-rpm/report.conf.rpmsave && keepcfg '
                '/etc/learning-lab-rpm/report.conf.rpmsave retained.conf && test "$(cat '
                'notes.txt)" = owner-notes'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'rpm',
  'image_id': 'almalinux9-rpm-admin-local-v1',
  'content': {'id': 'real-linux-rpm-recovery',
              'content_version': '1.0.0',
              'title': 'Repair an offline package incident and hand it over',
              'goal': 'Independently select a compatible fixture version, restore verified '
                      'content/config and leave unrelated packages untouched.',
              'challenge': 'An old handover claims data 1.0, but inspect the installed pair rather '
                           'than trusting it. Preserve header=handover-kept and the original '
                           'configuration; reject the inappropriate upgrade with its exact '
                           'refusal, recover the prepared damaged data to its supplied independent '
                           'SHA-256, and produce the full expected unprivileged report. Keep prior '
                           'damage evidence and unrelated package state; finish exact cleanup.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/rpm-recovery.XXXXXX") && cd "$w" && '
                                    'umask 077; here() { case "$w" in "$HOME"/rpm-recovery.??????) '
                                    ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d '
                                    '"$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" '
                                    '&& test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                                    'learner:700; }; fresh() { here || return 19; test "${1%/*}" = '
                                    '"$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                                    '"$1" in '
                                    '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                                    ';; *) return 19;; esac; here && test "$(realpath -e '
                                    '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test '
                                    '"$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = root:root:755 '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c '
                                    '%U:%G:%a:%h "$1")" = root:root:644:1; }; keepcfg() { cfg "$1" '
                                    '&& fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp -- "$1" "$w/$2" '
                                    '&& test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
                                    'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                                    '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h '
                                    '"$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm '
                                    '-- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
                                    'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && fresh '
                                    '"$w/before.json" && sudo "$h" status > before.json && grep -F '
                                    '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" '
                                    '&& timeout -k 1s 20s sudo rpm -qa --qf '
                                    "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' "
                                    '> before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort '
                                    'before-raw.tsv > before.tsv && pwd',
                         'explanation': 'Record this private path and shell definitions. A guard '
                                        'failure stops the exercise; do not continue over existing '
                                        'fixtures. Resume requires recorded path/definitions, not '
                                        'replaying setup.',
                         'expected': 'Fixture-free package baseline retained without masking query '
                                     'failure.'},
                        {'command': 'here && sudo "$h" apply pair && keepcfg '
                                    '/etc/learning-lab-rpm/report.conf original.conf && cfg '
                                    '/etc/learning-lab-rpm/report.conf && printf "%s\\n" '
                                    'header=handover-kept | sudo tee '
                                    '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                                    '/etc/learning-lab-rpm/report.conf edited.conf && fresh '
                                    '"$w/incident.txt" && printf "%s\\n" "Old note claims data '
                                    '1.0. Actual target: data 2.0-1/report 1.0-1." "Retain '
                                    'header=handover-kept and repair the approved damaged data." > '
                                    'incident.txt && cat incident.txt',
                         'explanation': 'Create a misleading handover distinct from the upgrade '
                                        'lesson. The initial pair is compatible; inspect reality '
                                        'before choosing a repair.',
                         'expected': 'Known original/edit; target versions independently stated.'},
                        {'command': 'rpm_step() { here || return 19; fresh "$w/wrong-plan.txt" || '
                                    'return 19; if sudo "$h" preview upgrade > wrong-plan.txt '
                                    '2>&1; then return 1; else test $? = 1 && grep -F "upgrade '
                                    'requires data1 only" wrong-plan.txt; fi; }; rpm_step',
                         'explanation': 'An upgrade based on stale inventory is wrong for '
                                        'installed data 2.0. Retain the exact refusal.',
                         'expected': 'No package changes; specific wrong-plan refusal.'},
                        {'command': 'rpm_step() { here || return 19; test -f '
                                    '/usr/share/learning-lab-rpm/data.txt && test ! -L '
                                    '/usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
                                    '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm '
                                    '&& test "$(stat -c %U:%G:%a:%h '
                                    '/usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && '
                                    'fresh "$w/verify-damaged.txt" || return 19; printf "%s\\n" '
                                    'damaged | sudo tee /usr/share/learning-lab-rpm/data.txt '
                                    '>/dev/null || return 19; if rpm -V ll-rpm-data > '
                                    'verify-damaged.txt; then return 1; else test $? = 1 && grep '
                                    '-F /usr/share/learning-lab-rpm/data.txt verify-damaged.txt; '
                                    'fi; }; rpm_step',
                         'explanation': 'Retain the deliberate package-owned damage evidence '
                                        'before repair. The expected independent data hash remains '
                                        'supplied.',
                         'expected': 'Actual damage detected; owner configuration retained.'},
                        {'command': 'here && sudo "$h" preview reinstall && sudo "$h" apply '
                                    'reinstall && cfg /etc/learning-lab-rpm/report.conf && cmp '
                                    'edited.conf /etc/learning-lab-rpm/report.conf && test '
                                    '"$(sha256sum /usr/share/learning-lab-rpm/data.txt | cut -d " '
                                    '" -f1)" = '
                                    'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4 '
                                    '&& fresh "$w/report.txt" && fresh "$w/expected-report.txt" && '
                                    '/usr/bin/ll-rpm-report > report.txt && printf "%s\\n" '
                                    '"Learning Lab package report" header=handover-kept "Learning '
                                    'Lab offline inventory" fixture_data_version=2.0 items=3 > '
                                    'expected-report.txt && cmp expected-report.txt report.txt && '
                                    'cat report.txt',
                         'explanation': 'Repair only the approved payload while preserving the '
                                        'owner edit. Check actual unprivileged report output '
                                        'against full expected bytes.',
                         'expected': 'Working correct-version report and independent content '
                                     'recovery.'}],
              'hints': ['A valid signature/digest or zero transaction status alone is '
                        'insufficient; do not invent complete RPM objective coverage.',
                        'Read supported helper operations and the exact plan before APPLY. '
                        'Unsigned fixture digests do not prove publisher authenticity.',
                        'Verify versions, payload/config bytes and actual learner access; package '
                        'exit status alone is insufficient.'],
              'review': ['I retained the requested actual output, statuses, versions and '
                         'byte/access evidence, including the incorrect case.',
                         'I met the selected mode’s outcomes and can explain the limitations. '
                         'Completion records self-review, not a score or verified assessment.',
                         'I preserved originals and retained candidates, compared unrelated '
                         'package state and completed only the exact cleanup.'],
              'coverage': 'LPIC-1 active v5.0 partial 102.5 102.5 transfer; no claim of full '
                          'objective or Zypper/YUM mastery. DNF4 awareness, not original YUM, DNF5 '
                          'or Zypper proficiency. No complete-objective or LPI endorsement claim.'},
  'entry': {'id': 'real-linux-rpm-recovery',
            'resource': 'real-linux-rpm-recovery.json',
            'description': 'Independently select a compatible fixture version, restore verified '
                           'content/config and leave unrelated packages untouched.',
            'objectives': ['102.5 transfer; no claim of full objective or Zypper/YUM mastery'],
            'troubleshooting': ['A valid signature/digest or zero transaction status alone is '
                                'insufficient; do not invent complete RPM objective coverage.',
                                'If the helper times out or retains incomplete state, inspect '
                                'evidence; do not retry blindly. Resume boots the same disk, not '
                                'RAM or shell variables.'],
            'cleanup': ['Run in the recorded workspace before removing packages; candidates '
                        'otherwise block the helper. Preserve and byte-check each named root-owned '
                        'regular single-link candidate before removing it. rpm_cleanup_step() { '
                        'here || return 19; for suffix in rpmnew rpmsave; do '
                        'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test '
                        '-L "$src"; then keepcfg "$src" "cleanup-before-$suffix.conf" && '
                        'releasecfg "$src" "cleanup-before-$suffix.conf" || return 19; fi; done; '
                        '}; rpm_cleanup_step',
                        'After candidate preservation, inspect and confirm exact fixture removals, '
                        'report first. Accept absence only with this exact recorded '
                        'missing-package result; query errors stop cleanup. rpm_cleanup_step() { '
                        'here || return 19; for name in ll-rpm-report ll-rpm-data; do fresh '
                        '"$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
                        '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
                        'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; '
                        'sudo "$h" preview "$op" && sudo "$h" apply "$op" || return 19; else '
                        'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
                        '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
                        'Preserve a newly produced .rpmsave, then compare actual full package '
                        'state. This does not claim a general guest-policy audit. here && if test '
                        '-e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
                        '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
                        '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && '
                        'releasecfg /etc/learning-lab-rpm/report.conf.rpmsave '
                        'cleanup-after-rpmsave.conf; fi && fresh "$w/after.json" && sudo "$h" '
                        'status > after.json && grep -F \'"fixtures": {}\' after.json && cmp '
                        'before.json after.json && fresh "$w/after-raw.tsv" && timeout -k 1s 20s '
                        'sudo rpm -qa --qf '
                        "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                        'after-raw.tsv && fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > '
                        'after.tsv && cmp before.tsv after.tsv',
                        'Keep this exact private workspace and helper records as evidence; do not '
                        'delete source archives, /opt resources, or helper transactions. Repeated '
                        'cleanup must inspect retained after.json/candidates and refuse '
                        'overwriting them; use Reset if interrupted ownership/state is ambiguous. '
                        'No recursive cleanup. Guest root can bypass these cooperative guards.'],
            'materials': ['Fresh Learn or Challenge setup (no repair performed): w=$(mktemp -d '
                          '"$HOME/rpm-recovery.XXXXXX") && cd "$w" && umask 077; here() { case '
                          '"$w" in "$HOME"/rpm-recovery.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here || return 19; test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
                          '"$1" in '
                          '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                          ';; *) return 19;; esac; here && test "$(realpath -e '
                          '/etc/learning-lab-rpm)" = /etc/learning-lab-rpm && test "$(stat -c '
                          '%U:%G:%a /etc/learning-lab-rpm)" = root:root:755 && test -f "$1" && '
                          'test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" = root:root:644:1; '
                          '}; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && cmp '
                          '-- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; '
                          '}; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" '
                          '&& test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                          'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                          'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; '
                          'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && '
                          'fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
                          '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout '
                          '-k 1s 20s sudo rpm -qa --qf '
                          "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
                          'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv '
                          '> before.tsv && pwd',
                          'Supported fixed helper operations: status; preview/apply data1, pair, '
                          'upgrade, reinstall, remove-report, remove-data. There is no data2 '
                          'operation. APPLY requires explicit confirmation within 60 seconds; '
                          'arbitrary paths/names/options are rejected.',
                          'Challenge preparation (not repair): challenge_fixture() { here && sudo '
                          '"$h" apply pair && keepcfg /etc/learning-lab-rpm/report.conf '
                          'original.conf && cfg /etc/learning-lab-rpm/report.conf && printf '
                          '"%s\\n" header=handover-kept | sudo tee '
                          '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                          '/etc/learning-lab-rpm/report.conf edited.conf && fresh '
                          '"$w/incident.txt" && printf "%s\\n" "Old note claims data 1.0. Actual '
                          'target: data 2.0-1/report 1.0-1." "Retain header=handover-kept and '
                          'repair the approved damaged data." > incident.txt && cat incident.txt '
                          '|| return 19; rpm_step() { here || return 19; test -f '
                          '/usr/share/learning-lab-rpm/data.txt && test ! -L '
                          '/usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
                          '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm && test '
                          '"$(stat -c %U:%G:%a:%h /usr/share/learning-lab-rpm/data.txt)" = '
                          'root:root:644:1 && fresh "$w/verify-damaged.txt" || return 19; printf '
                          '"%s\\n" damaged | sudo tee /usr/share/learning-lab-rpm/data.txt '
                          '>/dev/null || return 19; if rpm -V ll-rpm-data > verify-damaged.txt; '
                          'then return 1; else test $? = 1 && grep -F '
                          '/usr/share/learning-lab-rpm/data.txt verify-damaged.txt; fi; }; '
                          'rpm_step; }; challenge_fixture',
                          'Challenge outcome: An old handover claims data 1.0, but inspect the '
                          'installed pair rather than trusting it. Preserve header=handover-kept '
                          'and the original configuration; reject the inappropriate upgrade with '
                          'its exact refusal, recover the prepared damaged data to its supplied '
                          'independent SHA-256, and produce the full expected unprivileged report. '
                          'Keep prior damage evidence and unrelated package state; finish exact '
                          'cleanup. Expected data 2.0 SHA-256 when relevant: '
                          'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4. Full '
                          'expected report: Learning Lab package report; required header; Learning '
                          'Lab offline inventory; fixture_data_version=2.0; items=3.',
                          'On same-disk Resume, use the recorded directory rather than mktemp. '
                          'Restore its displayed here/fresh/cfg/keepcfg/releasecfg functions and '
                          'h/f variables from the setup text. Inspect retained reports and helper '
                          'status before continuing; never recreate or overwrite a fixture '
                          'silently.'],
            'observations': ['All intended fixture outcomes, negative-plan refusal, exact '
                             'versions/file bytes/access and unchanged unrelated package/guest '
                             'policy.',
                             'Actual nonfixture package comparison and intended learner '
                             'read/execute output, where the task installs a fixture.'],
            'questions': ['Which observation establishes the factual outcome, and which '
                          'conclusions remain unverified?',
                          'A valid signature/digest or zero transaction status alone is '
                          'insufficient; do not invent complete RPM objective coverage.'],
            'limitations': ['Existing guest only. No NIC, host shares or automatic assessment. '
                            'Guest root can modify/bypass the helper and guest limits. The helper '
                            'permits only three inspected local archives and fixed operations; '
                            'official package verification remains enabled. It uses one resolved '
                            'transaction, 60 seconds, a 32 MiB per-file kernel limit, 32 retained '
                            'transactions, 256 MiB logical evidence admission and at least 1 GiB '
                            'observed free space. Accounting is not a quota/reserve. Reset retains '
                            'the old disk; do not prune helper records.',
                            'No repository/network practice, arbitrary RPM extraction, signatures '
                            'of these unsigned fixtures, Zypper or broad package-manager '
                            'proficiency.']},
  'resource_sha256': 'c7e27d11b1c99c3b037fa18ffdac9c5621f87c0f721a1168bdab2c5bbce41819',
  'entry_sha256': '7acddf66ad59e7fec9a18e6020b45625b169848280c65d86ba8f02a905b5c63d',
  'learn': ['w=$(mktemp -d "$HOME/rpm-recovery.XXXXXX") && cd "$w" && umask 077; here() { case '
            '"$w" in "$HOME"/rpm-recovery.??????) ;; *) return 19;; esac; test "${w%/*}" = "$HOME" '
            '&& test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd '
            '-P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here || '
            'return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; cfg() { case '
            '"$1" in '
            '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
            ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
            '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
            'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h "$1")" '
            '= root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" "$w/$2" && '
            'cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1; }; '
            'releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f "$w/$2" && test ! -L '
            '"$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = learner:600:1 && cmp -- "$1" "$w/$2" '
            '&& sudo rm -- "$1"; }; h=/usr/local/sbin/ll-rpm-fixture; '
            'f=/opt/learning-lab/rpm-fixtures; here && test "$(df -B1 --output=avail / | tail -1)" '
            '-ge 1073741824 && fresh "$w/before.json" && sudo "$h" status > before.json && grep -F '
            '\'"fixtures": {}\' before.json && fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo '
            "rpm -qa --qf '%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > "
            'before-raw.tsv && fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv '
            '&& pwd',
            'here && printf \'APPLY\\n\' | sudo "$h" apply pair && keepcfg '
            '/etc/learning-lab-rpm/report.conf original.conf && cfg '
            '/etc/learning-lab-rpm/report.conf && printf "%s\\n" header=handover-kept | sudo tee '
            '/etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
            '/etc/learning-lab-rpm/report.conf edited.conf && fresh "$w/incident.txt" && printf '
            '"%s\\n" "Old note claims data 1.0. Actual target: data 2.0-1/report 1.0-1." "Retain '
            'header=handover-kept and repair the approved damaged data." > incident.txt && cat '
            'incident.txt',
            'rpm_step() { here || return 19; fresh "$w/wrong-plan.txt" || return 19; if sudo "$h" '
            'preview upgrade > wrong-plan.txt 2>&1; then return 1; else test $? = 1 && grep -F '
            '"upgrade requires data1 only" wrong-plan.txt; fi; }; rpm_step',
            'rpm_step() { here || return 19; test -f /usr/share/learning-lab-rpm/data.txt && test '
            '! -L /usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
            '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm && test "$(stat -c '
            '%U:%G:%a:%h /usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && fresh '
            '"$w/verify-damaged.txt" || return 19; printf "%s\\n" damaged | sudo tee '
            '/usr/share/learning-lab-rpm/data.txt >/dev/null || return 19; if rpm -V ll-rpm-data > '
            'verify-damaged.txt; then return 1; else test $? = 1 && grep -F '
            '/usr/share/learning-lab-rpm/data.txt verify-damaged.txt; fi; }; rpm_step',
            'here && sudo "$h" preview reinstall && printf \'APPLY\\n\' | sudo "$h" apply '
            'reinstall && cfg /etc/learning-lab-rpm/report.conf && cmp edited.conf '
            '/etc/learning-lab-rpm/report.conf && test "$(sha256sum '
            '/usr/share/learning-lab-rpm/data.txt | cut -d " " -f1)" = '
            'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4 && fresh '
            '"$w/report.txt" && fresh "$w/expected-report.txt" && /usr/bin/ll-rpm-report > '
            'report.txt && printf "%s\\n" "Learning Lab package report" header=handover-kept '
            '"Learning Lab offline inventory" fixture_data_version=2.0 items=3 > '
            'expected-report.txt && cmp expected-report.txt report.txt && cat report.txt'],
  'challenge': ['w=$(mktemp -d "$HOME/rpm-recovery.XXXXXX") && cd "$w" && umask 077; here() { case '
                '"$w" in "$HOME"/rpm-recovery.??????) ;; *) return 19;; esac; test "${w%/*}" = '
                '"$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && '
                'test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() '
                '{ here || return 19; test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; '
                '}; cfg() { case "$1" in '
                '/etc/learning-lab-rpm/report.conf|/etc/learning-lab-rpm/report.conf.rpmnew|/etc/learning-lab-rpm/report.conf.rpmsave) '
                ';; *) return 19;; esac; here && test "$(realpath -e /etc/learning-lab-rpm)" = '
                '/etc/learning-lab-rpm && test "$(stat -c %U:%G:%a /etc/learning-lab-rpm)" = '
                'root:root:755 && test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%G:%a:%h '
                '"$1")" = root:root:644:1; }; keepcfg() { cfg "$1" && fresh "$w/$2" && cp -- "$1" '
                '"$w/$2" && cmp -- "$1" "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1; }; releasecfg() { cfg "$1" && test "${2##*/}" = "$2" && test -f '
                '"$w/$2" && test ! -L "$w/$2" && test "$(stat -c %U:%a:%h "$w/$2")" = '
                'learner:600:1 && cmp -- "$1" "$w/$2" && sudo rm -- "$1"; }; '
                'h=/usr/local/sbin/ll-rpm-fixture; f=/opt/learning-lab/rpm-fixtures; here && test '
                '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && fresh "$w/before.json" '
                '&& sudo "$h" status > before.json && grep -F \'"fixtures": {}\' before.json && '
                'fresh "$w/before-raw.tsv" && timeout -k 1s 20s sudo rpm -qa --qf '
                "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > before-raw.tsv "
                '&& fresh "$w/before.tsv" && LC_ALL=C sort before-raw.tsv > before.tsv && pwd',
                'challenge_fixture() { here && printf \'APPLY\\n\' | sudo "$h" apply pair && '
                'keepcfg /etc/learning-lab-rpm/report.conf original.conf && cfg '
                '/etc/learning-lab-rpm/report.conf && printf "%s\\n" header=handover-kept | sudo '
                'tee /etc/learning-lab-rpm/report.conf >/dev/null && keepcfg '
                '/etc/learning-lab-rpm/report.conf edited.conf && fresh "$w/incident.txt" && '
                'printf "%s\\n" "Old note claims data 1.0. Actual target: data 2.0-1/report '
                '1.0-1." "Retain header=handover-kept and repair the approved damaged data." > '
                'incident.txt && cat incident.txt || return 19; rpm_step() { here || return 19; '
                'test -f /usr/share/learning-lab-rpm/data.txt && test ! -L '
                '/usr/share/learning-lab-rpm/data.txt && test "$(realpath -e '
                '/usr/share/learning-lab-rpm)" = /usr/share/learning-lab-rpm && test "$(stat -c '
                '%U:%G:%a:%h /usr/share/learning-lab-rpm/data.txt)" = root:root:644:1 && fresh '
                '"$w/verify-damaged.txt" || return 19; printf "%s\\n" damaged | sudo tee '
                '/usr/share/learning-lab-rpm/data.txt >/dev/null || return 19; if rpm -V '
                'll-rpm-data > verify-damaged.txt; then return 1; else test $? = 1 && grep -F '
                '/usr/share/learning-lab-rpm/data.txt verify-damaged.txt; fi; }; rpm_step; }; '
                'challenge_fixture',
                'rpm_step() { here || return 19; fresh "$w/wrong-plan.txt" || return 19; if sudo '
                '"$h" preview upgrade > wrong-plan.txt 2>&1; then return 1; else test $? = 1 && '
                'grep -F "upgrade requires data1 only" wrong-plan.txt; fi; }; rpm_step',
                'here && sudo "$h" preview reinstall && printf \'APPLY\\n\' | sudo "$h" apply '
                'reinstall && cfg /etc/learning-lab-rpm/report.conf && cmp edited.conf '
                '/etc/learning-lab-rpm/report.conf && test "$(sha256sum '
                '/usr/share/learning-lab-rpm/data.txt | cut -d " " -f1)" = '
                'efcc5782abc5684c58caca66d0f23fbf64bc72109e4f937575ff834bb7c1cac4 && fresh '
                '"$w/report.txt" && fresh "$w/expected-report.txt" && /usr/bin/ll-rpm-report > '
                'report.txt && printf "%s\\n" "Learning Lab package report" header=handover-kept '
                '"Learning Lab offline inventory" fixture_data_version=2.0 items=3 > '
                'expected-report.txt && cmp expected-report.txt report.txt && cat report.txt'],
  'cleanup': ['rpm_cleanup_step() { here || return 19; for suffix in rpmnew rpmsave; do '
              'src=/etc/learning-lab-rpm/report.conf.$suffix; if test -e "$src" || test -L "$src"; '
              'then keepcfg "$src" "cleanup-before-$suffix.conf" && releasecfg "$src" '
              '"cleanup-before-$suffix.conf" || return 19; fi; done; }; rpm_cleanup_step',
              'rpm_cleanup_step() { here || return 19; for name in ll-rpm-report ll-rpm-data; do '
              'fresh "$w/cleanup-query-$name.txt" || return 19; if LC_ALL=C rpm -q "$name" > '
              '"$w/cleanup-query-$name.txt" 2>&1; then case "$name" in ll-rpm-report) '
              'op=remove-report;; ll-rpm-data) op=remove-data;; *) return 19;; esac; sudo "$h" '
              'preview "$op" && printf \'APPLY\\n\' | sudo "$h" apply "$op" || return 19; else '
              'rc=$?; test "$rc" = 1 && grep -Fx "package $name is not installed" '
              '"$w/cleanup-query-$name.txt" || return 19; fi; done; }; rpm_cleanup_step',
              'here && if test -e /etc/learning-lab-rpm/report.conf.rpmsave || test -L '
              '/etc/learning-lab-rpm/report.conf.rpmsave; then keepcfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf && releasecfg '
              '/etc/learning-lab-rpm/report.conf.rpmsave cleanup-after-rpmsave.conf; fi && fresh '
              '"$w/after.json" && sudo "$h" status > after.json && grep -F \'"fixtures": {}\' '
              'after.json && cmp before.json after.json && fresh "$w/after-raw.tsv" && timeout -k '
              '1s 20s sudo rpm -qa --qf '
              "'%{NAME}\\t%{EPOCHNUM}\\t%{VERSION}\\t%{RELEASE}\\t%{ARCH}\\n' > after-raw.tsv && "
              'fresh "$w/after.tsv" && LC_ALL=C sort after-raw.tsv > after.tsv && cmp before.tsv '
              'after.tsv'],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-locale-scope',
              'content_version': '1.0.0',
              'title': 'Choose the locale scope deliberately',
              'goal': 'Separate LANG, category overrides and LC_ALL; make one command '
                      'deterministic without changing a login default.',
              'challenge': 'A child command inherits LANG=de_DE.UTF-8 but LC_ALL=C. Demonstrate '
                           'why its decimal point remains a dot. Supply a corrected one-command '
                           'environment whose numeric category is German while machine processing '
                           'remains explicit C elsewhere. Prove parent locale/default unchanged; '
                           'do not edit system policy.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-locale-scope.XXXXXX") && cd '
                                    '"$w" && umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-locale-scope.??????) ;; *) return 19;; '
                                    'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L '
                                    '"$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" '
                                    '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                                    'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && '
                                    'test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h '
                                    '"$1")" = learner:600:1; }; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                         'explanation': 'Record this unique guest-only workspace. On Resume '
                                        're-establish the recorded path/definitions; never '
                                        'overwrite another exercise.',
                         'expected': 'Private learner-owned700 directory and observed1GiB free '
                                     'admission.'},
                        {'command': 'here && fresh "$w/parent.txt" && fresh "$w/default.sha" && '
                                    'locale > parent.txt && sha256sum /etc/locale.conf > '
                                    'default.sha && locale -a && locale charmap',
                         'explanation': 'Record parent and system default before isolated command '
                                        'environments. Generated locales are real guest resources.',
                         'expected': 'Both en_US.utf8/de_DE.utf8 available; UTF-8 charmap.'},
                        {'command': 'here && fresh "$w/precedence.txt" && env LANG=de_DE.UTF-8 '
                                    'LC_ALL=C locale -k decimal_point > precedence.txt && grep -Fx '
                                    '\'decimal_point="."\' precedence.txt && fresh '
                                    '"$w/category.txt" && env -u LC_ALL LANG=en_US.UTF-8 '
                                    'LC_NUMERIC=de_DE.UTF-8 locale -k decimal_point > category.txt '
                                    '&& grep -Fx \'decimal_point=","\' category.txt',
                         'explanation': 'LC_ALL overrides LANG and category variables. Remove only '
                                        'the child override, then apply LC_NUMERIC deliberately.',
                         'expected': 'Actual decimal point changes only in the selected child '
                                     'category.'},
                        {'command': 'here && fresh "$w/after.txt" && locale > after.txt && cmp '
                                    'parent.txt after.txt && sha256sum -c default.sha',
                         'explanation': 'Compare real parent environment and default bytes. A '
                                        'displayed language does not by itself establish '
                                        'persistence.',
                         'expected': 'Parent/default unchanged.'}],
              'hints': ['LANG alone does not override LC_ALL; an unavailable locale is not a valid '
                        'localized result.',
                        'Choose command scope deliberately; compare known bytes and actual '
                        'statuses, not only a successful-looking display.',
                        'Retain before evidence; refuse collisions and restore exact policy state '
                        'before leaving. Guest root can bypass guest-side guards.'],
              'review': ['I demonstrated the selected mode’s actual observations and retained an '
                         'incorrect or incomplete case.',
                         'I preserved originals and can explain the reasoning and limitations; '
                         'this records self-review, not automatic assessment.',
                         'I restored any changed default/zone and retained the exact workspace '
                         'without touching unrelated files.'],
              'coverage': 'LPIC-1 active v5.0 partial 107.3 locale environment; 103.1 variables: '
                          'reinforcement. No complete-objective coverage or endorsement.'},
  'entry': {'id': 'real-linux-foundation-locale-scope',
            'resource': 'real-linux-foundation-locale-scope.json',
            'description': 'Separate LANG, category overrides and LC_ALL; make one command '
                           'deterministic without changing a login default.',
            'objectives': ['107.3 locale environment', '103.1 variables: reinforcement'],
            'troubleshooting': ['LANG alone does not override LC_ALL; an unavailable locale is not '
                                'a valid localized result.',
                                'A missing tool/default or unexpected collision is a refusal, not '
                                'permission to change image/PAM/packages. Retain the failure and '
                                'Reset if exact rollback cannot be proved.'],
            'cleanup': ['Stay inside the recorded private workspace; retain its original and '
                        'result files as evidence. Do not recursively delete or remove unknown '
                        'members.',
                        'If default locale/timezone changed, perform only the displayed guarded '
                        'exact rollback before leaving. Keep root snapshot evidence; no '
                        'authentication, clock, RTC, NTP or host changes.',
                        'Reset retains disk generations. Resume boots the same disk, not RAM, '
                        'shell variables or processes. Re-enter only recorded path/function '
                        'definitions.'],
            'materials': ['For either mode, this is the non-repair workspace setup: w=$(mktemp -d '
                          '"$HOME/foundation-locale-scope.XXXXXX") && cd "$w" && umask 077; here() '
                          '{ case "$w" in "$HOME"/foundation-locale-scope.??????) ;; *) return '
                          '19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" '
                          '&& test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 '
                          '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                          'On Resume set w to its recorded exact path, cd there and restore the '
                          'definitions; do not run mktemp or recreate retained fixtures. '
                          'Definitions: here() { case "$w" in '
                          '"$HOME"/foundation-locale-scope.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = '
                          '"$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { here && test '
                          '"${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test "$(stat -c '
                          '%U:%a:%h "$1")" = learner:600:1; }',
                          'Challenge starting context, not repair: here && env LANG=de_DE.UTF-8 '
                          'LC_ALL=C locale -k decimal_point. Required numeric decimal point is '
                          'comma in only the corrected child; parent/default remain unchanged. '
                          'Preserve a parent locale report and /etc/locale.conf hash before '
                          'investigation.'],
            'observations': ['Before/child/parent locale output, statuses, byte-exact '
                             'system-default snapshot, explanation of category precedence.',
                             'Observed command/status/byte outcomes, not automatically graded '
                             'reasoning.'],
            'questions': ['Which evidence proves the specific outcome, and what does it not '
                          'establish?',
                          'LANG alone does not override LC_ALL; an unavailable locale is not a '
                          'valid localized result.'],
            'limitations': ['Real offline guest, not supplied snapshots. One worker; <=64KiB input '
                            'and small fixed-fixture expected outputs below256KiB (cooperative '
                            'accounting, not a kernel aggregate quota). Each iconv/xz command10s '
                            'plus1s grace and64MiB xz cap; no large arbitrary streams. Free-space '
                            'admission is not a quota or guaranteed reserve. Guest root can '
                            'override guest-side limits.',
                            'No clock/RTC/NTP writes, networking, new credentials, source '
                            'replacement, automatic grading or public-release claim. Physical '
                            'keyboard/accessibility checks remain separate.']},
  'resource_sha256': 'cd08944d538794721fca1f07943c5a9a267166cc9018f89879b99502317b5bef',
  'entry_sha256': 'fc4134a916146e8563eb0fac5fedebfc1b6e3b0b4832c15d53a090c491b564c7',
  'learn': ['w=$(mktemp -d "$HOME/foundation-locale-scope.XXXXXX") && cd "$w" && umask 077; here() '
            '{ case "$w" in "$HOME"/foundation-locale-scope.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
            '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 --output=avail '
            '/ | tail -1)" -ge 1073741824 && pwd',
            'here && fresh "$w/parent.txt" && fresh "$w/default.sha" && locale > parent.txt && '
            'sha256sum /etc/locale.conf > default.sha && locale -a && locale charmap',
            'here && fresh "$w/precedence.txt" && env LANG=de_DE.UTF-8 LC_ALL=C locale -k '
            'decimal_point > precedence.txt && grep -Fx \'decimal_point="."\' precedence.txt && '
            'fresh "$w/category.txt" && env -u LC_ALL LANG=en_US.UTF-8 LC_NUMERIC=de_DE.UTF-8 '
            'locale -k decimal_point > category.txt && grep -Fx \'decimal_point=","\' category.txt',
            'here && fresh "$w/after.txt" && locale > after.txt && cmp parent.txt after.txt && '
            'sha256sum -c default.sha'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-locale-scope.XXXXXX") && cd "$w" && umask 077; '
                'here() { case "$w" in "$HOME"/foundation-locale-scope.??????) ;; *) return 19;; '
                'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a '
                '"$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; '
                'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && pwd',
                'here && env LANG=de_DE.UTF-8 LC_ALL=C locale -k decimal_point',
                'here && fresh "$w/parent.txt" && fresh "$w/default.sha" && locale > parent.txt && '
                'sha256sum /etc/locale.conf > default.sha && locale -a && locale charmap',
                'here && fresh "$w/precedence.txt" && env LANG=de_DE.UTF-8 LC_ALL=C locale -k '
                'decimal_point > precedence.txt && grep -Fx \'decimal_point="."\' precedence.txt '
                '&& fresh "$w/category.txt" && env -u LC_ALL LANG=en_US.UTF-8 '
                'LC_NUMERIC=de_DE.UTF-8 locale -k decimal_point > category.txt && grep -Fx '
                '\'decimal_point=","\' category.txt',
                'here && fresh "$w/after.txt" && locale > after.txt && cmp parent.txt after.txt && '
                'sha256sum -c default.sha'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-locale-formats',
              'content_version': '1.0.0',
              'title': 'Compare localized formats without corrupting data',
              'goal': 'Use prepared de_DE.UTF-8 and en_US.UTF-8 for numeric/time categories, '
                      'inspect monetary locale metadata and explicit C sorting.',
              'challenge': 'Choose display categories and machine-processing locale independently '
                           'for a supplied small dataset. Retain actual outputs/statuses and '
                           'preserve originals; report reasoning through self-review, not a score.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-locale-formats.XXXXXX") && cd '
                                    '"$w" && umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-locale-formats.??????) ;; *) return 19;; '
                                    'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L '
                                    '"$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" '
                                    '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                                    'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && '
                                    'test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h '
                                    '"$1")" = learner:600:1; }; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                         'explanation': 'Record this unique guest-only workspace. On Resume '
                                        're-establish the recorded path/definitions; never '
                                        'overwrite another exercise.',
                         'expected': 'Private learner-owned700 directory and observed1GiB free '
                                     'admission.'},
                        {'command': 'here && locale -a && env LC_ALL=de_DE.UTF-8 locale -k '
                                    'decimal_point thousands_sep currency_symbol && env '
                                    'LC_ALL=en_US.UTF-8 locale -k decimal_point currency_symbol && '
                                    'env LC_ALL=de_DE.UTF-8 date -d "2026-01-01 UTC" +%A && env '
                                    'LC_ALL=en_US.UTF-8 date -d "2026-01-01 UTC" +%A',
                         'explanation': 'Inspect actual categories and a fixed instant rather than '
                                        'locale assumptions. Monetary metadata is inspected, not a '
                                        'money arithmetic exercise.',
                         'expected': 'German comma/Donnerstag; English dot/Thursday.'},
                        {'command': 'here && fresh "$w/source.txt" && printf "z\\n\\303\\244\\n" > '
                                    'source.txt && fresh "$w/source.sha" && sha256sum source.txt > '
                                    'source.sha && fresh "$w/c.txt" && fresh "$w/de.txt" && env '
                                    'LC_ALL=C sort source.txt > c.txt && env LC_ALL=de_DE.UTF-8 '
                                    'sort source.txt > de.txt && cat c.txt de.txt && sha256sum -c '
                                    'source.sha',
                         'explanation': 'Keep original UTF-8 bytes. A machine-processing locale '
                                        'should be explicit; collation depends on dataset and '
                                        'locale implementation.',
                         'expected': 'Actual C versus German ordering retained without rewriting '
                                     'source.'}],
              'hints': ['Do not assume a localized decimal comma is a TSV separator or that every '
                        'locale orders every sample differently.',
                        'Choose command scope deliberately; compare known bytes and actual '
                        'statuses, not only a successful-looking display.',
                        'Retain before evidence; refuse collisions and restore exact policy state '
                        'before leaving. Guest root can bypass guest-side guards.'],
              'review': ['I demonstrated the selected mode’s actual observations and retained an '
                         'incorrect or incomplete case.',
                         'I preserved originals and can explain the reasoning and limitations; '
                         'this records self-review, not automatic assessment.',
                         'I restored any changed default/zone and retained the exact workspace '
                         'without touching unrelated files.'],
              'coverage': 'LPIC-1 active v5.0 partial 107.3 non-English localization and LC_*; '
                          '103.2 sorting: reinforcement. No complete-objective coverage or '
                          'endorsement.'},
  'entry': {'id': 'real-linux-foundation-locale-formats',
            'resource': 'real-linux-foundation-locale-formats.json',
            'description': 'Use prepared de_DE.UTF-8 and en_US.UTF-8 for numeric/time categories, '
                           'inspect monetary locale metadata and explicit C sorting.',
            'objectives': ['107.3 non-English localization and LC_*',
                           '103.2 sorting: reinforcement'],
            'troubleshooting': ['Do not assume a localized decimal comma is a TSV separator or '
                                'that every locale orders every sample differently.',
                                'A missing tool/default or unexpected collision is a refusal, not '
                                'permission to change image/PAM/packages. Retain the failure and '
                                'Reset if exact rollback cannot be proved.'],
            'cleanup': ['Stay inside the recorded private workspace; retain its original and '
                        'result files as evidence. Do not recursively delete or remove unknown '
                        'members.',
                        'If default locale/timezone changed, perform only the displayed guarded '
                        'exact rollback before leaving. Keep root snapshot evidence; no '
                        'authentication, clock, RTC, NTP or host changes.',
                        'Reset retains disk generations. Resume boots the same disk, not RAM, '
                        'shell variables or processes. Re-enter only recorded path/function '
                        'definitions.'],
            'materials': ['For either mode, this is the non-repair workspace setup: w=$(mktemp -d '
                          '"$HOME/foundation-locale-formats.XXXXXX") && cd "$w" && umask 077; '
                          'here() { case "$w" in "$HOME"/foundation-locale-formats.??????) ;; *) '
                          'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L '
                          '"$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && '
                          'test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 '
                          '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                          'On Resume set w to its recorded exact path, cd there and restore the '
                          'definitions; do not run mktemp or recreate retained fixtures. '
                          'Definitions: here() { case "$w" in '
                          '"$HOME"/foundation-locale-formats.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = '
                          '"$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { here && test '
                          '"${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test "$(stat -c '
                          '%U:%a:%h "$1")" = learner:600:1; }',
                          'Challenge source fixture (not repair): here && fresh "$w/source.txt" && '
                          'printf "z\\n\\303\\244\\n" > source.txt. Required localized display: '
                          'German decimal point, weekday Thursday in German for2026-01-01 UTC; '
                          'currency metadata inspected. Required machine sort: explicit LC_ALL=C, '
                          'original UTF8 bytes retained. Compare German sorting without assuming '
                          'every dataset differs.'],
            'observations': ['Actual locale availability, category output, retained byte-level '
                             'input/output and tested sorting interpretation.',
                             'Observed command/status/byte outcomes, not automatically graded '
                             'reasoning.'],
            'questions': ['Which evidence proves the specific outcome, and what does it not '
                          'establish?',
                          'Do not assume a localized decimal comma is a TSV separator or that '
                          'every locale orders every sample differently.'],
            'limitations': ['Real offline guest, not supplied snapshots. One worker; <=64KiB input '
                            'and small fixed-fixture expected outputs below256KiB (cooperative '
                            'accounting, not a kernel aggregate quota). Each iconv/xz command10s '
                            'plus1s grace and64MiB xz cap; no large arbitrary streams. Free-space '
                            'admission is not a quota or guaranteed reserve. Guest root can '
                            'override guest-side limits.',
                            'No clock/RTC/NTP writes, networking, new credentials, source '
                            'replacement, automatic grading or public-release claim. Physical '
                            'keyboard/accessibility checks remain separate.']},
  'resource_sha256': '8e7afc1779b9153241c3d4031d504046efe364b6cd8d7d30d9469f7bc4abda39',
  'entry_sha256': 'fbaa55d147c7bd4c5cd34883d7d3d94430e0e986eabe43b3368e81613b5aeda1',
  'learn': ['w=$(mktemp -d "$HOME/foundation-locale-formats.XXXXXX") && cd "$w" && umask 077; '
            'here() { case "$w" in "$HOME"/foundation-locale-formats.??????) ;; *) return 19;; '
            'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath '
            '-e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
            'learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! '
            '-L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L '
            '"$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 '
            '--output=avail / | tail -1)" -ge 1073741824 && pwd',
            'here && locale -a && env LC_ALL=de_DE.UTF-8 locale -k decimal_point thousands_sep '
            'currency_symbol && env LC_ALL=en_US.UTF-8 locale -k decimal_point currency_symbol && '
            'env LC_ALL=de_DE.UTF-8 date -d "2026-01-01 UTC" +%A && env LC_ALL=en_US.UTF-8 date -d '
            '"2026-01-01 UTC" +%A',
            'here && fresh "$w/source.txt" && printf "z\\n\\303\\244\\n" > source.txt && fresh '
            '"$w/source.sha" && sha256sum source.txt > source.sha && fresh "$w/c.txt" && fresh '
            '"$w/de.txt" && env LC_ALL=C sort source.txt > c.txt && env LC_ALL=de_DE.UTF-8 sort '
            'source.txt > de.txt && cat c.txt de.txt && sha256sum -c source.sha'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-locale-formats.XXXXXX") && cd "$w" && umask 077; '
                'here() { case "$w" in "$HOME"/foundation-locale-formats.??????) ;; *) return 19;; '
                'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a '
                '"$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; '
                'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && pwd',
                'here && fresh "$w/source.txt" && printf "z\\n\\303\\244\\n" > source.txt',
                'here && locale -a && env LC_ALL=de_DE.UTF-8 locale -k decimal_point thousands_sep '
                'currency_symbol && env LC_ALL=en_US.UTF-8 locale -k decimal_point currency_symbol '
                '&& env LC_ALL=de_DE.UTF-8 date -d "2026-01-01 UTC" +%A && env LC_ALL=en_US.UTF-8 '
                'date -d "2026-01-01 UTC" +%A',
                'here && regular "$w/source.txt" && fresh "$w/source.sha" && sha256sum source.txt '
                '> source.sha && fresh "$w/c.txt" && fresh "$w/de.txt" && env LC_ALL=C sort '
                'source.txt > c.txt && env LC_ALL=de_DE.UTF-8 sort source.txt > de.txt && cat '
                'c.txt de.txt && sha256sum -c source.sha'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-encoding',
              'content_version': '1.0.0',
              'title': 'Convert text strictly and preserve a recovery path',
              'goal': 'Distinguish UTF-8 bytes/characters from ASCII and ISO-8859-1; detect '
                      'invalid or unrepresentable input.',
              'challenge': 'Identify the correct source encoding, recover an independently '
                           'specified payload, and explain a rejected conversion. Retain actual '
                           'outputs/statuses and preserve originals; report reasoning through '
                           'self-review, not a score.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-encoding.XXXXXX") && cd "$w" '
                                    '&& umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-encoding.??????) ;; *) return 19;; esac; '
                                    'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                                    'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
                                    'here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L '
                                    '"$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                                    '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = '
                                    'learner:600:1; }; here && test "$(df -B1 --output=avail / | '
                                    'tail -1)" -ge 1073741824 && pwd',
                         'explanation': 'Record this unique guest-only workspace. On Resume '
                                        're-establish the recorded path/definitions; never '
                                        'overwrite another exercise.',
                         'expected': 'Private learner-owned700 directory and observed1GiB free '
                                     'admission.'},
                        {'command': 'here && fresh "$w/utf8.txt" && fresh "$w/source.sha" && '
                                    'printf "caf\\303\\251\\n" > utf8.txt && sha256sum utf8.txt > '
                                    'source.sha && wc -c utf8.txt && env LC_ALL=en_US.UTF-8 wc -m '
                                    'utf8.txt && od -An -tx1 utf8.txt',
                         'explanation': 'This fixed original is café plus newline: six bytes, five '
                                        'Unicode characters in UTF-8. ASCII is a subset, not a '
                                        'synonym.',
                         'expected': 'Actual byte/character counts and independent octets.'},
                        {'command': 'here && fresh "$w/latin1.txt" && fresh "$w/roundtrip.txt" && '
                                    'fresh "$w/expected-latin1.txt" && timeout -k 1s 10s iconv -f '
                                    'UTF-8 -t ISO-8859-1 utf8.txt > latin1.txt && printf '
                                    '"caf\\351\\n" > expected-latin1.txt && cmp '
                                    'expected-latin1.txt latin1.txt && timeout -k 1s 10s iconv -f '
                                    'ISO-8859-1 -t UTF-8 latin1.txt > roundtrip.txt && cmp '
                                    'utf8.txt roundtrip.txt',
                         'explanation': 'Convert to a separate path with known input encoding, '
                                        'then compare independent bytes and round-trip. Wrong '
                                        'source declarations can produce valid wrong text.',
                         'expected': 'Exact expected Latin-1 and restored UTF-8.'},
                        {'command': 'foundation_step() { here && fresh "$w/ascii-partial.txt" && '
                                    'fresh "$w/ascii-error.txt" || return 19; if timeout -k 1s 10s '
                                    'iconv -f UTF-8 -t ASCII utf8.txt > ascii-partial.txt 2> '
                                    'ascii-error.txt; then return 1; else test $? = 1 && test -s '
                                    'ascii-error.txt && sha256sum -c source.sha; fi; }; '
                                    'foundation_step',
                         'explanation': 'ASCII cannot represent this é. Retain error and any '
                                        'partial output; do not use //IGNORE to claim a lossless '
                                        'repair.',
                         'expected': 'Actual refusal, original preserved.'}],
              'hints': ['Wrong declared source can yield valid but wrong text; '
                        '//IGNORE/transliteration are not permitted repairs; nonzero status may '
                        'leave partial output.',
                        'Choose command scope deliberately; compare known bytes and actual '
                        'statuses, not only a successful-looking display.',
                        'Retain before evidence; refuse collisions and restore exact policy state '
                        'before leaving. Guest root can bypass guest-side guards.'],
              'review': ['I demonstrated the selected mode’s actual observations and retained an '
                         'incorrect or incomplete case.',
                         'I preserved originals and can explain the reasoning and limitations; '
                         'this records self-review, not automatic assessment.',
                         'I restored any changed default/zone and retained the exact workspace '
                         'without touching unrelated files.'],
              'coverage': 'LPIC-1 active v5.0 partial 107.3 iconv/encoding terms. No '
                          'complete-objective coverage or endorsement.'},
  'entry': {'id': 'real-linux-foundation-encoding',
            'resource': 'real-linux-foundation-encoding.json',
            'description': 'Distinguish UTF-8 bytes/characters from ASCII and ISO-8859-1; detect '
                           'invalid or unrepresentable input.',
            'objectives': ['107.3 iconv/encoding terms'],
            'troubleshooting': ['Wrong declared source can yield valid but wrong text; '
                                '//IGNORE/transliteration are not permitted repairs; nonzero '
                                'status may leave partial output.',
                                'A missing tool/default or unexpected collision is a refusal, not '
                                'permission to change image/PAM/packages. Retain the failure and '
                                'Reset if exact rollback cannot be proved.'],
            'cleanup': ['Stay inside the recorded private workspace; retain its original and '
                        'result files as evidence. Do not recursively delete or remove unknown '
                        'members.',
                        'If default locale/timezone changed, perform only the displayed guarded '
                        'exact rollback before leaving. Keep root snapshot evidence; no '
                        'authentication, clock, RTC, NTP or host changes.',
                        'Reset retains disk generations. Resume boots the same disk, not RAM, '
                        'shell variables or processes. Re-enter only recorded path/function '
                        'definitions.'],
            'materials': ['For either mode, this is the non-repair workspace setup: w=$(mktemp -d '
                          '"$HOME/foundation-encoding.XXXXXX") && cd "$w" && umask 077; here() { '
                          'case "$w" in "$HOME"/foundation-encoding.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 '
                          '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                          'On Resume set w to its recorded exact path, cd there and restore the '
                          'definitions; do not run mktemp or recreate retained fixtures. '
                          'Definitions: here() { case "$w" in "$HOME"/foundation-encoding.??????) '
                          ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                          'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" '
                          '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here '
                          '&& test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
                          'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L '
                          '"$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }',
                          'Challenge fixed original, not repair: here && fresh "$w/utf8.txt" && '
                          'printf "caf\\303\\251\\n" > utf8.txt. Known UTF8 octets63 61 66 c3 a9 '
                          '0a; expected Latin1 63 61 66 e9 0a. Convert strictly to separate paths '
                          'and show ASCII refusal/partial output without altering source.'],
            'observations': ['Input hashes, byte counts/od, status/error, independent expected '
                             'bytes and successful round-trip where representable.',
                             'Observed command/status/byte outcomes, not automatically graded '
                             'reasoning.'],
            'questions': ['Which evidence proves the specific outcome, and what does it not '
                          'establish?',
                          'Wrong declared source can yield valid but wrong text; '
                          '//IGNORE/transliteration are not permitted repairs; nonzero status may '
                          'leave partial output.'],
            'limitations': ['Real offline guest, not supplied snapshots. One worker; <=64KiB input '
                            'and small fixed-fixture expected outputs below256KiB (cooperative '
                            'accounting, not a kernel aggregate quota). Each iconv/xz command10s '
                            'plus1s grace and64MiB xz cap; no large arbitrary streams. Free-space '
                            'admission is not a quota or guaranteed reserve. Guest root can '
                            'override guest-side limits.',
                            'No clock/RTC/NTP writes, networking, new credentials, source '
                            'replacement, automatic grading or public-release claim. Physical '
                            'keyboard/accessibility checks remain separate.']},
  'resource_sha256': 'ba55c75059ce032b800bc43715b8c290513d8b55873319c294f2f243a1dfb93c',
  'entry_sha256': '752cc921db01ed5e0e5d487024afa3f5f613241e9e6b5b7ab0f669f83934b114',
  'learn': ['w=$(mktemp -d "$HOME/foundation-encoding.XXXXXX") && cd "$w" && umask 077; here() { '
            'case "$w" in "$HOME"/foundation-encoding.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
            '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 --output=avail '
            '/ | tail -1)" -ge 1073741824 && pwd',
            'here && fresh "$w/utf8.txt" && fresh "$w/source.sha" && printf "caf\\303\\251\\n" > '
            'utf8.txt && sha256sum utf8.txt > source.sha && wc -c utf8.txt && env '
            'LC_ALL=en_US.UTF-8 wc -m utf8.txt && od -An -tx1 utf8.txt',
            'here && fresh "$w/latin1.txt" && fresh "$w/roundtrip.txt" && fresh '
            '"$w/expected-latin1.txt" && timeout -k 1s 10s iconv -f UTF-8 -t ISO-8859-1 utf8.txt > '
            'latin1.txt && printf "caf\\351\\n" > expected-latin1.txt && cmp expected-latin1.txt '
            'latin1.txt && timeout -k 1s 10s iconv -f ISO-8859-1 -t UTF-8 latin1.txt > '
            'roundtrip.txt && cmp utf8.txt roundtrip.txt',
            'foundation_step() { here && fresh "$w/ascii-partial.txt" && fresh '
            '"$w/ascii-error.txt" || return 19; if timeout -k 1s 10s iconv -f UTF-8 -t ASCII '
            'utf8.txt > ascii-partial.txt 2> ascii-error.txt; then return 1; else test $? = 1 && '
            'test -s ascii-error.txt && sha256sum -c source.sha; fi; }; foundation_step'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-encoding.XXXXXX") && cd "$w" && umask 077; here() '
                '{ case "$w" in "$HOME"/foundation-encoding.??????) ;; *) return 19;; esac; test '
                '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e '
                '"$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                'learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test '
                '! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! '
                '-L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df '
                '-B1 --output=avail / | tail -1)" -ge 1073741824 && pwd',
                'here && fresh "$w/utf8.txt" && printf "caf\\303\\251\\n" > utf8.txt',
                'here && regular "$w/utf8.txt" && fresh "$w/source.sha" && sha256sum utf8.txt > '
                'source.sha && wc -c utf8.txt && env LC_ALL=en_US.UTF-8 wc -m utf8.txt && od -An '
                '-tx1 utf8.txt',
                'here && fresh "$w/latin1.txt" && fresh "$w/roundtrip.txt" && fresh '
                '"$w/expected-latin1.txt" && timeout -k 1s 10s iconv -f UTF-8 -t ISO-8859-1 '
                'utf8.txt > latin1.txt && printf "caf\\351\\n" > expected-latin1.txt && cmp '
                'expected-latin1.txt latin1.txt && timeout -k 1s 10s iconv -f ISO-8859-1 -t UTF-8 '
                'latin1.txt > roundtrip.txt && cmp utf8.txt roundtrip.txt',
                'foundation_step() { here && fresh "$w/ascii-partial.txt" && fresh '
                '"$w/ascii-error.txt" || return 19; if timeout -k 1s 10s iconv -f UTF-8 -t ASCII '
                'utf8.txt > ascii-partial.txt 2> ascii-error.txt; then return 1; else test $? = 1 '
                '&& test -s ascii-error.txt && sha256sum -c source.sha; fi; }; foundation_step'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-locale-persistence',
              'content_version': '1.0.0',
              'title': 'Make a guest locale default reversible',
              'goal': 'Distinguish per-command settings from a new guest login default; apply and '
                      'restore one documented locale policy.',
              'challenge': 'Correct one prepared default/category inconsistency and prove '
                           'new-session versus existing-shell behavior. Retain actual '
                           'outputs/statuses and preserve originals; report reasoning through '
                           'self-review, not a score.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-locale-persistence.XXXXXX") '
                                    '&& cd "$w" && umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-locale-persistence.??????) ;; *) return '
                                    '19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! '
                                    '-L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd '
                                    '-P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                                    'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && '
                                    'test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h '
                                    '"$1")" = learner:600:1; }; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                         'explanation': 'Record this unique guest-only workspace. On Resume '
                                        're-establish the recorded path/definitions; never '
                                        'overwrite another exercise.',
                         'expected': 'Private learner-owned700 directory and observed1GiB free '
                                     'admission.'},
                        {'command': 'foundation_step() { here && fresh "$w/locale-before.sha" && '
                                    'fresh "$w/shell-before.txt" && test "$(readlink '
                                    '/etc/default/locale)" = ../locale.conf && test -f '
                                    '/etc/locale.conf && test ! -L /etc/locale.conf && test '
                                    '"$(stat -c %U:%G:%a:%h /etc/locale.conf)" = root:root:644:1 '
                                    '|| return 19; rw=$(sudo mktemp -d /var/tmp/ll-locale.XXXXXX) '
                                    '|| return 19; case "$rw" in /var/tmp/ll-locale.??????) ;; *) '
                                    'return 19;; esac; sudo test ! -e "$rw/before" && sudo test ! '
                                    '-L "$rw/before" && sudo cp -p /etc/locale.conf "$rw/before" '
                                    '&& sudo sha256sum "$rw/before" > "$w/snapshot-before.sha" && '
                                    'sha256sum /etc/locale.conf > locale-before.sha && locale > '
                                    'shell-before.txt && printf "Recorded workspace: %s\\nRoot '
                                    'snapshot: %s\\n" "$w" "$rw"; }; foundation_step',
                         'explanation': 'Write down both exact paths for the fresh login. Preserve '
                                        'the resolved regular target, not an accidentally replaced '
                                        '/etc/default/locale symlink.',
                         'expected': 'Root-only original snapshot and unchanged parent '
                                     'environment.'},
                        {'command': 'here && fresh "$w/locale-change.sha" && fresh '
                                    '"$w/shell-after.txt" && sha256sum -c locale-before.sha && '
                                    'test "$(readlink /etc/default/locale)" = ../locale.conf && '
                                    'test "$(stat -c %U:%G:%a:%h /etc/locale.conf)" = '
                                    'root:root:644:1 && sudo /usr/sbin/update-locale --reset '
                                    'LANG=de_DE.UTF-8 && sha256sum /etc/locale.conf > '
                                    'locale-change.sha && grep -Fx LANG=de_DE.UTF-8 '
                                    '/etc/locale.conf && locale > shell-after.txt && cmp '
                                    'shell-before.txt shell-after.txt',
                         'explanation': 'Change only the approved guest locale default. '
                                        'update-locale writes an unquoted LANG line; this does not '
                                        'modify the already-running shell.',
                         'expected': 'Changed default bytes, unchanged current shell.'},
                        {'command': 'exit',
                         'explanation': 'Log out of only the learner guest console. Getty logs '
                                        'learner in again automatically; this is a new login, not '
                                        'a password/PAM change. Re-enter the recorded w/rw paths '
                                        'and here/fresh/regular definitions before continuing.',
                         'expected': 'Fresh console login, LANG=de_DE.UTF-8 and LC_ALL unset.'},
                        {'command': 'foundation_step() { case "$rw" in /var/tmp/ll-locale.??????) '
                                    ';; *) return 19;; esac; test "$(sudo realpath -e "$rw")" = '
                                    '"$rw" && test "$(sudo stat -c %U:%G:%a "$rw")" = '
                                    'root:root:700 && sudo sha256sum -c "$w/snapshot-before.sha" '
                                    '&& here && test "$LANG" = de_DE.UTF-8 && test -z "${LC_ALL-}" '
                                    '&& test "$(date -d "2026-01-01 UTC" +%A)" = Donnerstag && '
                                    'sha256sum -c locale-change.sha && test "$(readlink '
                                    '/etc/default/locale)" = ../locale.conf && test "$(stat -c '
                                    '%U:%G:%a:%h /etc/locale.conf)" = root:root:644:1 && sudo test '
                                    '-f "$rw/before" && sudo test ! -L "$rw/before" && test '
                                    '"$(sudo stat -c %U:%G:%a:%h "$rw/before")" = root:root:644:1 '
                                    '|| return 19; sudo cp -- "$rw/before" /etc/locale.conf && '
                                    'sha256sum -c locale-before.sha && test "$(readlink '
                                    '/etc/default/locale)" = ../locale.conf; }; foundation_step',
                         'explanation': 'Verify actual new-login values before byte-exact '
                                        'rollback. Refuse unexpected target/snapshot changes. Exit '
                                        'once more to observe the original default; retained paths '
                                        'remain evidence.',
                         'expected': 'Original bytes/mode/link restored; a later login uses '
                                     'original locale.'}],
              'hints': ['Editing LANG in the current shell is not persistent; LC_ALL can conceal '
                        'the changed default.',
                        'Choose command scope deliberately; compare known bytes and actual '
                        'statuses, not only a successful-looking display.',
                        'Retain before evidence; refuse collisions and restore exact policy state '
                        'before leaving. Guest root can bypass guest-side guards.'],
              'review': ['I demonstrated the selected mode’s actual observations and retained an '
                         'incorrect or incomplete case.',
                         'I preserved originals and can explain the reasoning and limitations; '
                         'this records self-review, not automatic assessment.',
                         'I restored any changed default/zone and retained the exact workspace '
                         'without touching unrelated files.'],
              'coverage': 'LPIC-1 active v5.0 partial 107.3 locale configuration; 105.1 '
                          'environment: reinforcement. No complete-objective coverage or '
                          'endorsement.'},
  'entry': {'id': 'real-linux-foundation-locale-persistence',
            'resource': 'real-linux-foundation-locale-persistence.json',
            'description': 'Distinguish per-command settings from a new guest login default; apply '
                           'and restore one documented locale policy.',
            'objectives': ['107.3 locale configuration', '105.1 environment: reinforcement'],
            'troubleshooting': ['Editing LANG in the current shell is not persistent; LC_ALL can '
                                'conceal the changed default.',
                                'A missing tool/default or unexpected collision is a refusal, not '
                                'permission to change image/PAM/packages. Retain the failure and '
                                'Reset if exact rollback cannot be proved.'],
            'cleanup': ['Stay inside the recorded private workspace; retain its original and '
                        'result files as evidence. Do not recursively delete or remove unknown '
                        'members.',
                        'If default locale/timezone changed, perform only the displayed guarded '
                        'exact rollback before leaving. Keep root snapshot evidence; no '
                        'authentication, clock, RTC, NTP or host changes.',
                        'Reset retains disk generations. Resume boots the same disk, not RAM, '
                        'shell variables or processes. Re-enter only recorded path/function '
                        'definitions.'],
            'materials': ['For either mode, this is the non-repair workspace setup: w=$(mktemp -d '
                          '"$HOME/foundation-locale-persistence.XXXXXX") && cd "$w" && umask 077; '
                          'here() { case "$w" in "$HOME"/foundation-locale-persistence.??????) ;; '
                          '*) return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! '
                          '-L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" '
                          '&& test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && '
                          'test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() '
                          '{ here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && '
                          'test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df '
                          '-B1 --output=avail / | tail -1)" -ge 1073741824 && pwd',
                          'On Resume set w to its recorded exact path, cd there and restore the '
                          'definitions; do not run mktemp or recreate retained fixtures. '
                          'Definitions: here() { case "$w" in '
                          '"$HOME"/foundation-locale-persistence.??????) ;; *) return 19;; esac; '
                          'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = '
                          '"$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { here && test '
                          '"${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test "$(stat -c '
                          '%U:%a:%h "$1")" = learner:600:1; }',
                          'Challenge initial policy and protected snapshot (not repair): '
                          'foundation_step() { here && fresh "$w/locale-before.sha" && fresh '
                          '"$w/shell-before.txt" && test "$(readlink /etc/default/locale)" = '
                          '../locale.conf && test -f /etc/locale.conf && test ! -L '
                          '/etc/locale.conf && test "$(stat -c %U:%G:%a:%h /etc/locale.conf)" = '
                          'root:root:644:1 || return 19; rw=$(sudo mktemp -d '
                          '/var/tmp/ll-locale.XXXXXX) || return 19; case "$rw" in '
                          '/var/tmp/ll-locale.??????) ;; *) return 19;; esac; sudo test ! -e '
                          '"$rw/before" && sudo test ! -L "$rw/before" && sudo cp -p '
                          '/etc/locale.conf "$rw/before" && sudo sha256sum "$rw/before" > '
                          '"$w/snapshot-before.sha" && sha256sum /etc/locale.conf > '
                          'locale-before.sha && locale > shell-before.txt && printf "Recorded '
                          'workspace: %s\\nRoot snapshot: %s\\n" "$w" "$rw"; }; foundation_step '
                          'Required default LANG=de_DE.UTF-8 with no persisted LC_ALL, existing '
                          'shell unchanged, actual fresh login showing German. Restore exact '
                          'original after documenting fresh-login behavior; record w/rw before '
                          'logout and restore the displayed definitions.'],
            'observations': ['Protected before copy, exact changed fields, real fresh-session '
                             'locale and successful byte/mode/owner rollback.',
                             'Observed command/status/byte outcomes, not automatically graded '
                             'reasoning.'],
            'questions': ['Which evidence proves the specific outcome, and what does it not '
                          'establish?',
                          'Editing LANG in the current shell is not persistent; LC_ALL can conceal '
                          'the changed default.'],
            'limitations': ['Real offline guest, not supplied snapshots. One worker; <=64KiB input '
                            'and small fixed-fixture expected outputs below256KiB (cooperative '
                            'accounting, not a kernel aggregate quota). Each iconv/xz command10s '
                            'plus1s grace and64MiB xz cap; no large arbitrary streams. Free-space '
                            'admission is not a quota or guaranteed reserve. Guest root can '
                            'override guest-side limits.',
                            'No clock/RTC/NTP writes, networking, new credentials, source '
                            'replacement, automatic grading or public-release claim. Physical '
                            'keyboard/accessibility checks remain separate.']},
  'resource_sha256': 'a8db8163de09afcb433961c15fbe961dadaf495bd0c9cd44da7660d1baa8a345',
  'entry_sha256': 'fe501236c19ff9076ef29db3150a379adbf8ab9dd6be4d66653f4026ff9ff605',
  'learn': ['w=$(mktemp -d "$HOME/foundation-locale-persistence.XXXXXX") && cd "$w" && umask 077; '
            'here() { case "$w" in "$HOME"/foundation-locale-persistence.??????) ;; *) return 19;; '
            'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath '
            '-e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
            'learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! '
            '-L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L '
            '"$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 '
            '--output=avail / | tail -1)" -ge 1073741824 && pwd',
            'foundation_step() { here && fresh "$w/locale-before.sha" && fresh '
            '"$w/shell-before.txt" && test "$(readlink /etc/default/locale)" = ../locale.conf && '
            'test -f /etc/locale.conf && test ! -L /etc/locale.conf && test "$(stat -c %U:%G:%a:%h '
            '/etc/locale.conf)" = root:root:644:1 || return 19; rw=$(sudo mktemp -d '
            '/var/tmp/ll-locale.XXXXXX) || return 19; case "$rw" in /var/tmp/ll-locale.??????) ;; '
            '*) return 19;; esac; sudo test ! -e "$rw/before" && sudo test ! -L "$rw/before" && '
            'sudo cp -p /etc/locale.conf "$rw/before" && sudo sha256sum "$rw/before" > '
            '"$w/snapshot-before.sha" && sha256sum /etc/locale.conf > locale-before.sha && locale '
            '> shell-before.txt && printf "Recorded workspace: %s\\nRoot snapshot: %s\\n" "$w" '
            '"$rw"; }; foundation_step',
            'here && fresh "$w/locale-change.sha" && fresh "$w/shell-after.txt" && sha256sum -c '
            'locale-before.sha && test "$(readlink /etc/default/locale)" = ../locale.conf && test '
            '"$(stat -c %U:%G:%a:%h /etc/locale.conf)" = root:root:644:1 && sudo '
            '/usr/sbin/update-locale --reset LANG=de_DE.UTF-8 && sha256sum /etc/locale.conf > '
            'locale-change.sha && grep -Fx LANG=de_DE.UTF-8 /etc/locale.conf && locale > '
            'shell-after.txt && cmp shell-before.txt shell-after.txt',
            'exit',
            'foundation_step() { case "$rw" in /var/tmp/ll-locale.??????) ;; *) return 19;; esac; '
            'test "$(sudo realpath -e "$rw")" = "$rw" && test "$(sudo stat -c %U:%G:%a "$rw")" = '
            'root:root:700 && sudo sha256sum -c "$w/snapshot-before.sha" && here && test "$LANG" = '
            'de_DE.UTF-8 && test -z "${LC_ALL-}" && test "$(date -d "2026-01-01 UTC" +%A)" = '
            'Donnerstag && sha256sum -c locale-change.sha && test "$(readlink '
            '/etc/default/locale)" = ../locale.conf && test "$(stat -c %U:%G:%a:%h '
            '/etc/locale.conf)" = root:root:644:1 && sudo test -f "$rw/before" && sudo test ! -L '
            '"$rw/before" && test "$(sudo stat -c %U:%G:%a:%h "$rw/before")" = root:root:644:1 || '
            'return 19; sudo cp -- "$rw/before" /etc/locale.conf && sha256sum -c locale-before.sha '
            '&& test "$(readlink /etc/default/locale)" = ../locale.conf; }; foundation_step'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-locale-persistence.XXXXXX") && cd "$w" && umask '
                '077; here() { case "$w" in "$HOME"/foundation-locale-persistence.??????) ;; *) '
                'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c '
                '%U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! '
                '-e "$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test '
                '-f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; '
                'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && pwd',
                'foundation_step() { here && fresh "$w/locale-before.sha" && fresh '
                '"$w/shell-before.txt" && test "$(readlink /etc/default/locale)" = ../locale.conf '
                '&& test -f /etc/locale.conf && test ! -L /etc/locale.conf && test "$(stat -c '
                '%U:%G:%a:%h /etc/locale.conf)" = root:root:644:1 || return 19; rw=$(sudo mktemp '
                '-d /var/tmp/ll-locale.XXXXXX) || return 19; case "$rw" in '
                '/var/tmp/ll-locale.??????) ;; *) return 19;; esac; sudo test ! -e "$rw/before" && '
                'sudo test ! -L "$rw/before" && sudo cp -p /etc/locale.conf "$rw/before" && sudo '
                'sha256sum "$rw/before" > "$w/snapshot-before.sha" && sha256sum /etc/locale.conf > '
                'locale-before.sha && locale > shell-before.txt && printf "Recorded workspace: '
                '%s\\nRoot snapshot: %s\\n" "$w" "$rw"; }; foundation_step',
                'here && fresh "$w/locale-change.sha" && fresh "$w/shell-after.txt" && sha256sum '
                '-c locale-before.sha && test "$(readlink /etc/default/locale)" = ../locale.conf '
                '&& test "$(stat -c %U:%G:%a:%h /etc/locale.conf)" = root:root:644:1 && sudo '
                '/usr/sbin/update-locale --reset LANG=de_DE.UTF-8 && sha256sum /etc/locale.conf > '
                'locale-change.sha && grep -Fx LANG=de_DE.UTF-8 /etc/locale.conf && locale > '
                'shell-after.txt && cmp shell-before.txt shell-after.txt',
                'exit',
                'foundation_step() { case "$rw" in /var/tmp/ll-locale.??????) ;; *) return 19;; '
                'esac; test "$(sudo realpath -e "$rw")" = "$rw" && test "$(sudo stat -c %U:%G:%a '
                '"$rw")" = root:root:700 && sudo sha256sum -c "$w/snapshot-before.sha" && here && '
                'test "$LANG" = de_DE.UTF-8 && test -z "${LC_ALL-}" && test "$(date -d "2026-01-01 '
                'UTC" +%A)" = Donnerstag && sha256sum -c locale-change.sha && test "$(readlink '
                '/etc/default/locale)" = ../locale.conf && test "$(stat -c %U:%G:%a:%h '
                '/etc/locale.conf)" = root:root:644:1 && sudo test -f "$rw/before" && sudo test ! '
                '-L "$rw/before" && test "$(sudo stat -c %U:%G:%a:%h "$rw/before")" = '
                'root:root:644:1 || return 19; sudo cp -- "$rw/before" /etc/locale.conf && '
                'sha256sum -c locale-before.sha && test "$(readlink /etc/default/locale)" = '
                '../locale.conf; }; foundation_step'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-timezones',
              'content_version': '1.0.0',
              'title': 'Interpret timezones without changing the clock',
              'goal': 'Distinguish UTC instants, local display and DST; configure and restore '
                      'guest timezone while leaving clock/NTP controls untouched.',
              'challenge': 'Resolve two ambiguous-looking log displays, choose the requested guest '
                           'zone, and demonstrate fixed-instant equivalence plus live elapsed-time '
                           'continuity without setting the clock. Retain actual outputs/statuses '
                           'and preserve originals; report reasoning through self-review, not a '
                           'score.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-timezones.XXXXXX") && cd "$w" '
                                    '&& umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-timezones.??????) ;; *) return 19;; esac; '
                                    'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                                    'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
                                    'here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L '
                                    '"$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                                    '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = '
                                    'learner:600:1; }; here && test "$(df -B1 --output=avail / | '
                                    'tail -1)" -ge 1073741824 && pwd',
                         'explanation': 'Record this unique guest-only workspace. On Resume '
                                        're-establish the recorded path/definitions; never '
                                        'overwrite another exercise.',
                         'expected': 'Private learner-owned700 directory and observed1GiB free '
                                     'admission.'},
                        {'command': 'here && fresh "$w/time-context.txt" && fresh '
                                    '"$w/localtime-before.txt" && timedatectl > time-context.txt '
                                    '&& test -L /etc/localtime && readlink /etc/localtime > '
                                    'localtime-before.txt && test "$(cat localtime-before.txt)" = '
                                    '/usr/share/zoneinfo/Etc/UTC && printf "winter\\n" && env '
                                    'TZ=Europe/Berlin date -d "2026-01-01 12:00:00 UTC" "+%F %T '
                                    '%z" && printf "summer\\n" && env TZ=Europe/Berlin date -d '
                                    '"2026-07-01 12:00:00 UTC" "+%F %T %z"',
                         'explanation': 'Inspect this pinned UTC guest and fixed winter/summer '
                                        'instants. Display offsets are not a synchronization '
                                        'result.',
                         'expected': 'Berlin winter13:00+0100, summer14:00+0200; original absolute '
                                     'UTC link.'},
                        {'command': 'here && fresh "$w/epoch-before.txt" && fresh '
                                    '"$w/zone-changed.txt" && fresh "$w/epoch-after.txt" && test '
                                    '"$(readlink /etc/localtime)" = "$(cat localtime-before.txt)" '
                                    '&& date +%s > epoch-before.txt && sudo timedatectl '
                                    'set-timezone Europe/Berlin && test "$(readlink -f '
                                    '/etc/localtime)" = /usr/share/zoneinfo/Europe/Berlin && '
                                    'readlink /etc/localtime > zone-changed.txt && date "+%F %T '
                                    '%z" && date +%s > epoch-after.txt && test "$(cat '
                                    'epoch-after.txt)" -ge "$(cat epoch-before.txt)"',
                         'explanation': 'Set only guest timezone, not clock/RTC/NTP. Epoch '
                                        'continuity plus fixed instants explains display versus '
                                        'instant; this is not time-sync practice.',
                         'expected': 'Zone display changed while epoch advances normally.'},
                        {'command': 'here && test -L /etc/localtime && test "$(readlink '
                                    '/etc/localtime)" = "$(cat zone-changed.txt)" && test "$(cat '
                                    'localtime-before.txt)" = /usr/share/zoneinfo/Etc/UTC && sudo '
                                    'ln -sfn -- /usr/share/zoneinfo/Etc/UTC /etc/localtime && test '
                                    '"$(readlink /etc/localtime)" = "$(cat localtime-before.txt)" '
                                    '&& timedatectl',
                         'explanation': 'Restore the exact original absolute link after validating '
                                        'the known changed link. set-timezone alone can restore '
                                        'semantics but create a relative link; record the '
                                        'distinction.',
                         'expected': 'Exact original link restored; no clock-writing commands.'}],
              'hints': ['A zone abbreviation is not a globally unique zone; TZ/date display is not '
                        'NTP synchronization or setting the system/RTC clock.',
                        'Choose command scope deliberately; compare known bytes and actual '
                        'statuses, not only a successful-looking display.',
                        'Retain before evidence; refuse collisions and restore exact policy state '
                        'before leaving. Guest root can bypass guest-side guards.'],
              'review': ['I demonstrated the selected mode’s actual observations and retained an '
                         'incorrect or incomplete case.',
                         'I preserved originals and can explain the reasoning and limitations; '
                         'this records self-review, not automatic assessment.',
                         'I restored any changed default/zone and retained the exact workspace '
                         'without touching unrelated files.'],
              'coverage': 'LPIC-1 active v5.0 partial 107.3 timezone configuration/TZ; 108.1 '
                          'timezone subskill only. No complete-objective coverage or endorsement.'},
  'entry': {'id': 'real-linux-foundation-timezones',
            'resource': 'real-linux-foundation-timezones.json',
            'description': 'Distinguish UTC instants, local display and DST; configure and restore '
                           'guest timezone while leaving clock/NTP controls untouched.',
            'objectives': ['107.3 timezone configuration/TZ', '108.1 timezone subskill only'],
            'troubleshooting': ['A zone abbreviation is not a globally unique zone; TZ/date '
                                'display is not NTP synchronization or setting the system/RTC '
                                'clock.',
                                'A missing tool/default or unexpected collision is a refusal, not '
                                'permission to change image/PAM/packages. Retain the failure and '
                                'Reset if exact rollback cannot be proved.'],
            'cleanup': ['Stay inside the recorded private workspace; retain its original and '
                        'result files as evidence. Do not recursively delete or remove unknown '
                        'members.',
                        'If default locale/timezone changed, perform only the displayed guarded '
                        'exact rollback before leaving. Keep root snapshot evidence; no '
                        'authentication, clock, RTC, NTP or host changes.',
                        'Reset retains disk generations. Resume boots the same disk, not RAM, '
                        'shell variables or processes. Re-enter only recorded path/function '
                        'definitions.'],
            'materials': ['For either mode, this is the non-repair workspace setup: w=$(mktemp -d '
                          '"$HOME/foundation-timezones.XXXXXX") && cd "$w" && umask 077; here() { '
                          'case "$w" in "$HOME"/foundation-timezones.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 '
                          '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                          'On Resume set w to its recorded exact path, cd there and restore the '
                          'definitions; do not run mktemp or recreate retained fixtures. '
                          'Definitions: here() { case "$w" in "$HOME"/foundation-timezones.??????) '
                          ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && '
                          'test ! -L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" '
                          '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here '
                          '&& test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
                          'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L '
                          '"$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }',
                          'Challenge evidence: two UTC instants2026-01-01 12:00:00 and2026-07-01 '
                          '12:00:00. Requested guest zone Europe/Berlin; expected local '
                          'times13:00+0100 and14:00+0200. Snapshot original absolute Etc/UTC '
                          'localtime link and demonstrate epoch continuity. Change only timezone '
                          'then restore exact original link; no time/NTP/RTC writes.'],
            'observations': ['Fixed-instant offsets, original/final localtime link or bytes, '
                             'monotonic/epoch observations, timedatectl fields, rollback.',
                             'Observed command/status/byte outcomes, not automatically graded '
                             'reasoning.'],
            'questions': ['Which evidence proves the specific outcome, and what does it not '
                          'establish?',
                          'A zone abbreviation is not a globally unique zone; TZ/date display is '
                          'not NTP synchronization or setting the system/RTC clock.'],
            'limitations': ['Real offline guest, not supplied snapshots. One worker; <=64KiB input '
                            'and small fixed-fixture expected outputs below256KiB (cooperative '
                            'accounting, not a kernel aggregate quota). Each iconv/xz command10s '
                            'plus1s grace and64MiB xz cap; no large arbitrary streams. Free-space '
                            'admission is not a quota or guaranteed reserve. Guest root can '
                            'override guest-side limits.',
                            'No clock/RTC/NTP writes, networking, new credentials, source '
                            'replacement, automatic grading or public-release claim. Physical '
                            'keyboard/accessibility checks remain separate.']},
  'resource_sha256': '01938eb1861c9f226c460abe3c7fe342ca84f105a429ec4d463a998a96e36432',
  'entry_sha256': '9dbdce4f007ba2cdaf217cfca89e3a6a86f89fd38f8ef9d895c616f1487fc9dc',
  'learn': ['w=$(mktemp -d "$HOME/foundation-timezones.XXXXXX") && cd "$w" && umask 077; here() { '
            'case "$w" in "$HOME"/foundation-timezones.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
            '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 --output=avail '
            '/ | tail -1)" -ge 1073741824 && pwd',
            'here && fresh "$w/time-context.txt" && fresh "$w/localtime-before.txt" && timedatectl '
            '> time-context.txt && test -L /etc/localtime && readlink /etc/localtime > '
            'localtime-before.txt && test "$(cat localtime-before.txt)" = '
            '/usr/share/zoneinfo/Etc/UTC && printf "winter\\n" && env TZ=Europe/Berlin date -d '
            '"2026-01-01 12:00:00 UTC" "+%F %T %z" && printf "summer\\n" && env TZ=Europe/Berlin '
            'date -d "2026-07-01 12:00:00 UTC" "+%F %T %z"',
            'here && fresh "$w/epoch-before.txt" && fresh "$w/zone-changed.txt" && fresh '
            '"$w/epoch-after.txt" && test "$(readlink /etc/localtime)" = "$(cat '
            'localtime-before.txt)" && date +%s > epoch-before.txt && sudo timedatectl '
            'set-timezone Europe/Berlin && test "$(readlink -f /etc/localtime)" = '
            '/usr/share/zoneinfo/Europe/Berlin && readlink /etc/localtime > zone-changed.txt && '
            'date "+%F %T %z" && date +%s > epoch-after.txt && test "$(cat epoch-after.txt)" -ge '
            '"$(cat epoch-before.txt)"',
            'here && test -L /etc/localtime && test "$(readlink /etc/localtime)" = "$(cat '
            'zone-changed.txt)" && test "$(cat localtime-before.txt)" = '
            '/usr/share/zoneinfo/Etc/UTC && sudo ln -sfn -- /usr/share/zoneinfo/Etc/UTC '
            '/etc/localtime && test "$(readlink /etc/localtime)" = "$(cat localtime-before.txt)" '
            '&& timedatectl'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-timezones.XXXXXX") && cd "$w" && umask 077; '
                'here() { case "$w" in "$HOME"/foundation-timezones.??????) ;; *) return 19;; '
                'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a '
                '"$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; '
                'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && pwd',
                'here && fresh "$w/time-context.txt" && fresh "$w/localtime-before.txt" && '
                'timedatectl > time-context.txt && test -L /etc/localtime && readlink '
                '/etc/localtime > localtime-before.txt && test "$(cat localtime-before.txt)" = '
                '/usr/share/zoneinfo/Etc/UTC && printf "winter\\n" && env TZ=Europe/Berlin date -d '
                '"2026-01-01 12:00:00 UTC" "+%F %T %z" && printf "summer\\n" && env '
                'TZ=Europe/Berlin date -d "2026-07-01 12:00:00 UTC" "+%F %T %z"',
                'here && fresh "$w/epoch-before.txt" && fresh "$w/zone-changed.txt" && fresh '
                '"$w/epoch-after.txt" && test "$(readlink /etc/localtime)" = "$(cat '
                'localtime-before.txt)" && date +%s > epoch-before.txt && sudo timedatectl '
                'set-timezone Europe/Berlin && test "$(readlink -f /etc/localtime)" = '
                '/usr/share/zoneinfo/Europe/Berlin && readlink /etc/localtime > zone-changed.txt '
                '&& date "+%F %T %z" && date +%s > epoch-after.txt && test "$(cat '
                'epoch-after.txt)" -ge "$(cat epoch-before.txt)"',
                'here && test -L /etc/localtime && test "$(readlink /etc/localtime)" = "$(cat '
                'zone-changed.txt)" && test "$(cat localtime-before.txt)" = '
                '/usr/share/zoneinfo/Etc/UTC && sudo ln -sfn -- /usr/share/zoneinfo/Etc/UTC '
                '/etc/localtime && test "$(readlink /etc/localtime)" = "$(cat '
                'localtime-before.txt)" && timedatectl'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-xz-evidence',
              'content_version': '1.0.0',
              'title': 'Inspect an xz stream and recover exact bytes',
              'goal': 'Practice xz/xzcat, bounded memory/threads, container validation versus '
                      'independent content checks.',
              'challenge': 'Select and recover the correct small stream, prove independent '
                           'expected bytes and retain the rejected candidate. Retain actual '
                           'outputs/statuses and preserve originals; report reasoning through '
                           'self-review, not a score.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-xz-evidence.XXXXXX") && cd '
                                    '"$w" && umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-xz-evidence.??????) ;; *) return 19;; '
                                    'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L '
                                    '"$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" '
                                    '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                                    'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && '
                                    'test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h '
                                    '"$1")" = learner:600:1; }; here && test "$(df -B1 '
                                    '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                         'explanation': 'Record this unique guest-only workspace. On Resume '
                                        're-establish the recorded path/definitions; never '
                                        'overwrite another exercise.',
                         'expected': 'Private learner-owned700 directory and observed1GiB free '
                                     'admission.'},
                        {'command': 'here && fresh "$w/source.txt" && fresh "$w/source.sha" && '
                                    'printf "caf\\303\\251\\n" > source.txt && sha256sum '
                                    'source.txt > source.sha && test "$(wc -c < source.txt)" -le '
                                    '65536 && fresh "$w/good.xz" && timeout -k 1s 10s xz '
                                    '--threads=1 --memlimit-compress=64MiB -1 -c source.txt > '
                                    'good.xz && timeout -k 1s 10s xz --list good.xz && timeout -k '
                                    '1s 10s xz --memlimit-decompress=64MiB -t good.xz',
                         'explanation': 'Keep the source using -c; one worker and small fixed '
                                        'input. Container integrity is neither authentication nor '
                                        'correct-content proof.',
                         'expected': 'Bounded xz creation/list/test; original retained.'},
                        {'command': 'here && fresh "$w/restored.txt" && timeout -k 1s 10s xzcat '
                                    '--memlimit-decompress=64MiB good.xz > restored.txt && cmp '
                                    'source.txt restored.txt && sha256sum -c source.sha && fresh '
                                    '"$w/truncated.xz" && head -c 12 good.xz > truncated.xz',
                         'explanation': 'Recover separately and compare independent original '
                                        'bytes; create only a tiny private damaged candidate.',
                         'expected': 'Exact recovery and retained 12-byte rejected candidate.'},
                        {'command': 'foundation_step() { here && fresh "$w/damaged.log" || return '
                                    '19; if timeout -k 1s 10s xz --memlimit-decompress=64MiB -t '
                                    'truncated.xz > damaged.log 2>&1; then return 1; else test $? '
                                    '= 1 && test -s damaged.log && sha256sum -c source.sha; fi; }; '
                                    'foundation_step',
                         'explanation': 'Require actual damage refusal, not any earlier guard '
                                        'failure. Do not overwrite source or retained stream.',
                         'expected': 'Container test rejects known truncated copy.'},
                        {'command': 'foundation_step() { here && fresh "$w/low-partial.xz" && '
                                    'fresh "$w/low.log" || return 19; if timeout -k 1s 10s xz '
                                    '--threads=1 --memlimit-compress=1MiB --no-adjust -9 -c '
                                    'source.txt > low-partial.xz 2> low.log; then return 1; else '
                                    'test $? = 1 && grep -F "Memory usage limit is too low for the '
                                    'given filter setup." low.log && grep -F "The limit is 1 MiB." '
                                    'low.log && sha256sum -c source.sha; fi; }; foundation_step',
                         'explanation': 'This deliberate refusal tests requested resource setup '
                                        'without allocating the reported674MiB. --no-adjust '
                                        'prevents silent preset reduction.',
                         'expected': 'Actual low-memory refusal; unchanged source.'}],
              'hints': ['xz -t success is not authenticity or the correct report; avoid default '
                        'source deletion and force overwrite.',
                        'Choose command scope deliberately; compare known bytes and actual '
                        'statuses, not only a successful-looking display.',
                        'Retain before evidence; refuse collisions and restore exact policy state '
                        'before leaving. Guest root can bypass guest-side guards.'],
              'review': ['I demonstrated the selected mode’s actual observations and retained an '
                         'incorrect or incomplete case.',
                         'I preserved originals and can explain the reasoning and limitations; '
                         'this records self-review, not automatic assessment.',
                         'I restored any changed default/zone and retained the exact workspace '
                         'without touching unrelated files.'],
              'coverage': 'LPIC-1 active v5.0 partial103.2 xzcat and103.3 xz/unxz; limited LPIC-2 '
                          'activev4.5 206.2 compression reinforcement only. Container validation '
                          'is not correct-content/authenticity proof; no complete-objective '
                          'credit.'},
  'entry': {'id': 'real-linux-foundation-xz-evidence',
            'resource': 'real-linux-foundation-xz-evidence.json',
            'description': 'Practice xz/xzcat, bounded memory/threads, container validation versus '
                           'independent content checks.',
            'objectives': ['103.2 xzcat', '103.3 xz/unxz; 206.2 reinforcement'],
            'troubleshooting': ['xz -t success is not authenticity or the correct report; avoid '
                                'default source deletion and force overwrite.',
                                'A missing tool/default or unexpected collision is a refusal, not '
                                'permission to change image/PAM/packages. Retain the failure and '
                                'Reset if exact rollback cannot be proved.'],
            'cleanup': ['Stay inside the recorded private workspace; retain its original and '
                        'result files as evidence. Do not recursively delete or remove unknown '
                        'members.',
                        'If default locale/timezone changed, perform only the displayed guarded '
                        'exact rollback before leaving. Keep root snapshot evidence; no '
                        'authentication, clock, RTC, NTP or host changes.',
                        'Reset retains disk generations. Resume boots the same disk, not RAM, '
                        'shell variables or processes. Re-enter only recorded path/function '
                        'definitions.'],
            'materials': ['For either mode, this is the non-repair workspace setup: w=$(mktemp -d '
                          '"$HOME/foundation-xz-evidence.XXXXXX") && cd "$w" && umask 077; here() '
                          '{ case "$w" in "$HOME"/foundation-xz-evidence.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 '
                          '--output=avail / | tail -1)" -ge 1073741824 && pwd',
                          'On Resume set w to its recorded exact path, cd there and restore the '
                          'definitions; do not run mktemp or recreate retained fixtures. '
                          'Definitions: here() { case "$w" in '
                          '"$HOME"/foundation-xz-evidence.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = '
                          '"$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { here && test '
                          '"${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test "$(stat -c '
                          '%U:%a:%h "$1")" = learner:600:1; }',
                          'Challenge starting fixture, not recovery: challenge_fixture() { here && '
                          'fresh "$w/source.txt" && fresh "$w/source.sha" && printf '
                          '"caf\\303\\251\\n" > source.txt && sha256sum source.txt > source.sha && '
                          'test "$(wc -c < source.txt)" -le 65536 && fresh "$w/good.xz" && timeout '
                          '-k 1s 10s xz --threads=1 --memlimit-compress=64MiB -1 -c source.txt > '
                          'good.xz && timeout -k 1s 10s xz --list good.xz && timeout -k 1s 10s xz '
                          '--memlimit-decompress=64MiB -t good.xz || return 19; here && fresh '
                          '"$w/truncated.xz" && head -c 12 good.xz > truncated.xz; }; '
                          'challenge_fixture. Required recovered original is UTF8 café plus '
                          'newline, octets63 61 66 c3 a9 0a. Retain rejected12byte stream and '
                          'deliberate1MiB-no-adjust failure; compare recovered bytes '
                          'independently.'],
            'observations': ['Source hash, compressed/list/check status, bounded resource options, '
                             'rejected-copy evidence, restored-byte comparison.',
                             'Observed command/status/byte outcomes, not automatically graded '
                             'reasoning.'],
            'questions': ['Which evidence proves the specific outcome, and what does it not '
                          'establish?',
                          'xz -t success is not authenticity or the correct report; avoid default '
                          'source deletion and force overwrite.'],
            'limitations': ['Real offline guest, not supplied snapshots. One worker; <=64KiB input '
                            'and small fixed-fixture expected outputs below256KiB (cooperative '
                            'accounting, not a kernel aggregate quota). Each iconv/xz command10s '
                            'plus1s grace and64MiB xz cap; no large arbitrary streams. Free-space '
                            'admission is not a quota or guaranteed reserve. Guest root can '
                            'override guest-side limits.',
                            'No clock/RTC/NTP writes, networking, new credentials, source '
                            'replacement, automatic grading or public-release claim. Physical '
                            'keyboard/accessibility checks remain separate.']},
  'resource_sha256': '29b774d5cc4c29044c8f7458dbce4b3403ae0529d995cd119343ce1c16c016e3',
  'entry_sha256': '7d94fa479991948a1afbc728b5f9e71543a3ab6f132d59152b5c1cf252197e37',
  'learn': ['w=$(mktemp -d "$HOME/foundation-xz-evidence.XXXXXX") && cd "$w" && umask 077; here() '
            '{ case "$w" in "$HOME"/foundation-xz-evidence.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
            '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; here && test "$(df -B1 --output=avail '
            '/ | tail -1)" -ge 1073741824 && pwd',
            'here && fresh "$w/source.txt" && fresh "$w/source.sha" && printf "caf\\303\\251\\n" > '
            'source.txt && sha256sum source.txt > source.sha && test "$(wc -c < source.txt)" -le '
            '65536 && fresh "$w/good.xz" && timeout -k 1s 10s xz --threads=1 '
            '--memlimit-compress=64MiB -1 -c source.txt > good.xz && timeout -k 1s 10s xz --list '
            'good.xz && timeout -k 1s 10s xz --memlimit-decompress=64MiB -t good.xz',
            'here && fresh "$w/restored.txt" && timeout -k 1s 10s xzcat '
            '--memlimit-decompress=64MiB good.xz > restored.txt && cmp source.txt restored.txt && '
            'sha256sum -c source.sha && fresh "$w/truncated.xz" && head -c 12 good.xz > '
            'truncated.xz',
            'foundation_step() { here && fresh "$w/damaged.log" || return 19; if timeout -k 1s 10s '
            'xz --memlimit-decompress=64MiB -t truncated.xz > damaged.log 2>&1; then return 1; '
            'else test $? = 1 && test -s damaged.log && sha256sum -c source.sha; fi; }; '
            'foundation_step',
            'foundation_step() { here && fresh "$w/low-partial.xz" && fresh "$w/low.log" || return '
            '19; if timeout -k 1s 10s xz --threads=1 --memlimit-compress=1MiB --no-adjust -9 -c '
            'source.txt > low-partial.xz 2> low.log; then return 1; else test $? = 1 && grep -F '
            '"Memory usage limit is too low for the given filter setup." low.log && grep -F "The '
            'limit is 1 MiB." low.log && sha256sum -c source.sha; fi; }; foundation_step'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-xz-evidence.XXXXXX") && cd "$w" && umask 077; '
                'here() { case "$w" in "$HOME"/foundation-xz-evidence.??????) ;; *) return 19;; '
                'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a '
                '"$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; '
                'here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && pwd',
                'challenge_fixture() { here && fresh "$w/source.txt" && fresh "$w/source.sha" && '
                'printf "caf\\303\\251\\n" > source.txt && sha256sum source.txt > source.sha && '
                'test "$(wc -c < source.txt)" -le 65536 && fresh "$w/good.xz" && timeout -k 1s 10s '
                'xz --threads=1 --memlimit-compress=64MiB -1 -c source.txt > good.xz && timeout -k '
                '1s 10s xz --list good.xz && timeout -k 1s 10s xz --memlimit-decompress=64MiB -t '
                'good.xz || return 19; here && fresh "$w/truncated.xz" && head -c 12 good.xz > '
                'truncated.xz; }; challenge_fixture',
                'here && fresh "$w/restored.txt" && timeout -k 1s 10s xzcat '
                '--memlimit-decompress=64MiB good.xz > restored.txt && cmp source.txt restored.txt '
                '&& sha256sum -c source.sha && regular "$w/truncated.xz" && test "$(wc -c < '
                'truncated.xz)" = 12',
                'foundation_step() { here && fresh "$w/damaged.log" || return 19; if timeout -k 1s '
                '10s xz --memlimit-decompress=64MiB -t truncated.xz > damaged.log 2>&1; then '
                'return 1; else test $? = 1 && test -s damaged.log && sha256sum -c source.sha; fi; '
                '}; foundation_step',
                'foundation_step() { here && fresh "$w/low-partial.xz" && fresh "$w/low.log" || '
                'return 19; if timeout -k 1s 10s xz --threads=1 --memlimit-compress=1MiB '
                '--no-adjust -9 -c source.txt > low-partial.xz 2> low.log; then return 1; else '
                'test $? = 1 && grep -F "Memory usage limit is too low for the given filter '
                'setup." low.log && grep -F "The limit is 1 MiB." low.log && sha256sum -c '
                'source.sha; fi; }; foundation_step'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': ['static_negative() { here && fresh "$w/source.txt" && printf "%s\\n" '
                           'collision-preserved > "source.txt" || return 19; '
                           'foundation_collision() { challenge_fixture() { here && fresh '
                           '"$w/source.txt" && fresh "$w/source.sha" && printf "caf\\303\\251\\n" '
                           '> source.txt && sha256sum source.txt > source.sha && test "$(wc -c < '
                           'source.txt)" -le 65536 && fresh "$w/good.xz" && timeout -k 1s 10s xz '
                           '--threads=1 --memlimit-compress=64MiB -1 -c source.txt > good.xz && '
                           'timeout -k 1s 10s xz --list good.xz && timeout -k 1s 10s xz '
                           '--memlimit-decompress=64MiB -t good.xz || return 19; here && fresh '
                           '"$w/truncated.xz" && head -c 12 good.xz > truncated.xz; }; '
                           'challenge_fixture\n'
                           '}; if foundation_collision; then return 1; else test $? -ne 0 || '
                           'return 19; fi && regular "$w/source.txt" && grep -Fx '
                           'collision-preserved "source.txt" && test ! -e "$w/failed-queued.log" '
                           '&& test ! -e "$w/good.xz" && test ! -e "$w/truncated.xz" && rm -- '
                           '"source.txt"; }; static_negative'],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-at-queue',
              'content_version': '1.0.0',
              'title': 'Inspect and cancel the exact one-off job',
              'goal': 'Distinguish queued work from completion; dynamically identify and remove '
                      'only the owned practice job.',
              'challenge': 'Submit the declared harmless learner job for now+2minutes, inspect its '
                           'actual ID/owner/body, cancel only that job, and prove no result after '
                           'its due time while all unrelated queued rows remain byte-identical. No '
                           'fixed IDs, all-job cancellation or spool editing.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-at-queue.XXXXXX") && cd "$w" '
                                    '&& umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-at-queue.??????) ;; *) return 19;; esac; '
                                    'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                                    'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
                                    'here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L '
                                    '"$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                                    '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = '
                                    'learner:600:1; }; jobid() { regular "$1" || return 19; '
                                    'job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); '
                                    'case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt '
                                    '0;; esac; }; here && test "$(df -B1 --output=avail / | tail '
                                    '-1)" -ge 1073741824 && systemctl is-active atd && pwd',
                         'explanation': 'Record the private path/definitions. Refuse collisions '
                                        'and insufficient space; Resume reuses the recorded '
                                        'workspace, not a new job.',
                         'expected': 'Owned700 workspace, actual atd and observed1GiB reserve.'},
                        {'command': 'foundation_step() { here && fresh "$w/foreign-queued.log" || '
                                    "return 19; printf '/usr/bin/true\\n' | sudo /usr/sbin/runuser "
                                    '-u ll-at-allow -- /usr/bin/at -M now + 30 minutes > '
                                    'foreign-queued.log 2>&1 && jobid "$w/foreign-queued.log" && '
                                    'fresh "$w/foreign-queue.txt" && sudo atq > foreign-queue.txt '
                                    '&& awk -v id="$job" \'$1==id && $NF=="ll-at-allow" {f=1} END '
                                    "{exit !f}' foreign-queue.txt; }; foundation_step",
                         'explanation': 'Create only this separately recorded harmless comparison '
                                        'job. It must survive learner-job cancellation; later '
                                        'cancel it exactly as its owner. Do not treat the root '
                                        'queue as learner-owned.',
                         'expected': 'Known ll-at-allow comparison job remains queued.'},
                        {'command': 'here && fresh "$w/queue-before.txt" && sudo atq > '
                                    'queue-before.txt && fresh "$w/job.sh" && printf \'set -C || '
                                    'exit 92\\nprintf "cancelled-job-ran\\\\n" > '
                                    '"%s/cancelled-result"\\n\' "$w" > job.sh && regular '
                                    '"$w/job.sh" && fresh "$w/cancelled-result" && fresh '
                                    '"$w/queued.log" && at -M -f job.sh now + 2 minutes > '
                                    'queued.log 2>&1 && jobid "$w/queued.log" && fresh '
                                    '"$w/queue-during.txt" && sudo atq > queue-during.txt && awk '
                                    '-v id="$job" \'$1==id && $NF=="learner" {f=1} END {exit !f}\' '
                                    'queue-during.txt',
                         'explanation': 'Dynamically capture the exact owned job ID and unchanged '
                                        'unrelated rows. A queued job is not a completed job.',
                         'expected': 'One declared future learner job with retained ownership '
                                     'evidence.'},
                        {'command': 'here && jobid "$w/queued.log" && fresh "$w/body.txt" && '
                                    'timeout -k 1s 10s at -c "$job" > body.txt && grep -F '
                                    '"$w/cancelled-result" body.txt && atrm "$job" && fresh '
                                    '"$w/queue-after.txt" && sudo atq > queue-after.txt && cmp '
                                    'queue-before.txt queue-after.txt && test ! -e '
                                    '"$w/cancelled-result" && test ! -L "$w/cancelled-result"',
                         'explanation': 'Inspect the expected body/path before exact cancellation. '
                                        'Never assume a fixed job number or remove all jobs. '
                                        'Immediate absence is observed; wait until the recorded '
                                        'due time for stronger absence evidence.',
                         'expected': 'Owned cancellation; identical other queue rows; no immediate '
                                     'result.'},
                        {'command': 'here && sleep 130 && test ! -e "$w/cancelled-result" && test '
                                    '! -L "$w/cancelled-result" && fresh "$w/queue-deadline.txt" '
                                    '&& sudo atq > queue-deadline.txt && cmp queue-before.txt '
                                    'queue-deadline.txt',
                         'explanation': 'This bounded wait exceeds the now+2minutes deadline, '
                                        'without changing the clock. Retain cancellation evidence '
                                        'and no-result check.',
                         'expected': 'Cancelled output absent after its due time, unrelated queue '
                                     'unchanged.'},
                        {'command': 'foundation_step() { here && jobid "$w/foreign-queued.log" && '
                                    'fresh "$w/foreign-before-cleanup.txt" && sudo atq > '
                                    'foreign-before-cleanup.txt && awk -v id="$job" \'$1==id && '
                                    '$NF=="ll-at-allow" {f=1} END {exit !f}\' '
                                    'foreign-before-cleanup.txt && fresh "$w/foreign-body.txt" && '
                                    'sudo /usr/sbin/runuser -u ll-at-allow -- at -c "$job" > '
                                    'foreign-body.txt && grep -Fx /usr/bin/true foreign-body.txt '
                                    '|| return 19; sudo /usr/sbin/runuser -u ll-at-allow -- atrm '
                                    '"$job" && fresh "$w/foreign-after-cleanup.txt" && sudo atq > '
                                    'foreign-after-cleanup.txt && ! awk -v id="$job" \'$1==id '
                                    "{f=1} END {exit !f}' foreign-after-cleanup.txt; }; "
                                    'foundation_step',
                         'explanation': 'After comparison, cancel only the positively matched '
                                        'declared comparison job. This does not authorize '
                                        'cancelling an unrelated owner job.',
                         'expected': 'Comparison job safely removed; unrelated rows preserved.'}],
              'hints': ['Never fixed job numbers, atrm all, global spool edits or count-only '
                        'proof; root atq sees others.',
                        'Use the actual dynamically captured job ID and successful owner-matched '
                        'queue queries; a command failure is not an empty queue.',
                        'Inspect actual result ownership, bytes and exit status; cancel only '
                        'positively matched pending work before exact rollback.'],
              'review': ['I demonstrated the selected mode’s facts, actual identities/results and '
                         'an incorrect interpretation or attempt.',
                         'I can separate queueing, execution, access policy and self-reviewed '
                         'reasoning. Completion is unscored and not automatic verification.',
                         'I removed only positively matched owned jobs, restored any exact policy '
                         'fixture and retained evidence; no authentication or host changes.'],
              'coverage': 'LPIC-1 active v5.0 partial 108.2 at/atq/atrm. No full objective, '
                          'automatic assessment or endorsement. The plan’s 107.2 at tags were '
                          'corrected to active108.2;107.2 concerns display/X11.'},
  'entry': {'id': 'real-linux-foundation-at-queue',
            'resource': 'real-linux-foundation-at-queue.json',
            'description': 'Distinguish queued work from completion; dynamically identify and '
                           'remove only the owned practice job.',
            'objectives': ['108.2 at/atq/atrm'],
            'troubleshooting': ['Never fixed job numbers, atrm all, global spool edits or '
                                'count-only proof; root atq sees others.',
                                'Direct sudo -u practice-user is not authorized by the root-only '
                                'guest sudo rule. Use the displayed root-authorized runuser; never '
                                'change sudo/PAM or enter/create passwords.'],
            'cleanup': ['Before leaving, inspect only each recorded job ID using its successful '
                        'owner query plus saved body/path/owner evidence. If still queued, cancel '
                        'that exact owned ID; if a job may be running, wait up to150s for its '
                        'bounded result/exit. Do not remove its workspace while it can write. '
                        'Unknown ownership requires refusal, not broad cleanup.',
                        'For at-access perform only the displayed SHA/type/mode guarded removal of '
                        'the known allow fixture and byte-check original deny/auth/sudo '
                        'fingerprints. Preserve pre-created practice users and root snapshots; no '
                        'account deletion or PAM editing.',
                        'Keep the exact private workspace as evidence; no recursive deletion, '
                        'spool edits or helper-state pruning. Repeated setup refuses existing '
                        'originals; interruption does not permit replacing a fixture. Reset '
                        'retains the previous disk; Resume restores disk, not RAM or jobs.'],
            'materials': ['Fresh Learn or Challenge setup: w=$(mktemp -d '
                          '"$HOME/foundation-at-queue.XXXXXX") && cd "$w" && umask 077; here() { '
                          'case "$w" in "$HOME"/foundation-at-queue.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" '
                          '|| return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' '
                          '"$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; '
                          'esac; }; here && test "$(df -B1 --output=avail / | tail -1)" -ge '
                          '1073741824 && systemctl is-active atd && pwd',
                          'For Resume set w to its recorded path and restore these definitions, '
                          'not mktemp or a new incident: here() { case "$w" in '
                          '"$HOME"/foundation-at-queue.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = '
                          '"$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { here && test '
                          '"${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test "$(stat -c '
                          '%U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" || return '
                          '19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); case '
                          '"$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }',
                          'Challenge starting comparison fixture (not target repair/cancellation): '
                          'foundation_step() { here && fresh "$w/foreign-queued.log" || return 19; '
                          "printf '/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-allow -- "
                          '/usr/bin/at -M now + 30 minutes > foreign-queued.log 2>&1 && jobid '
                          '"$w/foreign-queued.log" && fresh "$w/foreign-queue.txt" && sudo atq > '
                          'foreign-queue.txt && awk -v id="$job" \'$1==id && $NF=="ll-at-allow" '
                          "{f=1} END {exit !f}' foreign-queue.txt; }; foundation_step. Then submit "
                          'your own harmless now+2minutes job producing cancelled-result, inspect '
                          'its ID/owner/body, cancel only it, and show this comparison remains '
                          'until its separate exact cleanup.',
                          'Independent selected-mode outcome: Submit the declared harmless learner '
                          'job for now+2minutes, inspect its actual ID/owner/body, cancel only '
                          'that job, and prove no result after its due time while all unrelated '
                          'queued rows remain byte-identical. No fixed IDs, all-job cancellation '
                          'or spool editing. No keyword score or host/remote effects. Fixed '
                          'handover bytes and summer offset remain as described in the incident.'],
            'observations': ['Queue ID/owner/time/body hash before/after, absence of cancelled '
                             'output after its deadline, foreign job preserved.',
                             'Successful owner query, actual result/footer/UID/bytes where '
                             'executed; reasoning self-reviewed.'],
            'questions': ['What proves this specific action and what remains uncertain?',
                          'Never fixed job numbers, atrm all, global spool edits or count-only '
                          'proof; root atq sees others.'],
            'limitations': ['No runtime network/mail or credentials. at -M prevents mail delivery. '
                            '/bin/sh is not an interactive Bash session; queueing does not prove '
                            'PAM/account execution. Locked passwords and nologin do not prohibit '
                            'authorized root runuser.',
                            'One finite job at a time; child6s plus2s grace, output4KiB, '
                            'observation150s. Cancellation-only lesson waits130s after submission; '
                            'every utility query10s where bounded. At most64KiB input/256KiB '
                            'practice output, observed1GiB guest free admission; not a quota. Root '
                            'can override guest limits.',
                            'No automatically scored reasoning, preserved RAM/jobs on Resume, '
                            'physical-keyboard or accessibility certification.',
                            'The harmless foreign comparison is scheduled30minutes ahead; complete '
                            'observations and exact owned cancellation within15minutes. If '
                            'interrupted past that budget, inspect actual queue state and retain '
                            'the inconclusive comparison; never claim it remained queued after its '
                            'due time.']},
  'resource_sha256': '3dc1664a85bc905eb422ea5aa8be56cc46ea16211162563a9ffeab79e7d8ac6a',
  'entry_sha256': '47c8eaf69b9142ba8c1689981d770e2903e40dc5cf6dd77da7a14e098db72b8e',
  'learn': ['w=$(mktemp -d "$HOME/foundation-at-queue.XXXXXX") && cd "$w" && umask 077; here() { '
            'case "$w" in "$HOME"/foundation-at-queue.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
            '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" || return 19; '
            'job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); case "$job" in '
            '\'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }; here && test "$(df -B1 '
            '--output=avail / | tail -1)" -ge 1073741824 && systemctl is-active atd && pwd',
            'foundation_step() { here && fresh "$w/foreign-queued.log" || return 19; printf '
            "'/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-allow -- /usr/bin/at -M now + 30 "
            'minutes > foreign-queued.log 2>&1 && jobid "$w/foreign-queued.log" && fresh '
            '"$w/foreign-queue.txt" && sudo atq > foreign-queue.txt && awk -v id="$job" \'$1==id '
            '&& $NF=="ll-at-allow" {f=1} END {exit !f}\' foreign-queue.txt; }; foundation_step',
            'here && fresh "$w/queue-before.txt" && sudo atq > queue-before.txt && fresh '
            '"$w/job.sh" && printf \'set -C || exit 92\\nprintf "cancelled-job-ran\\\\n" > '
            '"%s/cancelled-result"\\n\' "$w" > job.sh && regular "$w/job.sh" && fresh '
            '"$w/cancelled-result" && fresh "$w/queued.log" && at -M -f job.sh now + 2 minutes > '
            'queued.log 2>&1 && jobid "$w/queued.log" && fresh "$w/queue-during.txt" && sudo atq > '
            'queue-during.txt && awk -v id="$job" \'$1==id && $NF=="learner" {f=1} END {exit !f}\' '
            'queue-during.txt',
            'here && jobid "$w/queued.log" && fresh "$w/body.txt" && timeout -k 1s 10s at -c '
            '"$job" > body.txt && grep -F "$w/cancelled-result" body.txt && atrm "$job" && fresh '
            '"$w/queue-after.txt" && sudo atq > queue-after.txt && cmp queue-before.txt '
            'queue-after.txt && test ! -e "$w/cancelled-result" && test ! -L "$w/cancelled-result"',
            'here && sleep 130 && test ! -e "$w/cancelled-result" && test ! -L '
            '"$w/cancelled-result" && fresh "$w/queue-deadline.txt" && sudo atq > '
            'queue-deadline.txt && cmp queue-before.txt queue-deadline.txt',
            'foundation_step() { here && jobid "$w/foreign-queued.log" && fresh '
            '"$w/foreign-before-cleanup.txt" && sudo atq > foreign-before-cleanup.txt && awk -v '
            'id="$job" \'$1==id && $NF=="ll-at-allow" {f=1} END {exit !f}\' '
            'foreign-before-cleanup.txt && fresh "$w/foreign-body.txt" && sudo /usr/sbin/runuser '
            '-u ll-at-allow -- at -c "$job" > foreign-body.txt && grep -Fx /usr/bin/true '
            'foreign-body.txt || return 19; sudo /usr/sbin/runuser -u ll-at-allow -- atrm "$job" '
            '&& fresh "$w/foreign-after-cleanup.txt" && sudo atq > foreign-after-cleanup.txt && ! '
            'awk -v id="$job" \'$1==id {f=1} END {exit !f}\' foreign-after-cleanup.txt; }; '
            'foundation_step'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-at-queue.XXXXXX") && cd "$w" && umask 077; here() '
                '{ case "$w" in "$HOME"/foundation-at-queue.??????) ;; *) return 19;; esac; test '
                '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e '
                '"$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = '
                'learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test '
                '! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! '
                '-L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular '
                '"$1" || return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); '
                'case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }; here && '
                'test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && systemctl is-active '
                'atd && pwd',
                'foundation_step() { here && fresh "$w/foreign-queued.log" || return 19; printf '
                "'/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-allow -- /usr/bin/at -M now "
                '+ 30 minutes > foreign-queued.log 2>&1 && jobid "$w/foreign-queued.log" && fresh '
                '"$w/foreign-queue.txt" && sudo atq > foreign-queue.txt && awk -v id="$job" '
                '\'$1==id && $NF=="ll-at-allow" {f=1} END {exit !f}\' foreign-queue.txt; }; '
                'foundation_step',
                'here && fresh "$w/queue-before.txt" && sudo atq > queue-before.txt && fresh '
                '"$w/job.sh" && printf \'set -C || exit 92\\nprintf "cancelled-job-ran\\\\n" > '
                '"%s/cancelled-result"\\n\' "$w" > job.sh && regular "$w/job.sh" && fresh '
                '"$w/cancelled-result" && fresh "$w/queued.log" && at -M -f job.sh now + 2 minutes '
                '> queued.log 2>&1 && jobid "$w/queued.log" && fresh "$w/queue-during.txt" && sudo '
                'atq > queue-during.txt && awk -v id="$job" \'$1==id && $NF=="learner" {f=1} END '
                "{exit !f}' queue-during.txt",
                'here && jobid "$w/queued.log" && fresh "$w/body.txt" && timeout -k 1s 10s at -c '
                '"$job" > body.txt && grep -F "$w/cancelled-result" body.txt && atrm "$job" && '
                'fresh "$w/queue-after.txt" && sudo atq > queue-after.txt && cmp queue-before.txt '
                'queue-after.txt && test ! -e "$w/cancelled-result" && test ! -L '
                '"$w/cancelled-result"',
                'here && sleep 130 && test ! -e "$w/cancelled-result" && test ! -L '
                '"$w/cancelled-result" && fresh "$w/queue-deadline.txt" && sudo atq > '
                'queue-deadline.txt && cmp queue-before.txt queue-deadline.txt',
                'foundation_step() { here && jobid "$w/foreign-queued.log" && fresh '
                '"$w/foreign-before-cleanup.txt" && sudo atq > foreign-before-cleanup.txt && awk '
                '-v id="$job" \'$1==id && $NF=="ll-at-allow" {f=1} END {exit !f}\' '
                'foreign-before-cleanup.txt && fresh "$w/foreign-body.txt" && sudo '
                '/usr/sbin/runuser -u ll-at-allow -- at -c "$job" > foreign-body.txt && grep -Fx '
                '/usr/bin/true foreign-body.txt || return 19; sudo /usr/sbin/runuser -u '
                'll-at-allow -- atrm "$job" && fresh "$w/foreign-after-cleanup.txt" && sudo atq > '
                'foreign-after-cleanup.txt && ! awk -v id="$job" \'$1==id {f=1} END {exit !f}\' '
                'foreign-after-cleanup.txt; }; foundation_step'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-at-execution',
              'content_version': '1.0.0',
              'title': 'Prove a one-off job’s environment and result',
              'goal': 'Observe /bin/sh execution, captured environment/cwd/umask and actual '
                      'successful or failed result.',
              'challenge': 'Repair the prepared wrong captured locale in a distinct one-off retry. '
                           'Preserve the first actual exit1/result, submit C locale and prove '
                           'actual UID/cwd/umask/file limit/content/exit0 despite a later '
                           'different display locale. A vanished queue row is insufficient. Use '
                           'the supplied6s finite body and keep originals.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-at-execution.XXXXXX") && cd '
                                    '"$w" && umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-at-execution.??????) ;; *) return 19;; '
                                    'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L '
                                    '"$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" '
                                    '= "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                                    'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && '
                                    'test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h '
                                    '"$1")" = learner:600:1; }; jobid() { regular "$1" || return '
                                    '19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' '
                                    '"$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test '
                                    '"$job" -gt 0;; esac; }; here && test "$(df -B1 --output=avail '
                                    '/ | tail -1)" -ge 1073741824 && systemctl is-active atd && '
                                    'pwd',
                         'explanation': 'Record the private path/definitions. Refuse collisions '
                                        'and insufficient space; Resume reuses the recorded '
                                        'workspace, not a new job.',
                         'expected': 'Owned700 workspace, actual atd and observed1GiB reserve.'},
                        {'command': 'here && fresh "$w/job.sh" && cat > job.sh <<\'LL_JOB\'\n'
                                    '#!/bin/sh\n'
                                    'umask 077 || exit 90\n'
                                    'ulimit -f 8 || exit 91\n'
                                    'test ! -e result && test ! -L result || exit 89\n'
                                    'set -C || exit 92\n'
                                    '{\n'
                                    ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 '
                                    '" hard=" $5}\' /proc/self/limits\n'
                                    " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
                                    '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" '
                                    '"$(id -u)" "$(pwd -P)" "$(umask)"; printf '
                                    '"LANG=%s\\nLC_ALL=%s\\n" "$LANG" "$LC_ALL"; test "$LANG" = C '
                                    '&& test "$LC_ALL" = C && printf "bounded-job-complete\\n"\'\n'
                                    ' rc=$?\n'
                                    ' printf \'exit=%s\\n\' "$rc"\n'
                                    '} > result 2>&1\n'
                                    'exit "$rc"\n'
                                    'LL_JOB',
                         'explanation': 'Enter this short /bin/sh job manually. Its own6s child '
                                        'timeout and4KiB output limit are explicit; sudo/root can '
                                        'override guest limits.',
                         'expected': 'Private fixed job body, explicit environment/status '
                                     'recording.'},
                        {'command': 'here && fresh "$w/result" && regular "$w/job.sh" && fresh '
                                    '"$w/failed-queued.log" && env LANG=de_DE.UTF-8 '
                                    'LC_ALL=de_DE.UTF-8 /usr/bin/at -M -f "$w/job.sh" now + 1 '
                                    'minute > failed-queued.log 2>&1 && jobid '
                                    '"$w/failed-queued.log" && printf "Failed-attempt job=%s\\n" '
                                    '"$job"',
                         'explanation': 'Submit the deliberately wrong captured environment; the '
                                        'job requires C locale. This is a separate actual failed '
                                        'run, not an error invented from queue state.',
                         'expected': 'Recorded first job with wrong environment.'},
                        {'command': 'foundation_step() { here && jobid "$w/failed-queued.log" || '
                                    'return 19; deadline=$(( $(date +%s)+150 )); while ! grep -Fxq '
                                    'exit=1 "$w/result" 2>/dev/null; do test "$(date +%s)" -lt '
                                    '"$deadline" || return 19; sleep 1; done; regular "$w/result" '
                                    '&& grep -Fx identity=learner result && grep -Fx '
                                    'LANG=de_DE.UTF-8 result && fresh "$w/failed-result" && mv -- '
                                    'result failed-result && regular "$w/failed-result" || return '
                                    '19; while :; do fresh "$w/failed-queue-current.txt" || '
                                    'regular "$w/failed-queue-current.txt" || return 19; atq > '
                                    'failed-queue-current.txt || return 19; if awk -v id="$job" '
                                    "'$1==id {f=1} END {exit !f}' failed-queue-current.txt; then "
                                    'test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; '
                                    'else break; fi; done; cat failed-result; }; foundation_step',
                         'explanation': 'Observe actual exit1 and captured locale, then preserve '
                                        'that regular owned result before retrying. Queue errors '
                                        'do not establish absence.',
                         'expected': 'Actual first failure retained; no pending first job.'},
                        {'command': 'here && fresh "$w/result" && regular "$w/job.sh" && fresh '
                                    '"$w/queued.log" && env LANG=C LC_ALL=C /usr/bin/at -M -f '
                                    '"$w/job.sh" now + 1 minute > queued.log 2>&1 && jobid '
                                    '"$w/queued.log" && printf "Recorded job=%s workspace=%s\\n" '
                                    '"$job" "$w"',
                         'explanation': 'Queue from the current verified workspace with explicit C '
                                        'locale. at -M suppresses mail; no MTA or shell-function '
                                        'inheritance is promised.',
                         'expected': 'Actual job ID and captured submission context.'},
                        {'command': 'here && fresh "$w/interactive-after.txt" && env '
                                    'LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 locale > '
                                    'interactive-after.txt && cat interactive-after.txt',
                         'explanation': 'A later display command cannot rewrite the queued job’s '
                                        'captured environment. Compare actual result, not queue '
                                        'disappearance.',
                         'expected': 'German display context differs from the captured C job.'},
                        {'command': 'foundation_step() { here && jobid "$w/queued.log" || return '
                                    '19; deadline=$(( $(date +%s)+150 )); while ! grep -Fxq exit=0 '
                                    '"$w/result" 2>/dev/null; do test "$(date +%s)" -lt '
                                    '"$deadline" || return 19; sleep 1; done; regular "$w/result" '
                                    '&& test "$(wc -c < result)" -le 4096 && grep -Fx '
                                    'identity=learner result && grep -Fx "uid=$(id -u)" result && '
                                    'grep -Fx "cwd=$w" result && grep -Fx umask=0077 result && '
                                    'grep -Fx LANG=C result && grep -Fx LC_ALL=C result && grep '
                                    '-Fx "file_limit_soft=4096 hard=4096" result && grep -Fx '
                                    'bounded-job-complete result || return 19; while :; do fresh '
                                    '"$w/queue-current.txt" || regular "$w/queue-current.txt" || '
                                    'return 19; atq > queue-current.txt || return 19; if awk -v '
                                    'id="$job" \'$1==id {f=1} END {exit !f}\' queue-current.txt; '
                                    'then test "$(date +%s)" -lt "$deadline" || return 19; sleep '
                                    '1; else break; fi; done; cat result; }; foundation_step',
                         'explanation': 'Observe until the original150s deadline. A result footer '
                                        'and actual UID/cwd/umask/locale/limit plus successful '
                                        'queue query prove this specific run; they are not a '
                                        'tamper-proof assessment.',
                         'expected': 'Owned600 result, expected actual fields/status and confirmed '
                                     'departure from queue.'}],
              'hints': ['Queue disappearance is not successful completion; shell functions/Bash '
                        'syntax are not automatically a /bin/sh environment; no promised mail.',
                        'Use the actual dynamically captured job ID and successful owner-matched '
                        'queue queries; a command failure is not an empty queue.',
                        'Inspect actual result ownership, bytes and exit status; cancel only '
                        'positively matched pending work before exact rollback.'],
              'review': ['I demonstrated the selected mode’s facts, actual identities/results and '
                         'an incorrect interpretation or attempt.',
                         'I can separate queueing, execution, access policy and self-reviewed '
                         'reasoning. Completion is unscored and not automatic verification.',
                         'I removed only positively matched owned jobs, restored any exact policy '
                         'fixture and retained evidence; no authentication or host changes.'],
              'coverage': 'LPIC-1 active v5.0 partial 108.2 at execution; 105.2 status: '
                          'reinforcement. No full objective, automatic assessment or endorsement. '
                          'The plan’s 107.2 at tags were corrected to active108.2;107.2 concerns '
                          'display/X11.'},
  'entry': {'id': 'real-linux-foundation-at-execution',
            'resource': 'real-linux-foundation-at-execution.json',
            'description': 'Observe /bin/sh execution, captured environment/cwd/umask and actual '
                           'successful or failed result.',
            'objectives': ['108.2 at execution', '105.2 status: reinforcement'],
            'troubleshooting': ['Queue disappearance is not successful completion; shell '
                                'functions/Bash syntax are not automatically a /bin/sh '
                                'environment; no promised mail.',
                                'Direct sudo -u practice-user is not authorized by the root-only '
                                'guest sudo rule. Use the displayed root-authorized runuser; never '
                                'change sudo/PAM or enter/create passwords.'],
            'cleanup': ['Before leaving, inspect only each recorded job ID using its successful '
                        'owner query plus saved body/path/owner evidence. If still queued, cancel '
                        'that exact owned ID; if a job may be running, wait up to150s for its '
                        'bounded result/exit. Do not remove its workspace while it can write. '
                        'Unknown ownership requires refusal, not broad cleanup.',
                        'For at-access perform only the displayed SHA/type/mode guarded removal of '
                        'the known allow fixture and byte-check original deny/auth/sudo '
                        'fingerprints. Preserve pre-created practice users and root snapshots; no '
                        'account deletion or PAM editing.',
                        'Keep the exact private workspace as evidence; no recursive deletion, '
                        'spool edits or helper-state pruning. Repeated setup refuses existing '
                        'originals; interruption does not permit replacing a fixture. Reset '
                        'retains the previous disk; Resume restores disk, not RAM or jobs.'],
            'materials': ['Fresh Learn or Challenge setup: w=$(mktemp -d '
                          '"$HOME/foundation-at-execution.XXXXXX") && cd "$w" && umask 077; here() '
                          '{ case "$w" in "$HOME"/foundation-at-execution.??????) ;; *) return '
                          '19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" '
                          '&& test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" '
                          '|| return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' '
                          '"$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; '
                          'esac; }; here && test "$(df -B1 --output=avail / | tail -1)" -ge '
                          '1073741824 && systemctl is-active atd && pwd',
                          'For Resume set w to its recorded path and restore these definitions, '
                          'not mktemp or a new incident: here() { case "$w" in '
                          '"$HOME"/foundation-at-execution.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = '
                          '"$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { here && test '
                          '"${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test "$(stat -c '
                          '%U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" || return '
                          '19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); case '
                          '"$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }',
                          'Challenge starting fault, not repair: challenge_fixture() { here && '
                          'fresh "$w/job.sh" && cat > job.sh <<\'LL_JOB\'\n'
                          '#!/bin/sh\n'
                          'umask 077 || exit 90\n'
                          'ulimit -f 8 || exit 91\n'
                          'test ! -e result && test ! -L result || exit 89\n'
                          'set -C || exit 92\n'
                          '{\n'
                          ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 " hard=" '
                          "$5}' /proc/self/limits\n"
                          " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
                          '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" '
                          '"$(pwd -P)" "$(umask)"; printf "LANG=%s\\nLC_ALL=%s\\n" "$LANG" '
                          '"$LC_ALL"; test "$LANG" = C && test "$LC_ALL" = C && printf '
                          '"bounded-job-complete\\n"\'\n'
                          ' rc=$?\n'
                          ' printf \'exit=%s\\n\' "$rc"\n'
                          '} > result 2>&1\n'
                          'exit "$rc"\n'
                          'LL_JOB\n'
                          'creation_rc=$?; test "$creation_rc" = 0 || return 19;\n'
                          'here && fresh "$w/result" && regular "$w/job.sh" && fresh '
                          '"$w/failed-queued.log" && env LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 '
                          '/usr/bin/at -M -f "$w/job.sh" now + 1 minute > failed-queued.log 2>&1 '
                          '&& jobid "$w/failed-queued.log" && printf "Failed-attempt job=%s\\n" '
                          '"$job"; }; challenge_fixture. Observe its actual exit1, preserve '
                          'failed-result, and retry with the required captured C environment; '
                          'never replace prior evidence.',
                          'Independent selected-mode outcome: Repair the prepared wrong captured '
                          'locale in a distinct one-off retry. Preserve the first actual '
                          'exit1/result, submit C locale and prove actual UID/cwd/umask/file '
                          'limit/content/exit0 despite a later different display locale. A '
                          'vanished queue row is insufficient. Use the supplied6s finite body and '
                          'keep originals. No keyword score or host/remote effects. Fixed handover '
                          'bytes and summer offset remain as described in the incident.'],
            'observations': ['Actual job UID/cwd/umask, exact bytes/status, failed job retained, '
                             '6s child timeout and <=150s observation deadline.',
                             'Successful owner query, actual result/footer/UID/bytes where '
                             'executed; reasoning self-reviewed.'],
            'questions': ['What proves this specific action and what remains uncertain?',
                          'Queue disappearance is not successful completion; shell functions/Bash '
                          'syntax are not automatically a /bin/sh environment; no promised mail.'],
            'limitations': ['No runtime network/mail or credentials. at -M prevents mail delivery. '
                            '/bin/sh is not an interactive Bash session; queueing does not prove '
                            'PAM/account execution. Locked passwords and nologin do not prohibit '
                            'authorized root runuser.',
                            'One finite job at a time; child6s plus2s grace, output4KiB, '
                            'observation150s. Cancellation-only lesson waits130s after submission; '
                            'every utility query10s where bounded. At most64KiB input/256KiB '
                            'practice output, observed1GiB guest free admission; not a quota. Root '
                            'can override guest limits.',
                            'No automatically scored reasoning, preserved RAM/jobs on Resume, '
                            'physical-keyboard or accessibility certification.']},
  'resource_sha256': 'a841728e671d7d2ce5fc62e25af6001637f1ee8c0ca17ad9a29fdcf83d944ab6',
  'entry_sha256': '7c19c2a069b599a0a93849aaf3616237ffab494b2e42563fdafef59a939719c9',
  'learn': ['w=$(mktemp -d "$HOME/foundation-at-execution.XXXXXX") && cd "$w" && umask 077; here() '
            '{ case "$w" in "$HOME"/foundation-at-execution.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
            '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" || return 19; '
            'job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); case "$job" in '
            '\'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }; here && test "$(df -B1 '
            '--output=avail / | tail -1)" -ge 1073741824 && systemctl is-active atd && pwd',
            'here && fresh "$w/job.sh" && cat > job.sh <<\'LL_JOB\'\n'
            '#!/bin/sh\n'
            'umask 077 || exit 90\n'
            'ulimit -f 8 || exit 91\n'
            'test ! -e result && test ! -L result || exit 89\n'
            'set -C || exit 92\n'
            '{\n'
            ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 " hard=" $5}\' '
            '/proc/self/limits\n'
            " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
            '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" "$(pwd -P)" '
            '"$(umask)"; printf "LANG=%s\\nLC_ALL=%s\\n" "$LANG" "$LC_ALL"; test "$LANG" = C && '
            'test "$LC_ALL" = C && printf "bounded-job-complete\\n"\'\n'
            ' rc=$?\n'
            ' printf \'exit=%s\\n\' "$rc"\n'
            '} > result 2>&1\n'
            'exit "$rc"\n'
            'LL_JOB',
            'here && fresh "$w/result" && regular "$w/job.sh" && fresh "$w/failed-queued.log" && '
            'env LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 /usr/bin/at -M -f "$w/job.sh" now + 1 minute '
            '> failed-queued.log 2>&1 && jobid "$w/failed-queued.log" && printf "Failed-attempt '
            'job=%s\\n" "$job"',
            'foundation_step() { here && jobid "$w/failed-queued.log" || return 19; deadline=$(( '
            '$(date +%s)+150 )); while ! grep -Fxq exit=1 "$w/result" 2>/dev/null; do test "$(date '
            '+%s)" -lt "$deadline" || return 19; sleep 1; done; regular "$w/result" && grep -Fx '
            'identity=learner result && grep -Fx LANG=de_DE.UTF-8 result && fresh '
            '"$w/failed-result" && mv -- result failed-result && regular "$w/failed-result" || '
            'return 19; while :; do fresh "$w/failed-queue-current.txt" || regular '
            '"$w/failed-queue-current.txt" || return 19; atq > failed-queue-current.txt || return '
            '19; if awk -v id="$job" \'$1==id {f=1} END {exit !f}\' failed-queue-current.txt; then '
            'test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; else break; fi; done; cat '
            'failed-result; }; foundation_step',
            'here && fresh "$w/result" && regular "$w/job.sh" && fresh "$w/queued.log" && env '
            'LANG=C LC_ALL=C /usr/bin/at -M -f "$w/job.sh" now + 1 minute > queued.log 2>&1 && '
            'jobid "$w/queued.log" && printf "Recorded job=%s workspace=%s\\n" "$job" "$w"',
            'here && fresh "$w/interactive-after.txt" && env LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 '
            'locale > interactive-after.txt && cat interactive-after.txt',
            'foundation_step() { here && jobid "$w/queued.log" || return 19; deadline=$(( $(date '
            '+%s)+150 )); while ! grep -Fxq exit=0 "$w/result" 2>/dev/null; do test "$(date +%s)" '
            '-lt "$deadline" || return 19; sleep 1; done; regular "$w/result" && test "$(wc -c < '
            'result)" -le 4096 && grep -Fx identity=learner result && grep -Fx "uid=$(id -u)" '
            'result && grep -Fx "cwd=$w" result && grep -Fx umask=0077 result && grep -Fx LANG=C '
            'result && grep -Fx LC_ALL=C result && grep -Fx "file_limit_soft=4096 hard=4096" '
            'result && grep -Fx bounded-job-complete result || return 19; while :; do fresh '
            '"$w/queue-current.txt" || regular "$w/queue-current.txt" || return 19; atq > '
            'queue-current.txt || return 19; if awk -v id="$job" \'$1==id {f=1} END {exit !f}\' '
            'queue-current.txt; then test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; '
            'else break; fi; done; cat result; }; foundation_step'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-at-execution.XXXXXX") && cd "$w" && umask 077; '
                'here() { case "$w" in "$HOME"/foundation-at-execution.??????) ;; *) return 19;; '
                'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a '
                '"$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; '
                'jobid() { regular "$1" || return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ '
                '{print $2}\' "$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt '
                '0;; esac; }; here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 '
                '&& systemctl is-active atd && pwd',
                'challenge_fixture() { here && fresh "$w/job.sh" && cat > job.sh <<\'LL_JOB\'\n'
                '#!/bin/sh\n'
                'umask 077 || exit 90\n'
                'ulimit -f 8 || exit 91\n'
                'test ! -e result && test ! -L result || exit 89\n'
                'set -C || exit 92\n'
                '{\n'
                ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 " hard=" $5}\' '
                '/proc/self/limits\n'
                " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
                '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" "$(pwd -P)" '
                '"$(umask)"; printf "LANG=%s\\nLC_ALL=%s\\n" "$LANG" "$LC_ALL"; test "$LANG" = C '
                '&& test "$LC_ALL" = C && printf "bounded-job-complete\\n"\'\n'
                ' rc=$?\n'
                ' printf \'exit=%s\\n\' "$rc"\n'
                '} > result 2>&1\n'
                'exit "$rc"\n'
                'LL_JOB\n'
                'creation_rc=$?; test "$creation_rc" = 0 || return 19;\n'
                'here && fresh "$w/result" && regular "$w/job.sh" && fresh "$w/failed-queued.log" '
                '&& env LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 /usr/bin/at -M -f "$w/job.sh" now + 1 '
                'minute > failed-queued.log 2>&1 && jobid "$w/failed-queued.log" && printf '
                '"Failed-attempt job=%s\\n" "$job"; }; challenge_fixture',
                'foundation_step() { here && jobid "$w/failed-queued.log" || return 19; '
                'deadline=$(( $(date +%s)+150 )); while ! grep -Fxq exit=1 "$w/result" '
                '2>/dev/null; do test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; done; '
                'regular "$w/result" && grep -Fx identity=learner result && grep -Fx '
                'LANG=de_DE.UTF-8 result && fresh "$w/failed-result" && mv -- result failed-result '
                '&& regular "$w/failed-result" || return 19; while :; do fresh '
                '"$w/failed-queue-current.txt" || regular "$w/failed-queue-current.txt" || return '
                '19; atq > failed-queue-current.txt || return 19; if awk -v id="$job" \'$1==id '
                '{f=1} END {exit !f}\' failed-queue-current.txt; then test "$(date +%s)" -lt '
                '"$deadline" || return 19; sleep 1; else break; fi; done; cat failed-result; }; '
                'foundation_step',
                'here && fresh "$w/result" && regular "$w/job.sh" && fresh "$w/queued.log" && env '
                'LANG=C LC_ALL=C /usr/bin/at -M -f "$w/job.sh" now + 1 minute > queued.log 2>&1 && '
                'jobid "$w/queued.log" && printf "Recorded job=%s workspace=%s\\n" "$job" "$w"',
                'here && fresh "$w/interactive-after.txt" && env LANG=de_DE.UTF-8 '
                'LC_ALL=de_DE.UTF-8 locale > interactive-after.txt && cat interactive-after.txt',
                'foundation_step() { here && jobid "$w/queued.log" || return 19; deadline=$(( '
                '$(date +%s)+150 )); while ! grep -Fxq exit=0 "$w/result" 2>/dev/null; do test '
                '"$(date +%s)" -lt "$deadline" || return 19; sleep 1; done; regular "$w/result" && '
                'test "$(wc -c < result)" -le 4096 && grep -Fx identity=learner result && grep -Fx '
                '"uid=$(id -u)" result && grep -Fx "cwd=$w" result && grep -Fx umask=0077 result '
                '&& grep -Fx LANG=C result && grep -Fx LC_ALL=C result && grep -Fx '
                '"file_limit_soft=4096 hard=4096" result && grep -Fx bounded-job-complete result '
                '|| return 19; while :; do fresh "$w/queue-current.txt" || regular '
                '"$w/queue-current.txt" || return 19; atq > queue-current.txt || return 19; if awk '
                '-v id="$job" \'$1==id {f=1} END {exit !f}\' queue-current.txt; then test "$(date '
                '+%s)" -lt "$deadline" || return 19; sleep 1; else break; fi; done; cat result; }; '
                'foundation_step'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': ['static_negative() { here && fresh "$w/job.sh" && printf "%s\\n" '
                           'collision-preserved > "job.sh" || return 19; foundation_collision() { '
                           'challenge_fixture() { here && fresh "$w/job.sh" && cat > job.sh '
                           "<<'LL_JOB'\n"
                           '#!/bin/sh\n'
                           'umask 077 || exit 90\n'
                           'ulimit -f 8 || exit 91\n'
                           'test ! -e result && test ! -L result || exit 89\n'
                           'set -C || exit 92\n'
                           '{\n'
                           ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 " hard=" '
                           "$5}' /proc/self/limits\n"
                           " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
                           '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" '
                           '"$(pwd -P)" "$(umask)"; printf "LANG=%s\\nLC_ALL=%s\\n" "$LANG" '
                           '"$LC_ALL"; test "$LANG" = C && test "$LC_ALL" = C && printf '
                           '"bounded-job-complete\\n"\'\n'
                           ' rc=$?\n'
                           ' printf \'exit=%s\\n\' "$rc"\n'
                           '} > result 2>&1\n'
                           'exit "$rc"\n'
                           'LL_JOB\n'
                           'creation_rc=$?; test "$creation_rc" = 0 || return 19;\n'
                           'here && fresh "$w/result" && regular "$w/job.sh" && fresh '
                           '"$w/failed-queued.log" && env LANG=de_DE.UTF-8 LC_ALL=de_DE.UTF-8 '
                           '/usr/bin/at -M -f "$w/job.sh" now + 1 minute > failed-queued.log 2>&1 '
                           '&& jobid "$w/failed-queued.log" && printf "Failed-attempt job=%s\\n" '
                           '"$job"; }; challenge_fixture\n'
                           '}; if foundation_collision; then return 1; else test $? -ne 0 || '
                           'return 19; fi && regular "$w/job.sh" && grep -Fx collision-preserved '
                           '"job.sh" && test ! -e "$w/failed-queued.log" && test ! -e "$w/good.xz" '
                           '&& test ! -e "$w/truncated.xz" && rm -- "job.sh"; }; static_negative'],
  'negative_after_job': ['here && regular "$w/job.sh" && fresh "$w/result" && printf "%s\\n" '
                         'retained-result > result && fresh "$w/result-collision-error.txt" && '
                         '(env LANG=C LC_ALL=C timeout -k 1s 10s /bin/sh "$w/job.sh" > '
                         'result-collision-error.txt 2>&1; test $? = 89) && grep -Fx '
                         'retained-result result && regular "$w/result" && rm -- result']},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-at-access',
              'content_version': '1.0.0',
              'title': 'Test scheduler access as the intended identity',
              'goal': 'Explain allow-file precedence, deny-file fallback and separate PAM/account '
                      'restrictions.',
              'challenge': 'Begin with the documented absent allow file and root:daemon0640 deny '
                           'file. Make a reversible allow fixture admitting learner and '
                           'll-at-allow but not ll-at-deny; prove specific admission/denial and '
                           'owned cancellation without altering passwords/PAM/sudo/accounts. '
                           'Restore exact original policy; do not claim queue admission alone '
                           'proves execution. Demonstrate a real finite successful job as '
                           'll-at-allow, retain its UID/cwd/status/owned bytes and remove only its '
                           'exact completed workspace. Queue admission is not completion.',
              'steps': [{'command': 'w=$(mktemp -d "$HOME/foundation-at-access.XXXXXX") && cd "$w" '
                                    '&& umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-at-access.??????) ;; *) return 19;; esac; '
                                    'test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                                    'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" '
                                    '&& test "$(stat -c %U:%a "$w")" = learner:700; }; fresh() { '
                                    'here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L '
                                    '"$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                                    '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = '
                                    'learner:600:1; }; jobid() { regular "$1" || return 19; '
                                    'job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); '
                                    'case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt '
                                    '0;; esac; }; here && test "$(df -B1 --output=avail / | tail '
                                    '-1)" -ge 1073741824 && systemctl is-active atd && pwd',
                         'explanation': 'Record the private path/definitions. Refuse collisions '
                                        'and insufficient space; Resume reuses the recorded '
                                        'workspace, not a new job.',
                         'expected': 'Owned700 workspace, actual atd and observed1GiB reserve.'},
                        {'command': 'foundation_step() { here && fresh "$w/policy-before.sha" && '
                                    'test ! -e /etc/at.allow && test ! -L /etc/at.allow && test -f '
                                    '/etc/at.deny && test ! -L /etc/at.deny && test "$(stat -c '
                                    '%U:%G:%a:%h /etc/at.deny)" = root:daemon:640:1 || return 19; '
                                    'rw=$(sudo mktemp -d /var/tmp/ll-at-policy.XXXXXX) || return '
                                    '19; case "$rw" in /var/tmp/ll-at-policy.??????) ;; *) return '
                                    '19;; esac; sudo cp -p /etc/at.deny "$rw/deny.before" && sudo '
                                    'sha256sum /etc/passwd /etc/shadow /etc/group /etc/sudoers '
                                    '/etc/sudoers.d/learning-lab /etc/at.deny > policy-before.sha '
                                    '&& printf "Root snapshot=%s\\n" "$rw" && sudo passwd -S '
                                    'll-at-allow && sudo passwd -S ll-at-deny && getent passwd '
                                    'll-at-allow ll-at-deny; }; foundation_step',
                         'explanation': 'These pre-created identities have locked passwords and '
                                        'nologin shells. Root-authorized runuser can test '
                                        'scheduler policy without changing either restriction.',
                         'expected': 'Original policy/auth hashes and protected root snapshot.'},
                        {'command': 'here && fresh "$w/allow-fixture.sha" && test ! -e '
                                    '/etc/at.allow && test ! -L /etc/at.allow && printf '
                                    '"learner\\nll-at-allow\\n" | sudo tee /etc/at.allow '
                                    '>/dev/null && sudo chown root:root /etc/at.allow && sudo '
                                    'chmod 0644 /etc/at.allow && sha256sum /etc/at.allow > '
                                    'allow-fixture.sha',
                         'explanation': 'Create only the declared allow list. Its presence takes '
                                        'precedence over deny; inspect actual admission as the '
                                        'intended identity, not root.',
                         'expected': 'Learner and ll-at-allow listed, ll-at-deny not listed.'},
                        {'command': 'foundation_step() { here && fresh "$w/denied.txt" || return '
                                    "19; if printf '/usr/bin/true\\n' | sudo /usr/sbin/runuser -u "
                                    'll-at-deny -- /usr/bin/at -M now + 2 minutes > denied.txt '
                                    '2>&1; then return 1; else test $? = 1 && grep -F "do not have '
                                    'permission" denied.txt; fi; }; foundation_step',
                         'explanation': 'Specific queue-policy refusal is separate from password '
                                        'locking, account expiry or interactive-shell restriction. '
                                        'Do not change PAM/passwords to make it pass.',
                         'expected': 'Actual deny identity refusal.'},
                        {'command': 'foundation_step() { here && fresh "$w/allowed.log" && fresh '
                                    '"$w/allow-queue.txt" && fresh "$w/wrong-owner.txt" && fresh '
                                    '"$w/allow-after.txt" || return 19; printf '
                                    "'/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-allow -- "
                                    '/usr/bin/at -M now + 2 minutes > allowed.log 2>&1 && jobid '
                                    '"$w/allowed.log" && sudo /usr/sbin/runuser -u ll-at-allow -- '
                                    '/usr/bin/atq > allow-queue.txt && awk -v id="$job" \'$1==id '
                                    '&& $NF=="ll-at-allow" {f=1} END {exit !f}\' allow-queue.txt '
                                    '|| return 19; if atrm "$job" > wrong-owner.txt 2>&1; then '
                                    'return 1; else test $? -ne 0 || return 19; fi; sudo '
                                    '/usr/sbin/runuser -u ll-at-allow -- /usr/bin/atrm "$job" && '
                                    'sudo /usr/sbin/runuser -u ll-at-allow -- /usr/bin/atq > '
                                    'allow-after.txt && ! awk -v id="$job" \'$1==id {f=1} END '
                                    "{exit !f}' allow-after.txt; }; foundation_step",
                         'explanation': 'Capture actual ownership, prove learner cannot cancel the '
                                        'other identity’s job, then cancel exactly as its owner. '
                                        'Admission/cancellation does not alone prove execution; '
                                        'the companion execution lesson and developer feasibility '
                                        'record demonstrate that separately.',
                         'expected': 'Owned cancellation and explicit wrong-owner refusal.'},
                        {'command': 'foundation_step() { here && fresh "$w/access-job.sh" || '
                                    'return 19; aw=$(sudo mktemp -d /var/tmp/ll-at-job.XXXXXX) || '
                                    'return 19; case "$aw" in /var/tmp/ll-at-job.??????) ;; *) '
                                    'return 19;; esac; sudo chown ll-at-allow:ll-at-allow "$aw" && '
                                    'test "$(stat -c %U:%G:%a "$aw")" = '
                                    'll-at-allow:ll-at-allow:700 || return 19; cat > access-job.sh '
                                    "<<'LL_ACCESS'\n"
                                    '#!/bin/sh\n'
                                    'umask 077 || exit 90\n'
                                    'ulimit -f 8 || exit 91\n'
                                    'test ! -e result && test ! -L result || exit 89\n'
                                    'set -C || exit 92\n'
                                    '{ /usr/bin/timeout --kill-after=2s 6s /bin/sh -c \'test "$(id '
                                    '-un)" = ll-at-allow && printf '
                                    '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" '
                                    '"$(id -u)" "$(pwd -P)" "$(umask)" && printf '
                                    '"bounded-access-job\\n"\'; rc=$?; printf \'exit=%s\\n\' '
                                    '"$rc"; } > result 2>&1\n'
                                    'exit "$rc"\n'
                                    'LL_ACCESS\n'
                                    'creation_rc=$?; test "$creation_rc" = 0 || return 19;\n'
                                    'regular "$w/access-job.sh" && sudo install -o ll-at-allow -g '
                                    'll-at-allow -m 0600 access-job.sh "$aw/job.sh" && fresh '
                                    '"$w/access-queued.log" && sudo test ! -e "$aw/result" && sudo '
                                    'test ! -L "$aw/result" && sudo /usr/sbin/runuser -u '
                                    'll-at-allow -- /bin/sh -c \'cd "$1" && exec /usr/bin/at -M -f '
                                    '"$1/job.sh" now + 1 minute\' sh "$aw" > access-queued.log '
                                    '2>&1 && jobid "$w/access-queued.log" && printf "Recorded '
                                    'owned workspace=%s job=%s\\n" "$aw" "$job"; }; '
                                    'foundation_step',
                         'explanation': 'Admission alone is not execution. Submit one bounded job '
                                        'from its accessible owner-matched workspace via '
                                        'root-authorized runuser, not by changing its '
                                        'login/password restrictions.',
                         'expected': 'Finite owned job and recorded unique path/ID.'},
                        {'command': 'foundation_step() { here && jobid "$w/access-queued.log" || '
                                    'return 19; case "$aw" in /var/tmp/ll-at-job.??????) ;; *) '
                                    'return 19;; esac; test "$(sudo realpath -e "$aw")" = "$aw" && '
                                    'test "$(stat -c %U:%G:%a "$aw")" = '
                                    'll-at-allow:ll-at-allow:700 || return 19; deadline=$(( $(date '
                                    '+%s)+150 )); while ! sudo grep -Fxq exit=0 "$aw/result" '
                                    '2>/dev/null; do test "$(date +%s)" -lt "$deadline" || return '
                                    '19; sleep 1; done; sudo test -f "$aw/result" && sudo test ! '
                                    '-L "$aw/result" && test "$(sudo stat -c %U:%G:%a:%h '
                                    '"$aw/result")" = ll-at-allow:ll-at-allow:600:1 && test '
                                    '"$(sudo stat -c %s "$aw/result")" -le 4096 && sudo grep -Fx '
                                    'identity=ll-at-allow "$aw/result" && sudo grep -Fx "uid=$(id '
                                    '-u ll-at-allow)" "$aw/result" && sudo grep -Fx "cwd=$aw" '
                                    '"$aw/result" && sudo grep -Fx umask=0077 "$aw/result" && '
                                    'fresh "$w/access-result.txt" && sudo cat "$aw/result" > '
                                    'access-result.txt || return 19; while :; do fresh '
                                    '"$w/access-queue-current.txt" || regular '
                                    '"$w/access-queue-current.txt" || return 19; sudo '
                                    '/usr/sbin/runuser -u ll-at-allow -- atq > '
                                    'access-queue-current.txt || return 19; if awk -v id="$job" '
                                    "'$1==id {f=1} END {exit !f}' access-queue-current.txt; then "
                                    'test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; '
                                    'else break; fi; done; }; foundation_step',
                         'explanation': 'Verify actual successful execution as the locked '
                                        'disposable identity, output/status/UID/cwd/umask and '
                                        'owner-query departure.',
                         'expected': 'Actual ll-at-allow execution, not root output or '
                                     'admission-only proof.'},
                        {'command': 'here && sha256sum -c allow-fixture.sha && sudo test -f '
                                    '"$rw/deny.before" && sudo test ! -L "$rw/deny.before" && test '
                                    '"$(sudo stat -c %U:%G:%a:%h "$rw/deny.before")" = '
                                    'root:daemon:640:1 && sudo cmp /etc/at.deny "$rw/deny.before" '
                                    '&& test "$(stat -c %U:%G:%a:%h /etc/at.allow)" = '
                                    'root:root:644:1 && sudo rm -- /etc/at.allow && sudo sha256sum '
                                    '-c policy-before.sha && test ! -e /etc/at.allow && test ! -L '
                                    '/etc/at.allow',
                         'explanation': 'Restore exact policy by removing only the known '
                                        'byte-matched allow fixture. Keep original deny and '
                                        'identities; no account deletion, shadow or sudo edit.',
                         'expected': 'Original auth/sudo/deny bytes unchanged; allow absent '
                                     'again.'},
                        {'command': 'foundation_step() { here && regular "$w/access-result.txt" || '
                                    'return 19; case "$aw" in /var/tmp/ll-at-job.??????) ;; *) '
                                    'return 19;; esac; test "$(sudo realpath -e "$aw")" = "$aw" && '
                                    'test "$(stat -c %U:%G:%a "$aw")" = '
                                    'll-at-allow:ll-at-allow:700 && sudo test -f "$aw/job.sh" && '
                                    'sudo test ! -L "$aw/job.sh" && test "$(sudo stat -c '
                                    '%U:%G:%a:%h "$aw/job.sh")" = ll-at-allow:ll-at-allow:600:1 && '
                                    'sudo cmp "$w/access-job.sh" "$aw/job.sh" && sudo cmp '
                                    '"$w/access-result.txt" "$aw/result" || return 19; sudo rm -- '
                                    '"$aw/job.sh" "$aw/result" && sudo rmdir -- "$aw"; }; '
                                    'foundation_step',
                         'explanation': 'After successful departure and policy rollback, compare '
                                        'retained script/result then remove only these exact owned '
                                        'files and empty directory. Unknown members cause rmdir '
                                        'refusal; no recursive removal.',
                         'expected': 'Owned output retained in learner workspace, exact temporary '
                                     'owner workspace removed.'}],
              'hints': ['Root bypass is not ordinary-user permission; policy admission does not '
                        'prove PAM/account execution success; never enable passwords to make a '
                        'test pass.',
                        'Use the actual dynamically captured job ID and successful owner-matched '
                        'queue queries; a command failure is not an empty queue.',
                        'Inspect actual result ownership, bytes and exit status; cancel only '
                        'positively matched pending work before exact rollback.'],
              'review': ['I demonstrated the selected mode’s facts, actual identities/results and '
                         'an incorrect interpretation or attempt.',
                         'I can separate queueing, execution, access policy and self-reviewed '
                         'reasoning. Completion is unscored and not automatic verification.',
                         'I removed only positively matched owned jobs, restored any exact policy '
                         'fixture and retained evidence; no authentication or host changes.'],
              'coverage': 'LPIC-1 active v5.0 partial 108.2 at access controls. No full objective, '
                          'automatic assessment or endorsement. The plan’s 107.2 at tags were '
                          'corrected to active108.2;107.2 concerns display/X11.'},
  'entry': {'id': 'real-linux-foundation-at-access',
            'resource': 'real-linux-foundation-at-access.json',
            'description': 'Explain allow-file precedence, deny-file fallback and separate '
                           'PAM/account restrictions.',
            'objectives': ['108.2 at access controls'],
            'troubleshooting': ['Root bypass is not ordinary-user permission; policy admission '
                                'does not prove PAM/account execution success; never enable '
                                'passwords to make a test pass.',
                                'Direct sudo -u practice-user is not authorized by the root-only '
                                'guest sudo rule. Use the displayed root-authorized runuser; never '
                                'change sudo/PAM or enter/create passwords.'],
            'cleanup': ['Before leaving, inspect only each recorded job ID using its successful '
                        'owner query plus saved body/path/owner evidence. If still queued, cancel '
                        'that exact owned ID; if a job may be running, wait up to150s for its '
                        'bounded result/exit. Do not remove its workspace while it can write. '
                        'Unknown ownership requires refusal, not broad cleanup.',
                        'For at-access perform only the displayed SHA/type/mode guarded removal of '
                        'the known allow fixture and byte-check original deny/auth/sudo '
                        'fingerprints. Preserve pre-created practice users and root snapshots; no '
                        'account deletion or PAM editing.',
                        'Keep the exact private workspace as evidence; no recursive deletion, '
                        'spool edits or helper-state pruning. Repeated setup refuses existing '
                        'originals; interruption does not permit replacing a fixture. Reset '
                        'retains the previous disk; Resume restores disk, not RAM or jobs.'],
            'materials': ['Fresh Learn or Challenge setup: w=$(mktemp -d '
                          '"$HOME/foundation-at-access.XXXXXX") && cd "$w" && umask 077; here() { '
                          'case "$w" in "$HOME"/foundation-at-access.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" '
                          '|| return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' '
                          '"$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; '
                          'esac; }; here && test "$(df -B1 --output=avail / | tail -1)" -ge '
                          '1073741824 && systemctl is-active atd && pwd',
                          'For Resume set w to its recorded path and restore these definitions, '
                          'not mktemp or a new incident: here() { case "$w" in '
                          '"$HOME"/foundation-at-access.??????) ;; *) return 19;; esac; test '
                          '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                          '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat '
                          '-c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = '
                          '"$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { here && test '
                          '"${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test "$(stat -c '
                          '%U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" || return '
                          '19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); case '
                          '"$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }',
                          'Challenge starting fixture: foundation_step() { here && fresh '
                          '"$w/policy-before.sha" && test ! -e /etc/at.allow && test ! -L '
                          '/etc/at.allow && test -f /etc/at.deny && test ! -L /etc/at.deny && test '
                          '"$(stat -c %U:%G:%a:%h /etc/at.deny)" = root:daemon:640:1 || return 19; '
                          'rw=$(sudo mktemp -d /var/tmp/ll-at-policy.XXXXXX) || return 19; case '
                          '"$rw" in /var/tmp/ll-at-policy.??????) ;; *) return 19;; esac; sudo cp '
                          '-p /etc/at.deny "$rw/deny.before" && sudo sha256sum /etc/passwd '
                          '/etc/shadow /etc/group /etc/sudoers /etc/sudoers.d/learning-lab '
                          '/etc/at.deny > policy-before.sha && printf "Root snapshot=%s\\n" "$rw" '
                          '&& sudo passwd -S ll-at-allow && sudo passwd -S ll-at-deny && getent '
                          'passwd ll-at-allow ll-at-deny; }; foundation_step',
                          'Independent selected-mode outcome: Begin with the documented absent '
                          'allow file and root:daemon0640 deny file. Make a reversible allow '
                          'fixture admitting learner and ll-at-allow but not ll-at-deny; prove '
                          'specific admission/denial and owned cancellation without altering '
                          'passwords/PAM/sudo/accounts. Restore exact original policy; do not '
                          'claim queue admission alone proves execution. Demonstrate a real finite '
                          'successful job as ll-at-allow, retain its UID/cwd/status/owned bytes '
                          'and remove only its exact completed workspace. Queue admission is not '
                          'completion. No keyword score or host/remote effects. Fixed handover '
                          'bytes and summer offset remain as described in the incident.'],
            'observations': ['Exact policy bytes/modes/owner, queue/run denial and successful UID '
                             'evidence, unaffected learner/auth/sudo fingerprints.',
                             'Successful owner query, actual result/footer/UID/bytes where '
                             'executed; reasoning self-reviewed.'],
            'questions': ['What proves this specific action and what remains uncertain?',
                          'Root bypass is not ordinary-user permission; policy admission does not '
                          'prove PAM/account execution success; never enable passwords to make a '
                          'test pass.'],
            'limitations': ['No runtime network/mail or credentials. at -M prevents mail delivery. '
                            '/bin/sh is not an interactive Bash session; queueing does not prove '
                            'PAM/account execution. Locked passwords and nologin do not prohibit '
                            'authorized root runuser.',
                            'One finite job at a time; child6s plus2s grace, output4KiB, '
                            'observation150s. Cancellation-only lesson waits130s after submission; '
                            'every utility query10s where bounded. At most64KiB input/256KiB '
                            'practice output, observed1GiB guest free admission; not a quota. Root '
                            'can override guest limits.',
                            'No automatically scored reasoning, preserved RAM/jobs on Resume, '
                            'physical-keyboard or accessibility certification.']},
  'resource_sha256': '0f4b628d6fc90dcac64b3a64340b516b07dab753b36c8a272e8993c67b8ff5cc',
  'entry_sha256': '95847a6b55c8f2633f0d708b1716ab2e39c494a5cdb230e853c151273ef77f4e',
  'learn': ['w=$(mktemp -d "$HOME/foundation-at-access.XXXXXX") && cd "$w" && umask 077; here() { '
            'case "$w" in "$HOME"/foundation-at-access.??????) ;; *) return 19;; esac; test '
            '"${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test "$(realpath -e "$w")" = '
            '"$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
            'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; '
            'regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
            '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" || return 19; '
            'job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); case "$job" in '
            '\'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }; here && test "$(df -B1 '
            '--output=avail / | tail -1)" -ge 1073741824 && systemctl is-active atd && pwd',
            'foundation_step() { here && fresh "$w/policy-before.sha" && test ! -e /etc/at.allow '
            '&& test ! -L /etc/at.allow && test -f /etc/at.deny && test ! -L /etc/at.deny && test '
            '"$(stat -c %U:%G:%a:%h /etc/at.deny)" = root:daemon:640:1 || return 19; rw=$(sudo '
            'mktemp -d /var/tmp/ll-at-policy.XXXXXX) || return 19; case "$rw" in '
            '/var/tmp/ll-at-policy.??????) ;; *) return 19;; esac; sudo cp -p /etc/at.deny '
            '"$rw/deny.before" && sudo sha256sum /etc/passwd /etc/shadow /etc/group /etc/sudoers '
            '/etc/sudoers.d/learning-lab /etc/at.deny > policy-before.sha && printf "Root '
            'snapshot=%s\\n" "$rw" && sudo passwd -S ll-at-allow && sudo passwd -S ll-at-deny && '
            'getent passwd ll-at-allow ll-at-deny; }; foundation_step',
            'here && fresh "$w/allow-fixture.sha" && test ! -e /etc/at.allow && test ! -L '
            '/etc/at.allow && printf "learner\\nll-at-allow\\n" | sudo tee /etc/at.allow '
            '>/dev/null && sudo chown root:root /etc/at.allow && sudo chmod 0644 /etc/at.allow && '
            'sha256sum /etc/at.allow > allow-fixture.sha',
            'foundation_step() { here && fresh "$w/denied.txt" || return 19; if printf '
            "'/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-deny -- /usr/bin/at -M now + 2 "
            'minutes > denied.txt 2>&1; then return 1; else test $? = 1 && grep -F "do not have '
            'permission" denied.txt; fi; }; foundation_step',
            'foundation_step() { here && fresh "$w/allowed.log" && fresh "$w/allow-queue.txt" && '
            'fresh "$w/wrong-owner.txt" && fresh "$w/allow-after.txt" || return 19; printf '
            "'/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-allow -- /usr/bin/at -M now + 2 "
            'minutes > allowed.log 2>&1 && jobid "$w/allowed.log" && sudo /usr/sbin/runuser -u '
            'll-at-allow -- /usr/bin/atq > allow-queue.txt && awk -v id="$job" \'$1==id && '
            '$NF=="ll-at-allow" {f=1} END {exit !f}\' allow-queue.txt || return 19; if atrm "$job" '
            '> wrong-owner.txt 2>&1; then return 1; else test $? -ne 0 || return 19; fi; sudo '
            '/usr/sbin/runuser -u ll-at-allow -- /usr/bin/atrm "$job" && sudo /usr/sbin/runuser -u '
            'll-at-allow -- /usr/bin/atq > allow-after.txt && ! awk -v id="$job" \'$1==id {f=1} '
            "END {exit !f}' allow-after.txt; }; foundation_step",
            'foundation_step() { here && fresh "$w/access-job.sh" || return 19; aw=$(sudo mktemp '
            '-d /var/tmp/ll-at-job.XXXXXX) || return 19; case "$aw" in /var/tmp/ll-at-job.??????) '
            ';; *) return 19;; esac; sudo chown ll-at-allow:ll-at-allow "$aw" && test "$(stat -c '
            '%U:%G:%a "$aw")" = ll-at-allow:ll-at-allow:700 || return 19; cat > access-job.sh '
            "<<'LL_ACCESS'\n"
            '#!/bin/sh\n'
            'umask 077 || exit 90\n'
            'ulimit -f 8 || exit 91\n'
            'test ! -e result && test ! -L result || exit 89\n'
            'set -C || exit 92\n'
            '{ /usr/bin/timeout --kill-after=2s 6s /bin/sh -c \'test "$(id -un)" = ll-at-allow && '
            'printf "identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" "$(pwd '
            '-P)" "$(umask)" && printf "bounded-access-job\\n"\'; rc=$?; printf \'exit=%s\\n\' '
            '"$rc"; } > result 2>&1\n'
            'exit "$rc"\n'
            'LL_ACCESS\n'
            'creation_rc=$?; test "$creation_rc" = 0 || return 19;\n'
            'regular "$w/access-job.sh" && sudo install -o ll-at-allow -g ll-at-allow -m 0600 '
            'access-job.sh "$aw/job.sh" && fresh "$w/access-queued.log" && sudo test ! -e '
            '"$aw/result" && sudo test ! -L "$aw/result" && sudo /usr/sbin/runuser -u ll-at-allow '
            '-- /bin/sh -c \'cd "$1" && exec /usr/bin/at -M -f "$1/job.sh" now + 1 minute\' sh '
            '"$aw" > access-queued.log 2>&1 && jobid "$w/access-queued.log" && printf "Recorded '
            'owned workspace=%s job=%s\\n" "$aw" "$job"; }; foundation_step',
            'foundation_step() { here && jobid "$w/access-queued.log" || return 19; case "$aw" in '
            '/var/tmp/ll-at-job.??????) ;; *) return 19;; esac; test "$(sudo realpath -e "$aw")" = '
            '"$aw" && test "$(stat -c %U:%G:%a "$aw")" = ll-at-allow:ll-at-allow:700 || return 19; '
            'deadline=$(( $(date +%s)+150 )); while ! sudo grep -Fxq exit=0 "$aw/result" '
            '2>/dev/null; do test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; done; sudo '
            'test -f "$aw/result" && sudo test ! -L "$aw/result" && test "$(sudo stat -c '
            '%U:%G:%a:%h "$aw/result")" = ll-at-allow:ll-at-allow:600:1 && test "$(sudo stat -c %s '
            '"$aw/result")" -le 4096 && sudo grep -Fx identity=ll-at-allow "$aw/result" && sudo '
            'grep -Fx "uid=$(id -u ll-at-allow)" "$aw/result" && sudo grep -Fx "cwd=$aw" '
            '"$aw/result" && sudo grep -Fx umask=0077 "$aw/result" && fresh "$w/access-result.txt" '
            '&& sudo cat "$aw/result" > access-result.txt || return 19; while :; do fresh '
            '"$w/access-queue-current.txt" || regular "$w/access-queue-current.txt" || return 19; '
            'sudo /usr/sbin/runuser -u ll-at-allow -- atq > access-queue-current.txt || return 19; '
            'if awk -v id="$job" \'$1==id {f=1} END {exit !f}\' access-queue-current.txt; then '
            'test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; else break; fi; done; }; '
            'foundation_step',
            'here && sha256sum -c allow-fixture.sha && sudo test -f "$rw/deny.before" && sudo test '
            '! -L "$rw/deny.before" && test "$(sudo stat -c %U:%G:%a:%h "$rw/deny.before")" = '
            'root:daemon:640:1 && sudo cmp /etc/at.deny "$rw/deny.before" && test "$(stat -c '
            '%U:%G:%a:%h /etc/at.allow)" = root:root:644:1 && sudo rm -- /etc/at.allow && sudo '
            'sha256sum -c policy-before.sha && test ! -e /etc/at.allow && test ! -L /etc/at.allow',
            'foundation_step() { here && regular "$w/access-result.txt" || return 19; case "$aw" '
            'in /var/tmp/ll-at-job.??????) ;; *) return 19;; esac; test "$(sudo realpath -e '
            '"$aw")" = "$aw" && test "$(stat -c %U:%G:%a "$aw")" = ll-at-allow:ll-at-allow:700 && '
            'sudo test -f "$aw/job.sh" && sudo test ! -L "$aw/job.sh" && test "$(sudo stat -c '
            '%U:%G:%a:%h "$aw/job.sh")" = ll-at-allow:ll-at-allow:600:1 && sudo cmp '
            '"$w/access-job.sh" "$aw/job.sh" && sudo cmp "$w/access-result.txt" "$aw/result" || '
            'return 19; sudo rm -- "$aw/job.sh" "$aw/result" && sudo rmdir -- "$aw"; }; '
            'foundation_step'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-at-access.XXXXXX") && cd "$w" && umask 077; '
                'here() { case "$w" in "$HOME"/foundation-at-access.??????) ;; *) return 19;; '
                'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
                '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a '
                '"$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e '
                '"$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f '
                '"$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; '
                'jobid() { regular "$1" || return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ '
                '{print $2}\' "$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt '
                '0;; esac; }; here && test "$(df -B1 --output=avail / | tail -1)" -ge 1073741824 '
                '&& systemctl is-active atd && pwd',
                'foundation_step() { here && fresh "$w/policy-before.sha" && test ! -e '
                '/etc/at.allow && test ! -L /etc/at.allow && test -f /etc/at.deny && test ! -L '
                '/etc/at.deny && test "$(stat -c %U:%G:%a:%h /etc/at.deny)" = root:daemon:640:1 || '
                'return 19; rw=$(sudo mktemp -d /var/tmp/ll-at-policy.XXXXXX) || return 19; case '
                '"$rw" in /var/tmp/ll-at-policy.??????) ;; *) return 19;; esac; sudo cp -p '
                '/etc/at.deny "$rw/deny.before" && sudo sha256sum /etc/passwd /etc/shadow '
                '/etc/group /etc/sudoers /etc/sudoers.d/learning-lab /etc/at.deny > '
                'policy-before.sha && printf "Root snapshot=%s\\n" "$rw" && sudo passwd -S '
                'll-at-allow && sudo passwd -S ll-at-deny && getent passwd ll-at-allow ll-at-deny; '
                '}; foundation_step',
                'here && fresh "$w/allow-fixture.sha" && test ! -e /etc/at.allow && test ! -L '
                '/etc/at.allow && printf "learner\\nll-at-allow\\n" | sudo tee /etc/at.allow '
                '>/dev/null && sudo chown root:root /etc/at.allow && sudo chmod 0644 /etc/at.allow '
                '&& sha256sum /etc/at.allow > allow-fixture.sha',
                'foundation_step() { here && fresh "$w/denied.txt" || return 19; if printf '
                "'/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-deny -- /usr/bin/at -M now + "
                '2 minutes > denied.txt 2>&1; then return 1; else test $? = 1 && grep -F "do not '
                'have permission" denied.txt; fi; }; foundation_step',
                'foundation_step() { here && fresh "$w/allowed.log" && fresh "$w/allow-queue.txt" '
                '&& fresh "$w/wrong-owner.txt" && fresh "$w/allow-after.txt" || return 19; printf '
                "'/usr/bin/true\\n' | sudo /usr/sbin/runuser -u ll-at-allow -- /usr/bin/at -M now "
                '+ 2 minutes > allowed.log 2>&1 && jobid "$w/allowed.log" && sudo '
                '/usr/sbin/runuser -u ll-at-allow -- /usr/bin/atq > allow-queue.txt && awk -v '
                'id="$job" \'$1==id && $NF=="ll-at-allow" {f=1} END {exit !f}\' allow-queue.txt || '
                'return 19; if atrm "$job" > wrong-owner.txt 2>&1; then return 1; else test $? -ne '
                '0 || return 19; fi; sudo /usr/sbin/runuser -u ll-at-allow -- /usr/bin/atrm "$job" '
                '&& sudo /usr/sbin/runuser -u ll-at-allow -- /usr/bin/atq > allow-after.txt && ! '
                'awk -v id="$job" \'$1==id {f=1} END {exit !f}\' allow-after.txt; }; '
                'foundation_step',
                'foundation_step() { here && fresh "$w/access-job.sh" || return 19; aw=$(sudo '
                'mktemp -d /var/tmp/ll-at-job.XXXXXX) || return 19; case "$aw" in '
                '/var/tmp/ll-at-job.??????) ;; *) return 19;; esac; sudo chown '
                'll-at-allow:ll-at-allow "$aw" && test "$(stat -c %U:%G:%a "$aw")" = '
                "ll-at-allow:ll-at-allow:700 || return 19; cat > access-job.sh <<'LL_ACCESS'\n"
                '#!/bin/sh\n'
                'umask 077 || exit 90\n'
                'ulimit -f 8 || exit 91\n'
                'test ! -e result && test ! -L result || exit 89\n'
                'set -C || exit 92\n'
                '{ /usr/bin/timeout --kill-after=2s 6s /bin/sh -c \'test "$(id -un)" = ll-at-allow '
                '&& printf "identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" '
                '"$(pwd -P)" "$(umask)" && printf "bounded-access-job\\n"\'; rc=$?; printf '
                '\'exit=%s\\n\' "$rc"; } > result 2>&1\n'
                'exit "$rc"\n'
                'LL_ACCESS\n'
                'creation_rc=$?; test "$creation_rc" = 0 || return 19;\n'
                'regular "$w/access-job.sh" && sudo install -o ll-at-allow -g ll-at-allow -m 0600 '
                'access-job.sh "$aw/job.sh" && fresh "$w/access-queued.log" && sudo test ! -e '
                '"$aw/result" && sudo test ! -L "$aw/result" && sudo /usr/sbin/runuser -u '
                'll-at-allow -- /bin/sh -c \'cd "$1" && exec /usr/bin/at -M -f "$1/job.sh" now + 1 '
                'minute\' sh "$aw" > access-queued.log 2>&1 && jobid "$w/access-queued.log" && '
                'printf "Recorded owned workspace=%s job=%s\\n" "$aw" "$job"; }; foundation_step',
                'foundation_step() { here && jobid "$w/access-queued.log" || return 19; case "$aw" '
                'in /var/tmp/ll-at-job.??????) ;; *) return 19;; esac; test "$(sudo realpath -e '
                '"$aw")" = "$aw" && test "$(stat -c %U:%G:%a "$aw")" = ll-at-allow:ll-at-allow:700 '
                '|| return 19; deadline=$(( $(date +%s)+150 )); while ! sudo grep -Fxq exit=0 '
                '"$aw/result" 2>/dev/null; do test "$(date +%s)" -lt "$deadline" || return 19; '
                'sleep 1; done; sudo test -f "$aw/result" && sudo test ! -L "$aw/result" && test '
                '"$(sudo stat -c %U:%G:%a:%h "$aw/result")" = ll-at-allow:ll-at-allow:600:1 && '
                'test "$(sudo stat -c %s "$aw/result")" -le 4096 && sudo grep -Fx '
                'identity=ll-at-allow "$aw/result" && sudo grep -Fx "uid=$(id -u ll-at-allow)" '
                '"$aw/result" && sudo grep -Fx "cwd=$aw" "$aw/result" && sudo grep -Fx umask=0077 '
                '"$aw/result" && fresh "$w/access-result.txt" && sudo cat "$aw/result" > '
                'access-result.txt || return 19; while :; do fresh "$w/access-queue-current.txt" '
                '|| regular "$w/access-queue-current.txt" || return 19; sudo /usr/sbin/runuser -u '
                'll-at-allow -- atq > access-queue-current.txt || return 19; if awk -v id="$job" '
                '\'$1==id {f=1} END {exit !f}\' access-queue-current.txt; then test "$(date +%s)" '
                '-lt "$deadline" || return 19; sleep 1; else break; fi; done; }; foundation_step',
                'here && sha256sum -c allow-fixture.sha && sudo test -f "$rw/deny.before" && sudo '
                'test ! -L "$rw/deny.before" && test "$(sudo stat -c %U:%G:%a:%h '
                '"$rw/deny.before")" = root:daemon:640:1 && sudo cmp /etc/at.deny '
                '"$rw/deny.before" && test "$(stat -c %U:%G:%a:%h /etc/at.allow)" = '
                'root:root:644:1 && sudo rm -- /etc/at.allow && sudo sha256sum -c '
                'policy-before.sha && test ! -e /etc/at.allow && test ! -L /etc/at.allow',
                'foundation_step() { here && regular "$w/access-result.txt" || return 19; case '
                '"$aw" in /var/tmp/ll-at-job.??????) ;; *) return 19;; esac; test "$(sudo realpath '
                '-e "$aw")" = "$aw" && test "$(stat -c %U:%G:%a "$aw")" = '
                'll-at-allow:ll-at-allow:700 && sudo test -f "$aw/job.sh" && sudo test ! -L '
                '"$aw/job.sh" && test "$(sudo stat -c %U:%G:%a:%h "$aw/job.sh")" = '
                'll-at-allow:ll-at-allow:600:1 && sudo cmp "$w/access-job.sh" "$aw/job.sh" && sudo '
                'cmp "$w/access-result.txt" "$aw/result" || return 19; sudo rm -- "$aw/job.sh" '
                '"$aw/result" && sudo rmdir -- "$aw"; }; foundation_step'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []},
 {'family': 'foundation',
  'image_id': 'debian13-foundation-admin-local-v1',
  'content': {'id': 'real-linux-foundation-localization-handover',
              'content_version': '1.0.0',
              'title': 'Deliver a localized offline job handover',
              'goal': 'Transfer locale, encoding, time and one-off execution decisions without '
                      'repeating a guided repair.',
              'challenge': 'Independently deliver exact factual results from a different dataset, '
                           'a successful bounded job and a readable handover. Retain actual IDs, '
                           'owners, statuses, contents and failed evidence. Never fixed job '
                           'numbers or broad cancellation; completion remains self-reviewed.',
              'steps': [{'command': 'w=$(mktemp -d '
                                    '"$HOME/foundation-localization-handover.XXXXXX") && cd "$w" '
                                    '&& umask 077; here() { case "$w" in '
                                    '"$HOME"/foundation-localization-handover.??????) ;; *) return '
                                    '19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! '
                                    '-L "$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd '
                                    '-P)" = "$w" && test "$(stat -c %U:%a "$w")" = learner:700; }; '
                                    'fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && '
                                    'test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" '
                                    '&& test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h '
                                    '"$1")" = learner:600:1; }; jobid() { regular "$1" || return '
                                    '19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' '
                                    '"$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test '
                                    '"$job" -gt 0;; esac; }; here && test "$(df -B1 --output=avail '
                                    '/ | tail -1)" -ge 1073741824 && systemctl is-active atd && '
                                    'pwd',
                         'explanation': 'Record the private path/definitions. Refuse collisions '
                                        'and insufficient space; Resume reuses the recorded '
                                        'workspace, not a new job.',
                         'expected': 'Owned700 workspace, actual atd and observed1GiB reserve.'},
                        {'command': 'here && fresh "$w/incident.txt" && printf "Source bytes: '
                                    'ISO-8859-1 cafe-with-e-acute plus newline.\\nInstant: '
                                    '2026-07-01 12:00:00 UTC.\\nRequired report: UTF-8, UTC '
                                    'instant and Berlin offset; capture C-locale job.\\nWrong '
                                    'handover calls the source UTF-8 and assumes Berlin is always '
                                    '+0100.\\n" > incident.txt && fresh "$w/source-latin1.txt" && '
                                    'printf "caf\\351\\n" > source-latin1.txt && fresh '
                                    '"$w/source.sha" && sha256sum source-latin1.txt > source.sha '
                                    '&& cat incident.txt',
                         'explanation': 'Use this tiny different dataset and deliberately '
                                        'misleading report. Facts have independent byte/time '
                                        'expectations; language/causal reasoning remains '
                                        'self-reviewed.',
                         'expected': 'Original incident and encoding evidence retained.'},
                        {'command': 'foundation_step() { here && fresh "$w/wrong-partial.txt" && '
                                    'fresh "$w/wrong-error.txt" || return 19; if timeout -k 1s 10s '
                                    'iconv -f UTF-8 -t UTF-8 source-latin1.txt > wrong-partial.txt '
                                    '2> wrong-error.txt; then return 1; else test $? = 1 && test '
                                    '-s wrong-error.txt && sha256sum -c source.sha; fi; }; '
                                    'foundation_step',
                         'explanation': 'Retain a wrong encoding hypothesis and partial output; '
                                        'failure does not authorize discarding the original.',
                         'expected': 'Actual strict rejection and original preserved.'},
                        {'command': 'here && fresh "$w/recovered-utf8.txt" && fresh '
                                    '"$w/expected-utf8.txt" && timeout -k 1s 10s iconv -f '
                                    'ISO-8859-1 -t UTF-8 source-latin1.txt > recovered-utf8.txt && '
                                    'printf "caf\\303\\251\\n" > expected-utf8.txt && cmp '
                                    'recovered-utf8.txt expected-utf8.txt && fresh "$w/zone.txt" '
                                    '&& env TZ=Europe/Berlin LC_ALL=C date -d "2026-07-01 12:00:00 '
                                    'UTC" "+%F %T %z" > zone.txt && grep -Fx "2026-07-01 14:00:00 '
                                    '+0200" zone.txt && sha256sum -c source.sha',
                         'explanation': 'Recover exact UTF-8 and resolve the fixed instant without '
                                        'guest default/clock changes. Do not present a handover '
                                        'sentence or keyword as automated reasoning assessment.',
                         'expected': 'Independent recovered bytes and actual summer offset.'},
                        {'command': 'here && fresh "$w/job.sh" && cat > job.sh <<\'LL_JOB\'\n'
                                    '#!/bin/sh\n'
                                    'umask 077 || exit 90\n'
                                    'ulimit -f 8 || exit 91\n'
                                    'test ! -e result && test ! -L result || exit 89\n'
                                    'set -C || exit 92\n'
                                    '{\n'
                                    ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 '
                                    '" hard=" $5}\' /proc/self/limits\n'
                                    " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
                                    '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" '
                                    '"$(id -u)" "$(pwd -P)" "$(umask)"; printf '
                                    '"LANG=%s\\nLC_ALL=%s\\n" "$LANG" "$LC_ALL"; test "$LANG" = C '
                                    '&& test "$LC_ALL" = C && printf "bounded-job-complete\\n"\'\n'
                                    ' rc=$?\n'
                                    ' printf \'exit=%s\\n\' "$rc"\n'
                                    '} > result 2>&1\n'
                                    'exit "$rc"\n'
                                    'LL_JOB',
                         'explanation': 'Prepare the same bounded result contract, then choose '
                                        'explicit scheduling context for the independent handover.',
                         'expected': 'Finite /bin/sh job; no reliance on interactive shell '
                                     'functions.'},
                        {'command': 'here && fresh "$w/result" && regular "$w/job.sh" && fresh '
                                    '"$w/queued.log" && env LANG=C LC_ALL=C /usr/bin/at -M -f '
                                    '"$w/job.sh" now + 1 minute > queued.log 2>&1 && jobid '
                                    '"$w/queued.log" && printf "Recorded job=%s workspace=%s\\n" '
                                    '"$job" "$w"',
                         'explanation': 'Queue only this owned job; retain its ID/body/context.',
                         'expected': 'Distinct recorded run.'},
                        {'command': 'foundation_step() { here && jobid "$w/queued.log" || return '
                                    '19; deadline=$(( $(date +%s)+150 )); while ! grep -Fxq exit=0 '
                                    '"$w/result" 2>/dev/null; do test "$(date +%s)" -lt '
                                    '"$deadline" || return 19; sleep 1; done; regular "$w/result" '
                                    '&& test "$(wc -c < result)" -le 4096 && grep -Fx '
                                    'identity=learner result && grep -Fx "uid=$(id -u)" result && '
                                    'grep -Fx "cwd=$w" result && grep -Fx umask=0077 result && '
                                    'grep -Fx LANG=C result && grep -Fx LC_ALL=C result && grep '
                                    '-Fx "file_limit_soft=4096 hard=4096" result && grep -Fx '
                                    'bounded-job-complete result || return 19; while :; do fresh '
                                    '"$w/queue-current.txt" || regular "$w/queue-current.txt" || '
                                    'return 19; atq > queue-current.txt || return 19; if awk -v '
                                    'id="$job" \'$1==id {f=1} END {exit !f}\' queue-current.txt; '
                                    'then test "$(date +%s)" -lt "$deadline" || return 19; sleep '
                                    '1; else break; fi; done; cat result; }; foundation_step',
                         'explanation': 'Verify actual execution evidence before writing the '
                                        'handover: encoding/zone facts and successful job are '
                                        'separate claims.',
                         'expected': 'Known output, real identity/cwd/locale/status and no pending '
                                     'owned job.'}],
              'hints': ['No causal or language-quality score from keywords; correct-looking '
                        'display alone does not prove correct encoded bytes or execution.',
                        'Use the actual dynamically captured job ID and successful owner-matched '
                        'queue queries; a command failure is not an empty queue.',
                        'Inspect actual result ownership, bytes and exit status; cancel only '
                        'positively matched pending work before exact rollback.'],
              'review': ['I demonstrated the selected mode’s facts, actual identities/results and '
                         'an incorrect interpretation or attempt.',
                         'I can separate queueing, execution, access policy and self-reviewed '
                         'reasoning. Completion is unscored and not automatic verification.',
                         'I removed only positively matched owned jobs, restored any exact policy '
                         'fixture and retained evidence; no authentication or host changes.'],
              'coverage': 'LPIC-1 active v5.0 partial 107.3 and108.2 independent transfer; no new '
                          'objective credit. No full objective, automatic assessment or '
                          'endorsement. The plan’s 107.2 at tags were corrected to '
                          'active108.2;107.2 concerns display/X11.'},
  'entry': {'id': 'real-linux-foundation-localization-handover',
            'resource': 'real-linux-foundation-localization-handover.json',
            'description': 'Transfer locale, encoding, time and one-off execution decisions '
                           'without repeating a guided repair.',
            'objectives': ['107.3 and108.2 independent transfer; no new objective credit'],
            'troubleshooting': ['No causal or language-quality score from keywords; '
                                'correct-looking display alone does not prove correct encoded '
                                'bytes or execution.',
                                'Direct sudo -u practice-user is not authorized by the root-only '
                                'guest sudo rule. Use the displayed root-authorized runuser; never '
                                'change sudo/PAM or enter/create passwords.'],
            'cleanup': ['Before leaving, inspect only each recorded job ID using its successful '
                        'owner query plus saved body/path/owner evidence. If still queued, cancel '
                        'that exact owned ID; if a job may be running, wait up to150s for its '
                        'bounded result/exit. Do not remove its workspace while it can write. '
                        'Unknown ownership requires refusal, not broad cleanup.',
                        'For at-access perform only the displayed SHA/type/mode guarded removal of '
                        'the known allow fixture and byte-check original deny/auth/sudo '
                        'fingerprints. Preserve pre-created practice users and root snapshots; no '
                        'account deletion or PAM editing.',
                        'Keep the exact private workspace as evidence; no recursive deletion, '
                        'spool edits or helper-state pruning. Repeated setup refuses existing '
                        'originals; interruption does not permit replacing a fixture. Reset '
                        'retains the previous disk; Resume restores disk, not RAM or jobs.'],
            'materials': ['Fresh Learn or Challenge setup: w=$(mktemp -d '
                          '"$HOME/foundation-localization-handover.XXXXXX") && cd "$w" && umask '
                          '077; here() { case "$w" in '
                          '"$HOME"/foundation-localization-handover.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" '
                          '|| return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' '
                          '"$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; '
                          'esac; }; here && test "$(df -B1 --output=avail / | tail -1)" -ge '
                          '1073741824 && systemctl is-active atd && pwd',
                          'For Resume set w to its recorded path and restore these definitions, '
                          'not mktemp or a new incident: here() { case "$w" in '
                          '"$HOME"/foundation-localization-handover.??????) ;; *) return 19;; '
                          'esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && '
                          'test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                          '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test '
                          '"${1%/*}" = "$w" && test ! -e "$1" && test ! -L "$1"; }; regular() { '
                          'here && test "${1%/*}" = "$w" && test -f "$1" && test ! -L "$1" && test '
                          '"$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular "$1" '
                          '|| return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' '
                          '"$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; '
                          'esac; }',
                          'Challenge starting fixture: here && fresh "$w/incident.txt" && printf '
                          '"Source bytes: ISO-8859-1 cafe-with-e-acute plus newline.\\nInstant: '
                          '2026-07-01 12:00:00 UTC.\\nRequired report: UTF-8, UTC instant and '
                          'Berlin offset; capture C-locale job.\\nWrong handover calls the source '
                          'UTF-8 and assumes Berlin is always +0100.\\n" > incident.txt && fresh '
                          '"$w/source-latin1.txt" && printf "caf\\351\\n" > source-latin1.txt && '
                          'fresh "$w/source.sha" && sha256sum source-latin1.txt > source.sha && '
                          'cat incident.txt',
                          'Independent target: Independently deliver exact factual results from a '
                          'different dataset, a successful bounded job and a readable handover. '
                          'Retain actual IDs, owners, statuses, contents and failed evidence. '
                          'Never fixed job numbers or broad cancellation; completion remains '
                          'self-reviewed. Fixed handover source Latin1 octets63 61 66 e9 0a; '
                          'recovered UTF8 63 61 66 c3 a9 0a. July Berlin +0200; queueing alone '
                          'does not prove completion.'],
            'observations': ['Facts, units/zone/encoding, job identity/status, original '
                             'preservation, rejected hypothesis and self-review answers.',
                             'Successful owner query, actual result/footer/UID/bytes where '
                             'executed; reasoning self-reviewed.'],
            'questions': ['What proves this specific action and what remains uncertain?',
                          'No causal or language-quality score from keywords; correct-looking '
                          'display alone does not prove correct encoded bytes or execution.'],
            'limitations': ['No runtime network/mail or credentials. at -M prevents mail delivery. '
                            '/bin/sh is not an interactive Bash session; queueing does not prove '
                            'PAM/account execution. Locked passwords and nologin do not prohibit '
                            'authorized root runuser.',
                            'One finite job at a time; child6s plus2s grace, output4KiB, '
                            'observation150s. Cancellation-only lesson waits130s after submission; '
                            'every utility query10s where bounded. At most64KiB input/256KiB '
                            'practice output, observed1GiB guest free admission; not a quota. Root '
                            'can override guest limits.',
                            'No automatically scored reasoning, preserved RAM/jobs on Resume, '
                            'physical-keyboard or accessibility certification.']},
  'resource_sha256': '70f3fbf22202a7993cf2d311e27b3a3a8b1850bca8f0bfb507343c58ffb4d3d6',
  'entry_sha256': '6045a52edf1d83c0d3985fc603e5e60b1a209a4a500922220009639022fc57c3',
  'learn': ['w=$(mktemp -d "$HOME/foundation-localization-handover.XXXXXX") && cd "$w" && umask '
            '077; here() { case "$w" in "$HOME"/foundation-localization-handover.??????) ;; *) '
            'return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L "$w" && test '
            '"$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test "$(stat -c %U:%a '
            '"$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" && test ! -e "$1" && '
            'test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" && test -f "$1" && test '
            '! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = learner:600:1; }; jobid() { regular '
            '"$1" || return 19; job=$(awk \'$1=="job" && $2 ~ /^[0-9]+$/ {print $2}\' "$1"); case '
            '"$job" in \'\'|*[!0-9]*) return 19;; *) test "$job" -gt 0;; esac; }; here && test '
            '"$(df -B1 --output=avail / | tail -1)" -ge 1073741824 && systemctl is-active atd && '
            'pwd',
            'here && fresh "$w/incident.txt" && printf "Source bytes: ISO-8859-1 cafe-with-e-acute '
            'plus newline.\\nInstant: 2026-07-01 12:00:00 UTC.\\nRequired report: UTF-8, UTC '
            'instant and Berlin offset; capture C-locale job.\\nWrong handover calls the source '
            'UTF-8 and assumes Berlin is always +0100.\\n" > incident.txt && fresh '
            '"$w/source-latin1.txt" && printf "caf\\351\\n" > source-latin1.txt && fresh '
            '"$w/source.sha" && sha256sum source-latin1.txt > source.sha && cat incident.txt',
            'foundation_step() { here && fresh "$w/wrong-partial.txt" && fresh '
            '"$w/wrong-error.txt" || return 19; if timeout -k 1s 10s iconv -f UTF-8 -t UTF-8 '
            'source-latin1.txt > wrong-partial.txt 2> wrong-error.txt; then return 1; else test $? '
            '= 1 && test -s wrong-error.txt && sha256sum -c source.sha; fi; }; foundation_step',
            'here && fresh "$w/recovered-utf8.txt" && fresh "$w/expected-utf8.txt" && timeout -k '
            '1s 10s iconv -f ISO-8859-1 -t UTF-8 source-latin1.txt > recovered-utf8.txt && printf '
            '"caf\\303\\251\\n" > expected-utf8.txt && cmp recovered-utf8.txt expected-utf8.txt && '
            'fresh "$w/zone.txt" && env TZ=Europe/Berlin LC_ALL=C date -d "2026-07-01 12:00:00 '
            'UTC" "+%F %T %z" > zone.txt && grep -Fx "2026-07-01 14:00:00 +0200" zone.txt && '
            'sha256sum -c source.sha',
            'here && fresh "$w/job.sh" && cat > job.sh <<\'LL_JOB\'\n'
            '#!/bin/sh\n'
            'umask 077 || exit 90\n'
            'ulimit -f 8 || exit 91\n'
            'test ! -e result && test ! -L result || exit 89\n'
            'set -C || exit 92\n'
            '{\n'
            ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 " hard=" $5}\' '
            '/proc/self/limits\n'
            " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
            '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" "$(pwd -P)" '
            '"$(umask)"; printf "LANG=%s\\nLC_ALL=%s\\n" "$LANG" "$LC_ALL"; test "$LANG" = C && '
            'test "$LC_ALL" = C && printf "bounded-job-complete\\n"\'\n'
            ' rc=$?\n'
            ' printf \'exit=%s\\n\' "$rc"\n'
            '} > result 2>&1\n'
            'exit "$rc"\n'
            'LL_JOB',
            'here && fresh "$w/result" && regular "$w/job.sh" && fresh "$w/queued.log" && env '
            'LANG=C LC_ALL=C /usr/bin/at -M -f "$w/job.sh" now + 1 minute > queued.log 2>&1 && '
            'jobid "$w/queued.log" && printf "Recorded job=%s workspace=%s\\n" "$job" "$w"',
            'foundation_step() { here && jobid "$w/queued.log" || return 19; deadline=$(( $(date '
            '+%s)+150 )); while ! grep -Fxq exit=0 "$w/result" 2>/dev/null; do test "$(date +%s)" '
            '-lt "$deadline" || return 19; sleep 1; done; regular "$w/result" && test "$(wc -c < '
            'result)" -le 4096 && grep -Fx identity=learner result && grep -Fx "uid=$(id -u)" '
            'result && grep -Fx "cwd=$w" result && grep -Fx umask=0077 result && grep -Fx LANG=C '
            'result && grep -Fx LC_ALL=C result && grep -Fx "file_limit_soft=4096 hard=4096" '
            'result && grep -Fx bounded-job-complete result || return 19; while :; do fresh '
            '"$w/queue-current.txt" || regular "$w/queue-current.txt" || return 19; atq > '
            'queue-current.txt || return 19; if awk -v id="$job" \'$1==id {f=1} END {exit !f}\' '
            'queue-current.txt; then test "$(date +%s)" -lt "$deadline" || return 19; sleep 1; '
            'else break; fi; done; cat result; }; foundation_step'],
  'challenge': ['w=$(mktemp -d "$HOME/foundation-localization-handover.XXXXXX") && cd "$w" && '
                'umask 077; here() { case "$w" in "$HOME"/foundation-localization-handover.??????) '
                ';; *) return 19;; esac; test "${w%/*}" = "$HOME" && test -d "$w" && test ! -L '
                '"$w" && test "$(realpath -e "$w")" = "$w" && test "$(pwd -P)" = "$w" && test '
                '"$(stat -c %U:%a "$w")" = learner:700; }; fresh() { here && test "${1%/*}" = "$w" '
                '&& test ! -e "$1" && test ! -L "$1"; }; regular() { here && test "${1%/*}" = "$w" '
                '&& test -f "$1" && test ! -L "$1" && test "$(stat -c %U:%a:%h "$1")" = '
                'learner:600:1; }; jobid() { regular "$1" || return 19; job=$(awk \'$1=="job" && '
                '$2 ~ /^[0-9]+$/ {print $2}\' "$1"); case "$job" in \'\'|*[!0-9]*) return 19;; *) '
                'test "$job" -gt 0;; esac; }; here && test "$(df -B1 --output=avail / | tail -1)" '
                '-ge 1073741824 && systemctl is-active atd && pwd',
                'here && fresh "$w/incident.txt" && printf "Source bytes: ISO-8859-1 '
                'cafe-with-e-acute plus newline.\\nInstant: 2026-07-01 12:00:00 UTC.\\nRequired '
                'report: UTF-8, UTC instant and Berlin offset; capture C-locale job.\\nWrong '
                'handover calls the source UTF-8 and assumes Berlin is always +0100.\\n" > '
                'incident.txt && fresh "$w/source-latin1.txt" && printf "caf\\351\\n" > '
                'source-latin1.txt && fresh "$w/source.sha" && sha256sum source-latin1.txt > '
                'source.sha && cat incident.txt',
                'foundation_step() { here && fresh "$w/wrong-partial.txt" && fresh '
                '"$w/wrong-error.txt" || return 19; if timeout -k 1s 10s iconv -f UTF-8 -t UTF-8 '
                'source-latin1.txt > wrong-partial.txt 2> wrong-error.txt; then return 1; else '
                'test $? = 1 && test -s wrong-error.txt && sha256sum -c source.sha; fi; }; '
                'foundation_step',
                'here && fresh "$w/recovered-utf8.txt" && fresh "$w/expected-utf8.txt" && timeout '
                '-k 1s 10s iconv -f ISO-8859-1 -t UTF-8 source-latin1.txt > recovered-utf8.txt && '
                'printf "caf\\303\\251\\n" > expected-utf8.txt && cmp recovered-utf8.txt '
                'expected-utf8.txt && fresh "$w/zone.txt" && env TZ=Europe/Berlin LC_ALL=C date -d '
                '"2026-07-01 12:00:00 UTC" "+%F %T %z" > zone.txt && grep -Fx "2026-07-01 14:00:00 '
                '+0200" zone.txt && sha256sum -c source.sha',
                'here && fresh "$w/job.sh" && cat > job.sh <<\'LL_JOB\'\n'
                '#!/bin/sh\n'
                'umask 077 || exit 90\n'
                'ulimit -f 8 || exit 91\n'
                'test ! -e result && test ! -L result || exit 89\n'
                'set -C || exit 92\n'
                '{\n'
                ' /usr/bin/awk \'/^Max file size/ {print "file_limit_soft=" $4 " hard=" $5}\' '
                '/proc/self/limits\n'
                " /usr/bin/timeout --kill-after=2s 6s /bin/sh -c 'printf "
                '"identity=%s\\nuid=%s\\ncwd=%s\\numask=%s\\n" "$(id -un)" "$(id -u)" "$(pwd -P)" '
                '"$(umask)"; printf "LANG=%s\\nLC_ALL=%s\\n" "$LANG" "$LC_ALL"; test "$LANG" = C '
                '&& test "$LC_ALL" = C && printf "bounded-job-complete\\n"\'\n'
                ' rc=$?\n'
                ' printf \'exit=%s\\n\' "$rc"\n'
                '} > result 2>&1\n'
                'exit "$rc"\n'
                'LL_JOB',
                'here && fresh "$w/result" && regular "$w/job.sh" && fresh "$w/queued.log" && env '
                'LANG=C LC_ALL=C /usr/bin/at -M -f "$w/job.sh" now + 1 minute > queued.log 2>&1 && '
                'jobid "$w/queued.log" && printf "Recorded job=%s workspace=%s\\n" "$job" "$w"',
                'foundation_step() { here && jobid "$w/queued.log" || return 19; deadline=$(( '
                '$(date +%s)+150 )); while ! grep -Fxq exit=0 "$w/result" 2>/dev/null; do test '
                '"$(date +%s)" -lt "$deadline" || return 19; sleep 1; done; regular "$w/result" && '
                'test "$(wc -c < result)" -le 4096 && grep -Fx identity=learner result && grep -Fx '
                '"uid=$(id -u)" result && grep -Fx "cwd=$w" result && grep -Fx umask=0077 result '
                '&& grep -Fx LANG=C result && grep -Fx LC_ALL=C result && grep -Fx '
                '"file_limit_soft=4096 hard=4096" result && grep -Fx bounded-job-complete result '
                '|| return 19; while :; do fresh "$w/queue-current.txt" || regular '
                '"$w/queue-current.txt" || return 19; atq > queue-current.txt || return 19; if awk '
                '-v id="$job" \'$1==id {f=1} END {exit !f}\' queue-current.txt; then test "$(date '
                '+%s)" -lt "$deadline" || return 19; sleep 1; else break; fi; done; cat result; }; '
                'foundation_step'],
  'cleanup': [],
  'assertions': ['here && test "$(du --apparent-size -sb "$w" | cut -f1)" -le 262144 && fresh '
                 '"$w/isolation-collision" && printf "%s\\n" preserved > isolation-collision && ! '
                 'fresh "$w/isolation-collision" && grep -Fx preserved isolation-collision'],
  'negative_after_setup': [],
  'negative_after_job': []}]
