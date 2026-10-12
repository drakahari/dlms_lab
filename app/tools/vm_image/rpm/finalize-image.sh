#!/bin/sh
# Trusted one-time guest finalization after the installer completely powered off.
set -eu
export LC_ALL=C LANG=C
exec >/dev/ttyS0 2>&1
test "$(getenforce)" = Enforcing
test "$(passwd -S root | cut -d ' ' -f2)" = LK
test "$(passwd -S learner | cut -d ' ' -f2)" = LK
visudo -cf /etc/sudoers
grep -Fx 'learner ALL=(root) NOPASSWD: ALL' /etc/sudoers.d/learning-lab
test "$(stat -c '%U:%G:%a' /etc/sudoers.d/learning-lab)" = root:root:440
rpm -qa --qf '%{NAME}\t%{EPOCHNUM}\t%{VERSION}\t%{RELEASE}\t%{ARCH}\t%{SOURCERPM}\n' > /tmp/ll-inventory-raw
awk -F '\t' '$1 != "gpg-pubkey"' /tmp/ll-inventory-raw | LC_ALL=C sort > /usr/local/share/learning-lab/packages.tsv
awk -F '\t' '$1 == "gpg-pubkey"' /tmp/ll-inventory-raw > /usr/local/share/learning-lab/rpm-trust.tsv
# RPM public-key pseudo-records are trust metadata, not source/binary packages.
printf 'gpg-pubkey\t0\tb86b3716\t61e69f29\t(none)\t(none)\n' > /tmp/ll-expected-trust
cmp /tmp/ll-expected-trust /usr/local/share/learning-lab/rpm-trust.tsv
rm -- /tmp/ll-expected-trust
if ! cmp /usr/local/sbin/ll-expected.tsv /usr/local/share/learning-lab/packages.tsv; then
 printf 'LL_REJECTED_INVENTORY_BEGIN\n';cat /usr/local/share/learning-lab/packages.tsv;printf 'LL_REJECTED_INVENTORY_END\n';exit 1
fi
for name in ll-rpm-data ll-rpm-report openssh-server openssh-clients cloud-init qemu-guest-agent kexec-tools NetworkManager firewalld chrony; do
 ! rpm -q "$name"
done
test "$(systemctl is-enabled dnf-makecache.timer || :)" = disabled
if test -f /usr/local/sbin/ll-build-fixtures; then
 timeout --signal=TERM --kill-after=5s 420s /bin/sh /usr/local/sbin/ll-build-fixtures
fi
# The finalizer is the only default-target build unit. Normal boot starts no
# installer or package automation, and no package step follows this inventory.
rm -- /etc/systemd/system/default.target /etc/systemd/system/ll-image-finalize.service /etc/systemd/system/ll-image-finalize.target /usr/local/sbin/ll-finalize /usr/local/sbin/ll-expected.tsv /tmp/ll-inventory-raw
ln -s /usr/lib/systemd/system/multi-user.target /etc/systemd/system/default.target
printf 'LL_FINAL_POLICY_BEGIN\n'
id learner;passwd -S learner;passwd -S root;getenforce
systemctl list-unit-files --state=enabled --no-pager
sha256sum /etc/sudoers.d/learning-lab
printf 'LL_FINAL_POLICY_END\nLL_FINAL_INVENTORY_BEGIN\n'
cat /usr/local/share/learning-lab/packages.tsv
printf 'LL_FINAL_INVENTORY_END\n'
# Known fresh-build state only, never an owner's image or used overlay.
rm -f /root/.bash_history /home/learner/.bash_history /var/lib/systemd/random-seed /etc/machine-id
: > /etc/machine-id
find /var/log -type f -exec truncate -s 0 '{}' ';'
sync
printf 'LL_ALMA_IMAGE_FINALIZED\n'
