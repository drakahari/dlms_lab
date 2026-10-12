#!/bin/sh
# Trusted build-only guest step. Original project sources; never lesson execution.
set -eu
export LC_ALL=C LANG=C SOURCE_DATE_EPOCH=1767225600
umask 022
src=/opt/learning-lab-rpm-source
test -d "$src" && test ! -L "$src"
for round in a b; do
 # Separate wall-clock rounds so equality cannot be a same-second coincidence.
 if test "$round" = b; then sleep 2; fi
 printf "LL_FIXTURE_BUILD_ROUND %s %s\n" "$round" "$(date +%s)"
 w=/home/learner/ll-rpm-build-$round
 test ! -e "$w" && test ! -L "$w"
 install -d -m 0700 -o learner -g learner "$w"
 for version in 1.0 2.0; do
  top=$w/data-$version
  install -d -m 0700 -o learner -g learner "$top" "$top/SOURCES" "$top/SPECS" "$top/BUILD" "$top/BUILDROOT" "$top/RPMS" "$top/SRPMS"
  install -m 0644 -o learner -g learner "$src/data-$version/data.txt" "$src/data-$version/report.conf" "$src/LICENSE" "$top/SOURCES/"
  install -m 0644 -o learner -g learner "$src/data-$version/ll-rpm-data.spec" "$top/SPECS/"
  find "$top" -type f -exec touch -d @1767225600 '{}' ';'
  timeout --signal=TERM --kill-after=5s 60s runuser -u learner -- rpmbuild -bb --define "_topdir $top" --define '_buildhost learning-lab.invalid' --define 'use_source_date_epoch_as_buildtime 1' --define 'clamp_mtime_to_source_date_epoch 1' --define 'source_date_epoch_from_changelog 1' --define '_binary_payload w9.gzdio' "$top/SPECS/ll-rpm-data.spec"
 done
 top=$w/report
 install -d -m 0700 -o learner -g learner "$top" "$top/SOURCES" "$top/SPECS" "$top/BUILD" "$top/BUILDROOT" "$top/RPMS" "$top/SRPMS"
 install -m 0644 -o learner -g learner "$src/report-1.0/ll-rpm-report" "$src/LICENSE" "$top/SOURCES/"
 install -m 0644 -o learner -g learner "$src/report-1.0/ll-rpm-report.spec" "$top/SPECS/"
 find "$top" -type f -exec touch -d @1767225600 '{}' ';'
 timeout --signal=TERM --kill-after=5s 60s runuser -u learner -- rpmbuild -bb --define "_topdir $top" --define '_buildhost learning-lab.invalid' --define 'use_source_date_epoch_as_buildtime 1' --define 'clamp_mtime_to_source_date_epoch 1' --define 'source_date_epoch_from_changelog 1' --define '_binary_payload w9.gzdio' "$top/SPECS/ll-rpm-report.spec"
done
for pair in data-1.0/ll-rpm-data-1.0-1.noarch.rpm data-2.0/ll-rpm-data-2.0-1.noarch.rpm report/ll-rpm-report-1.0-1.noarch.rpm; do
 dir=${pair%/*}; name=${pair##*/}
 a=/home/learner/ll-rpm-build-a/$dir/RPMS/noarch/$name
 b=/home/learner/ll-rpm-build-b/$dir/RPMS/noarch/$name
 test -f "$a" && test ! -L "$a" && test -f "$b" && test ! -L "$b"
 test "$(stat -c %s "$a")" -le 131072
 cmp "$a" "$b"
 test "$(rpm -qp --qf '%{BUILDTIME}' "$a")" = 1767225600
 rpm -qp --qf '[%{FILEMTIMES}\n]' "$a" | awk '$0 != "1767225600" { bad=1 } END { exit bad }'
 printf 'LL_FIXTURE_BEGIN %s %s\n' "$name" "$(sha256sum "$a" | cut -d ' ' -f1)"
 base64 "$a"
 printf 'LL_FIXTURE_END %s\n' "$name"
done
printf 'LL_FIXTURE_REPRODUCIBLE_PASS\n'
