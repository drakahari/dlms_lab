#!/bin/sh
# Trusted one-time guest build step. Runs only AFTER Debian Installer powers off.
set -eu
export LC_ALL=C
exec >/dev/ttyS0 2>&1
# No network, login, package automation or unrelated system units are started by
# the dedicated finalization target. Abort before publishing on any difference.
dpkg --audit > /tmp/ll-dpkg-audit
test ! -s /tmp/ll-dpkg-audit
dpkg-query -W -f='${binary:Package}\t${Version}\t${source:Package}\t${source:Version}\n' > /usr/local/share/learning-lab/packages.tsv
cmp /usr/local/sbin/ll-build-expected-packages.tsv /usr/local/share/learning-lab/packages.tsv
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
(cd /opt/learning-lab/package-fixtures; sha256sum -c SHA256SUMS)
# Restore ordinary boot and remove only known build helpers before final evidence.
rm -- /etc/systemd/system/default.target /etc/systemd/system/ll-image-finalize.service /etc/systemd/system/ll-image-finalize.target /usr/local/sbin/ll-image-finalize /usr/local/sbin/ll-build-expected-packages.tsv /tmp/ll-dpkg-audit
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
