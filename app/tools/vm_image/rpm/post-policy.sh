#!/bin/sh
# Runs inside the fresh target guest only. No host/service/authentication changes.
set -eu
export LC_ALL=C
install -d -m 0755 /usr/local/share/learning-lab /etc/sudoers.d /etc/systemd/system/getty@tty1.service.d
printf '%s\n' 'learner ALL=(root) NOPASSWD: ALL' > /etc/sudoers.d/learning-lab
chmod 0440 /etc/sudoers.d/learning-lab
visudo -cf /etc/sudoers
passwd -l root
passwd -l learner
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin learner --noclear %I $TERM
EOF
systemctl disable dnf-makecache.timer
# No remote service or network manager is installed; do not add one for a build.
cat > /etc/systemd/system/ll-image-finalize.service <<'EOF'
[Unit]
Description=Learning Lab one-time fresh-image finalization
DefaultDependencies=no
After=local-fs.target sysinit.target
Requires=local-fs.target sysinit.target
JobTimeoutSec=780
JobTimeoutAction=poweroff
SuccessAction=poweroff
FailureAction=poweroff
[Service]
Type=oneshot
ExecStart=/bin/sh /usr/local/sbin/ll-finalize
StandardOutput=tty
StandardError=tty
TTYPath=/dev/ttyS0
TimeoutStartSec=600
EOF
cat > /etc/systemd/system/ll-image-finalize.target <<'EOF'
[Unit]
Description=Learning Lab isolated finalization target
DefaultDependencies=no
Requires=ll-image-finalize.service
After=ll-image-finalize.service
EOF
if test -e /etc/systemd/system/default.target || test -L /etc/systemd/system/default.target; then
 test -L /etc/systemd/system/default.target
 case "$(readlink /etc/systemd/system/default.target)" in
  multi-user.target|/usr/lib/systemd/system/multi-user.target|/lib/systemd/system/multi-user.target) ;;
  *) printf 'Unexpected fresh-install default target\n' >&2; exit 1;;
 esac
 rm -- /etc/systemd/system/default.target
fi
ln -s ll-image-finalize.target /etc/systemd/system/default.target
# Keep original vendor PAM and SELinux policy; label only new reviewed paths.
restorecon -RF /etc/sudoers.d /etc/systemd/system /usr/local/share/learning-lab /usr/local/sbin /opt
printf 'LL_ALMA_INSTALL_CONFIGURED\n'
