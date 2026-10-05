"""Static developer guest-console fixtures; never imported by application code.
Lesson JSON is display-only. These literals are parity-checked, never loaded from packs.
"""
COMMANDS = {'real-linux-admin-change': ['id; sudo -n -l; pwd',
                             'work=$(mktemp -d "$HOME/admin-change.XXXXXX") && cd "$work" && pwd',
                             'printf "message=trial\\n" > /etc/learning-lab/change.conf; printf '
                             '"previous status=%s\\n" "$?"',
                             'sudo cp -p /etc/learning-lab/change.conf "$work/original.conf"; sudo '
                             'cp -p /etc/learning-lab/change.conf '
                             '/etc/learning-lab/change.conf.before',
                             'printf "message=reviewed\\n" | sudo tee '
                             '/etc/learning-lab/change.conf; diff -u "$work/original.conf" '
                             '/etc/learning-lab/change.conf',
                             'grep -Fx "message=reviewed" /etc/learning-lab/change.conf && printf '
                             '"validated\\n"',
                             'sudo cp -p /etc/learning-lab/change.conf.before '
                             '/etc/learning-lab/change.conf; cmp "$work/original.conf" '
                             '/etc/learning-lab/change.conf; printf "compare status=%s\\n" "$?"'],
 'real-linux-admin-lifecycle': ['systemctl status ll-lifecycle.service --no-pager; systemctl '
                                'is-enabled ll-lifecycle.service',
                                'sudo systemctl start ll-lifecycle.service; systemctl show '
                                'll-lifecycle.service -p ActiveState -p MainPID -p User -p '
                                'MemoryMax -p TasksMax',
                                'pid=$(systemctl show ll-lifecycle.service -p MainPID --value); ps '
                                '-o pid,user,stat,args -p "$pid"',
                                'sudo systemctl restart ll-lifecycle.service; sudo journalctl -u '
                                'll-lifecycle.service -n 12 --no-pager',
                                'sudo systemctl stop ll-lifecycle.service; systemctl is-active '
                                'll-lifecycle.service'],
 'real-linux-admin-boot': ['systemctl get-default; systemctl is-enabled ll-boot.service; sudo '
                           'systemctl start ll-boot.service',
                           'sudo systemctl enable ll-boot.service; systemctl is-enabled '
                           'll-boot.service; cat /proc/sys/kernel/random/boot_id',
                           'sudo systemctl reboot',
                           'cat /proc/sys/kernel/random/boot_id; sudo cat '
                           '/var/lib/ll-boot/last-start; sudo journalctl -b -u ll-boot.service -n '
                           '12 --no-pager',
                           'sudo systemctl disable --now ll-boot.service; systemctl is-enabled '
                           'll-boot.service; systemctl is-active ll-boot.service'],
 'real-linux-admin-override': ['sudo systemctl start ll-override.service; systemctl status '
                               'll-override.service --no-pager; sudo journalctl -u '
                               'll-override.service -n 10 --no-pager',
                               'systemctl cat ll-override.service; sudo systemd-analyze verify '
                               'll-override.service',
                               'sudo cp -p /etc/systemd/system/ll-override.service.d/broken.conf '
                               '/etc/learning-lab/override-dropin.before; sudo nano '
                               '/etc/systemd/system/ll-override.service.d/broken.conf',
                               'sudo systemd-analyze verify ll-override.service && sudo systemctl '
                               'daemon-reload && sudo systemctl restart ll-override.service',
                               'systemctl is-active ll-override.service; sudo journalctl -u '
                               'll-override.service -n 8 --no-pager; sudo systemctl stop '
                               'll-override.service'],
 'real-linux-admin-access': ['getent passwd ll-service; id ll-service; sudo passwd -S ll-service; '
                             'ls -ld /etc/learning-lab; ls -l /etc/learning-lab/access.conf',
                             'sudo runuser -u ll-service -- cat /etc/learning-lab/access.conf; '
                             'sudo systemctl start ll-access.service; sudo journalctl -u '
                             'll-access.service -n 8 --no-pager',
                             'sudo cp -p /etc/learning-lab/access.conf '
                             '/etc/learning-lab/access.conf.before; sudo chgrp ll-service '
                             '/etc/learning-lab/access.conf; sudo chmod 0640 '
                             '/etc/learning-lab/access.conf',
                             'sudo runuser -u ll-service -- cat /etc/learning-lab/access.conf; '
                             'sudo runuser -u nobody -- cat /etc/learning-lab/access.conf',
                             'sudo systemctl restart ll-access.service; sleep 1; sudo journalctl '
                             '-u ll-access.service -n 8 --no-pager',
                             'sudo systemctl stop ll-access.service; systemctl is-active '
                             'll-access.service'],
 'real-linux-admin-logs': ['logger -t ll-admin -p local5.notice "LAB_EVENT before"; sudo '
                           'journalctl -t ll-admin -n 5 --no-pager; sudo cat '
                           '/etc/rsyslog.d/40-learning-lab.conf',
                           'sudo cp -p /etc/rsyslog.d/40-learning-lab.conf '
                           '/etc/learning-lab/logging.before; sudo nano '
                           '/etc/rsyslog.d/40-learning-lab.conf',
                           'sudo rsyslogd -N1 && sudo systemctl restart rsyslog.service',
                           'logger -t ll-admin -p local5.notice "LAB_EVENT after"; sleep 1; sudo '
                           'journalctl -t ll-admin -p notice -n 5 --no-pager; sudo cat '
                           '/var/log/learning-lab/events.log',
                           'sudo ls -l /var/log/learning-lab/events.log; sudo wc -c '
                           '/var/log/learning-lab/events.log'],
 'real-linux-admin-rotation': ['printf "LAB_ROTATE retained record\\n" | sudo tee '
                               '/var/log/learning-lab/rotation.log; sudo chmod 0640 '
                               '/var/log/learning-lab/rotation.log; sudo chown root:adm '
                               '/var/log/learning-lab/rotation.log',
                               'sudo logrotate --debug --state '
                               '/var/lib/learning-lab/rotation.state '
                               '/etc/learning-lab/rotation.conf',
                               'sudo cp -p /etc/learning-lab/rotation.conf '
                               '/etc/learning-lab/rotation.before; sudo nano '
                               '/etc/learning-lab/rotation.conf',
                               'sudo logrotate --debug --state '
                               '/var/lib/learning-lab/rotation.state '
                               '/etc/learning-lab/rotation.conf && sudo logrotate --force --state '
                               '/var/lib/learning-lab/rotation.state '
                               '/etc/learning-lab/rotation.conf',
                               'sudo cat /var/log/learning-lab/rotation.log.1; sudo ls -l '
                               '/var/log/learning-lab/rotation.log*; sudo wc -c '
                               '/var/log/learning-lab/rotation.log'],
 'real-linux-admin-incident': ['work=$(mktemp -d "$HOME/admin-incident.XXXXXX") && cd "$work" && '
                               'pwd; systemctl status ll-incident.service --no-pager; systemctl '
                               'is-enabled ll-incident.service',
                               'sudo systemctl start ll-incident.service; sudo journalctl -u '
                               'll-incident.service -n 10 --no-pager; ls -l '
                               '/etc/learning-lab/incident.conf',
                               'sudo install -o root -g ll-service -m 0640 '
                               '/usr/local/share/learning-lab/admin-originals/incident.conf '
                               '/etc/learning-lab/incident.conf; sudo runuser -u ll-service -- cat '
                               '/etc/learning-lab/incident.conf',
                               'sudo systemctl enable --now ll-incident.service; sleep 1; '
                               'systemctl is-enabled ll-incident.service; sudo journalctl -u '
                               'll-incident.service -n 8 --no-pager',
                               'nano handover.txt',
                               'cat handover.txt; sudo systemctl disable --now '
                               'll-incident.service']}
