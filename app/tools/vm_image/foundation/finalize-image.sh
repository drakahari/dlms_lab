#!/bin/sh
# Trusted one-time guest build step. Runs only AFTER Debian Installer powers off.
set -eu
export LC_ALL=C
exec >/dev/ttyS0 2>&1
# No network, login, package automation or unrelated system units are started by
# the dedicated finalization target. Abort before publishing on any difference.
dpkg --audit > /tmp/ll-dpkg-audit
test ! -s /tmp/ll-dpkg-audit
dpkg-query -W -f='${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\n' > /tmp/ll-inventory-raw
# dpkg's internal enumeration order can differ after explicit seed installation.
# Preserve every complete row and C-sort; exact frozen contents still gate admission.
LC_ALL=C sort /tmp/ll-inventory-raw > /usr/local/share/learning-lab/packages.tsv
if ! cmp /usr/local/sbin/ll-build-expected-packages.tsv /usr/local/share/learning-lab/packages.tsv; then
 printf 'LEARNING_LAB_REJECTED_INVENTORY_BEGIN\n'
 cat /usr/local/share/learning-lab/packages.tsv
 printf 'LEARNING_LAB_REJECTED_INVENTORY_END\n'
 diff -u /usr/local/sbin/ll-build-expected-packages.tsv /usr/local/share/learning-lab/packages.tsv || :
 exit 1
fi
for p in ll-discovery-data ll-discovery-report qemu-guest-agent intel-microcode iucode-tool; do
 test "$(dpkg-query -W -f='${db:Status-Status}' "$p" 2>/dev/null || :)" != installed
done
test "$(id -Gn learner)" = 'learner users'
test "$(passwd -S root | cut -d ' ' -f2)" = L
test "$(passwd -S learner | cut -d ' ' -f2)" = L
grep -Fx 'learner ALL=(root) NOPASSWD: ALL' /etc/sudoers.d/learning-lab
test "$(stat -c '%U:%G:%a' /etc/sudoers.d/learning-lab)" = root:root:440
visudo -cf /etc/sudoers
rsyslogd -N1
test "$(dpkg-query -W -f='${Version}' at)" = '3.2.5-2.2'
test "$(dpkg-query -W -f='${Version}' xz-utils)" = '5.8.1-1+deb13u2'
test "$(dpkg-query -W -f='${Version}' liblzma5:amd64)" = '5.8.1-1+deb13u2'
locale -a | grep -Fx en_US.utf8
locale -a | grep -Fx de_DE.utf8
test "$(systemctl is-enabled atd.service)" = enabled
for timer in apt-daily.timer apt-daily-upgrade.timer; do
 test "$(systemctl is-enabled "$timer" || :)" = disabled
done
grep -Fx 'APT::Periodic::Enable "0";' /etc/apt/apt.conf.d/99learning-lab-offline
test "$(stat -c '%U:%G:%a' /usr/bin/at)" = daemon:daemon:6755
for name in ll-at-allow ll-at-deny; do
 test "$(passwd -S "$name" | cut -d ' ' -f2)" = L
 test "$(getent passwd "$name" | cut -d: -f7)" = /usr/sbin/nologin
done
test ! -e /opt/learning-lab/package-fixtures
# Reject unexpected member types/names, not just queued regular files.
test "$(stat -c '%U:%G:%a' /var/spool/cron/atjobs)" = daemon:daemon:1770
test "$(stat -c '%U:%G:%a' /var/spool/cron/atspool)" = daemon:daemon:1770
test "$(stat -c '%U:%G:%a' /var/spool/cron/atjobs/.SEQ)" = daemon:daemon:600
test ! -L /var/spool/cron/atjobs/.SEQ
test "$(find /var/spool/cron/atjobs -mindepth 1 -maxdepth 1 -printf '%f\n')" = .SEQ
test -z "$(find /var/spool/cron/atspool -mindepth 1 -maxdepth 1 -printf '%f\n')"
echo 'c9edc682b985b87e20a83ade37677f0cb86acaf0cf8e40fa1779662678aa5cb2  /usr/local/share/learning-lab/LICENSE' | sha256sum -c -
# Restore ordinary boot and remove only known build helpers before final evidence.
rm -- /etc/systemd/system/default.target /etc/systemd/system/ll-image-finalize.service /etc/systemd/system/ll-image-finalize.target /usr/local/sbin/ll-image-finalize /usr/local/sbin/ll-build-expected-packages.tsv /tmp/ll-dpkg-audit /tmp/ll-inventory-raw
printf '\nLEARNING_LAB_FINAL_AUDIT_BEGIN\n'
id learner; id ll-service; passwd -S root; passwd -S learner; passwd -S ll-service
systemctl list-unit-files --state=enabled --no-pager
sha256sum /etc/sudoers.d/learning-lab
printf 'LEARNING_LAB_FINAL_AUDIT_END\n'
printf 'LEARNING_LAB_INVENTORY_BEGIN\n'
cat /usr/local/share/learning-lab/packages.tsv
printf 'LEARNING_LAB_INVENTORY_END\n'
# Preserve package notices, remove fresh build state, never personal data.
rm -f /root/.bash_history /home/learner/.bash_history /var/lib/systemd/random-seed /etc/machine-id /var/lib/dbus/machine-id
: > /etc/machine-id
ln -s /etc/machine-id /var/lib/dbus/machine-id
rm -rf /var/log/installer
find /var/log -type f -exec truncate -s 0 '{}' ';'
sync
printf 'LEARNING_LAB_IMAGE_FINALIZED\n'
# PID 1 performs clean poweroff through the unit SuccessAction after exit 0.
