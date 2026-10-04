#!/bin/sh
# Runs ONLY inside the newly installed guest via Debian Installer in-target.
set -eux
exec 2>/dev/ttyS0
passwd -l root
passwd -l learner
usermod -G users learner
if dpkg-query -W -f='${Status}' sudo 2>/dev/null | grep -q 'install ok installed'; then
    dpkg --purge sudo
fi
if dpkg-query -W -f='${Status}' openssh-server 2>/dev/null | grep -q 'install ok installed'; then
    dpkg --purge openssh-server
fi
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/override.conf <<'UNIT'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin learner --noclear %I $TERM
UNIT
cat > /etc/motd <<'MOTD'
Learning Lab — Real Linux offline preview
This guest is disposable. Resume keeps disk files, not RAM or shell jobs.
Use Learning Lab's Stop control for clean shutdown. Reset retains the prior disk.
No networking, shared host folders, clipboard or remote login is configured.
MOTD
mkdir -p /usr/local/share/learning-lab
printf '%s\n' 'debian13-jobs-local-v1' > /usr/local/share/learning-lab/image-id
dpkg-query -W -f='${binary:Package}\t${Version}\n' > /usr/local/share/learning-lab/packages.tsv
# Emit inventory and non-secret assertions to the isolated build console.
printf '\nLEARNING_LAB_INVENTORY_BEGIN\n' > /dev/ttyS0
cat /usr/local/share/learning-lab/packages.tsv > /dev/ttyS0
printf 'LEARNING_LAB_INVENTORY_END\n' > /dev/ttyS0
id learner > /dev/ttyS0
passwd -S root > /dev/ttyS0
passwd -S learner > /dev/ttyS0
# No owner credentials/history are ever inputs. Remove installer/build artifacts.
rm -f /root/.bash_history /home/learner/.bash_history /var/lib/systemd/random-seed
rm -f /etc/machine-id
: > /etc/machine-id
mkdir -p /var/lib/dbus
rm -f /var/lib/dbus/machine-id
ln -s /etc/machine-id /var/lib/dbus/machine-id
rm -rf /var/log/installer
find /var/log -type f -exec truncate -s 0 '{}' ';'
sync
printf 'LEARNING_LAB_IMAGE_PREPARED\n' > /dev/ttyS0
