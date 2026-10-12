#!/bin/sh
# Trusted build recipe, executed ONLY inside a fresh Debian guest by its installer.
set -eu
exec 2>/dev/ttyS0
passwd -l root
passwd -l learner
usermod -G users learner
test ! -x /usr/sbin/sshd
test "$(dpkg-query -W -f='${Version}' sudo)" = '1.9.16p2-3+deb13u2'
test "$(dpkg-query -W -f='${Version}' rsyslog)" = '8.2504.0-1+deb13u2'
printf '%s\n' 'learner ALL=(root) NOPASSWD: ALL' > /etc/sudoers.d/learning-lab
chmod 0440 /etc/sudoers.d/learning-lab
visudo -cf /etc/sudoers
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/override.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin learner --noclear %I $TERM
EOF
useradd --system --no-create-home --shell /usr/sbin/nologin ll-service
passwd -l ll-service
mkdir -p /usr/local/lib/learning-lab /usr/local/share/learning-lab/admin-originals /etc/learning-lab /var/lib/learning-lab /var/log/learning-lab
chmod 0755 /etc/learning-lab /var/lib/learning-lab /var/log/learning-lab
cat > /usr/local/lib/learning-lab/admin-worker <<'EOF'
#!/bin/bash
# Fixed, bounded teaching service. Configuration is one data line, never sourced.
set -eu
case "${1-}" in lifecycle|boot|override|access|incident) name=$1;; *) exit 64;; esac
config=/etc/learning-lab/$name.conf
if ! IFS= read -r message < "$config"; then printf 'LAB_CONFIG_UNREADABLE %s\n' "$config" >&2; exit 2; fi
case "$message" in message=*) message=${message#message=};; *) echo LAB_CONFIG_INVALID >&2; exit 3;; esac
if [ "${#message}" -gt 120 ]; then echo LAB_CONFIG_TOO_LONG >&2; exit 3; fi
printf 'LAB_READY %s uid=%s message=%s\n' "$name" "$(id -u)" "$message"
# StateDirectory is created by systemd for this unprivileged service user.
printf '%s\n' "$(cat /proc/sys/kernel/random/boot_id) $name" > "/var/lib/ll-$name/last-start"
trap 'echo LAB_STOPPED; exit 0' TERM INT
sleep 120 & child=$!
wait "$child" || :
EOF
chmod 0755 /usr/local/lib/learning-lab/admin-worker
for name in lifecycle boot override access incident; do
 printf 'message=%s ready\n' "$name" > /etc/learning-lab/$name.conf
 chown root:ll-service /etc/learning-lab/$name.conf
 chmod 0640 /etc/learning-lab/$name.conf
 cat > /etc/systemd/system/ll-$name.service <<EOF
[Unit]
Description=Learning Lab $name (bounded offline fixture)
[Service]
Type=simple
User=ll-service
Group=ll-service
ExecStart=/usr/local/lib/learning-lab/admin-worker $name
StateDirectory=ll-$name
RuntimeMaxSec=120s
TimeoutStopSec=5s
MemoryMax=64M
TasksMax=8
CPUQuota=20%
LimitFSIZE=1M
Restart=no
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/ll-$name
StandardOutput=journal
StandardError=journal
[Install]
WantedBy=multi-user.target
EOF
 cp -p /etc/learning-lab/$name.conf /usr/local/share/learning-lab/admin-originals/$name.conf
done
printf 'message=original\n' > /etc/learning-lab/change.conf
chmod 0644 /etc/learning-lab/change.conf
mkdir -p /etc/systemd/system/ll-override.service.d
cat > /etc/systemd/system/ll-override.service.d/broken.conf <<'EOF'
[Service]
ExecStart=
ExecStart=/usr/local/lib/learning-lab/missing-worker override
EOF
# Independent dormant faults: no services enabled in the base.
chown root:root /etc/learning-lab/access.conf
mv /etc/learning-lab/incident.conf /usr/local/share/learning-lab/admin-originals/incident-disabled.conf
chmod 0000 /usr/local/share/learning-lab/admin-originals/incident-disabled.conf
cat > /etc/rsyslog.d/40-learning-lab.conf <<'EOF'
# Intentional selector fault: lesson 6 sends local5.notice.
local6.notice /var/log/learning-lab/events.log
EOF
# Local Unix input only. No TCP/UDP input or forwarding modules/actions.
cat > /etc/rsyslog.conf <<'EOF'
module(load="imuxsock")
$FileOwner root
$FileGroup adm
$FileCreateMode 0640
$DirCreateMode 0755
$WorkDirectory /var/spool/rsyslog
$IncludeConfig /etc/rsyslog.d/*.conf
EOF
mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/learning-lab.conf <<'EOF'
[Journal]
Storage=persistent
SystemMaxUse=32M
RuntimeMaxUse=16M
RateLimitIntervalSec=30s
RateLimitBurst=200
EOF
mkdir -p /var/log/journal
cat > /etc/learning-lab/rotation.conf <<'EOF'
/var/log/learning-lab/rotation.log {
    size 1k
    rotate 2
    missingok
    notifempty
    create 0999 root adm
}
EOF
printf '%s\n' 'Guest-only administration fixture: use sudo deliberately. Root can override all guest-side limits.' > /etc/motd
printf '%s\n' 'No NIC, host sharing, clipboard, remote login, or verified assessment. Reset retains old disks; profile backups exclude VM state.' >> /etc/motd
printf '%s\n' 'debian13-foundation-admin-local-v1' > /usr/local/share/learning-lab/image-id
# Only these three authenticated, approved archives are added/replaced.
# Dependencies are already in the frozen base; no resolver or network repair.
dpkg -i /tmp/ll-inputs/liblzma5.deb /tmp/ll-inputs/xz-utils.deb /tmp/ll-inputs/at.deb
for name in en_US.UTF-8 de_DE.UTF-8; do
 sed -i "s/^# $name UTF-8$/$name UTF-8/" /etc/locale.gen
done
locale-gen
systemctl enable atd.service
# Fixed offline image: no automatic package upgrade jobs. No old image changes.
printf '%s\n' 'APT::Periodic::Enable "0";' 'APT::Install-Recommends "false";' > /etc/apt/apt.conf.d/99learning-lab-offline
systemctl disable apt-daily.timer apt-daily-upgrade.timer
for name in ll-at-allow ll-at-deny; do
 useradd --system --create-home --shell /usr/sbin/nologin "$name"
 passwd -l "$name"
done
rm -- /tmp/ll-inputs/liblzma5.deb /tmp/ll-inputs/xz-utils.deb /tmp/ll-inputs/at.deb
rmdir /tmp/ll-inputs
install -m 0644 /tmp/learning-lab-LICENSE /usr/local/share/learning-lab/LICENSE
rm -- /tmp/learning-lab-LICENSE
# Do not capture inventory here: d-i has not finished its later hooks.
# A dedicated first boot has no interactive login, timers or package jobs.
test ! -e /etc/systemd/system/default.target
cat > /etc/systemd/system/ll-image-finalize.service <<'EOF'
[Unit]
Description=One-time offline Learning Lab image finalization
DefaultDependencies=no
Requires=local-fs.target
After=local-fs.target
Before=shutdown.target
Conflicts=shutdown.target
OnFailure=poweroff.target
SuccessAction=poweroff
[Service]
Type=oneshot
ExecStart=/bin/sh /usr/local/sbin/ll-image-finalize
TimeoutStartSec=120
StandardOutput=tty
StandardError=tty
TTYPath=/dev/ttyS0
EOF
cat > /etc/systemd/system/ll-image-finalize.target <<'EOF'
[Unit]
Description=One-time offline finalization boot
DefaultDependencies=no
Requires=ll-image-finalize.service
After=ll-image-finalize.service
AllowIsolate=yes
EOF
ln -s ll-image-finalize.target /etc/systemd/system/default.target
sync
printf 'LEARNING_LAB_INSTALL_CONFIGURED\n' > /dev/ttyS0
