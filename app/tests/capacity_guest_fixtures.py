"""Fixed developer console fixtures. Never imported by application/runtime.
No lesson or imported JSON is executed; tests check these reviewed literals against guidance.
"""
COMMANDS = {'real-linux-capacity-baseline': ['work=$(mktemp -d "$HOME/capacity-baseline.XXXXXX"); cd "$work" && pwd',
                                  'date -Is; nproc; uptime',
                                  'free -m; df -Pk .; df -Pi .',
                                  'timeout -k 2s 8s vmstat 1 3',
                                  '{ date -Is; nproc; uptime; free -m; df -Pk .; df -Pi .; } > baseline.txt; '
                                  'cat baseline.txt'],
 'real-linux-capacity-cpu': ['work=$(mktemp -d "$HOME/capacity-cpu.XXXXXX"); cd "$work" && pwd',
                             'timeout -k 2s 8s vmstat 1 3 > before.txt; cat before.txt',
                             'if [ -z "$(jobs -p)" ]; then timeout -k 2s 12s bash -c \'while :; do :; done\' '
                             '& worker=$!; sleep 1; birth=$(awk \'{print $22}\' "/proc/$worker/stat"); '
                             'cpu=$(ps -o pid= --ppid "$worker"); ps -o pid,ppid,pcpu,stat,args -p "$worker" '
                             '--ppid "$worker"; timeout -k 2s 8s vmstat 1 4 > during.txt; wait "$worker"; '
                             'result=$?; printf "supervisor=%s child=%s status=%s\\n" "$worker" "$cpu" '
                             '"$result" > worker.txt; cat during.txt worker.txt; else printf "Finish '
                             'existing shell jobs before another worker.\\n"; fi',
                             'timeout -k 2s 8s vmstat 1 3 > after.txt; cat after.txt',
                             'if [ -n "$worker" ] && jobs -p | grep -qx "$worker" && [ "$(awk \'{print '
                             '$22}\' "/proc/$worker/stat" 2>/dev/null)" = "$birth" ]; then kill -TERM '
                             '"$worker"; fi; if [ -n "$worker" ]; then wait "$worker" 2>/dev/null || :; fi',
                             'jobs -l; cat worker.txt'],
 'real-linux-capacity-memory': ['work=$(mktemp -d "$HOME/capacity-memory.XXXXXX"); cd "$work" && pwd',
                                'free -m; grep -E '
                                '"^(MemTotal|MemFree|MemAvailable|Cached|SwapTotal|SwapFree):" /proc/meminfo',
                                'timeout -k 2s 8s vmstat 1 3',
                                "printf '%s\\n' 'SYNTHETIC example; MiB, not this VM' 'total=2048 free=120 "
                                "available=1200 cached=900 swap_total=0' > memory-example.txt",
                                'cat memory-example.txt'],
 'real-linux-capacity-io': ['work=$(mktemp -d "$HOME/capacity-io.XXXXXX"); cd "$work" && pwd',
                            'df -Pk .; df -Pi .',
                            'test "$PWD" = "$work" && available=$(df -Pk . | awk \'NR==2 {print $4}\') && [ '
                            '"$available" -ge 540672 ] && TIMEFORMAT=\'%3R seconds\' && { time ( ulimit -f '
                            '16384; timeout -k 2s 15s dd if=/dev/zero of=io.bin bs=1M count=16 conv=fsync '
                            'status=none ); } 2> write-time.txt',
                            'test "$PWD" = "$work" && TIMEFORMAT=\'%3R seconds\' && { time timeout -k 2s 15s '
                            'dd if=io.bin of=/dev/null bs=1M count=16 status=none; } 2> read-time.txt',
                            'wc -c io.bin; cat write-time.txt read-time.txt',
                            'if [ "$PWD" = "$work" ]; then rm -f -- io.bin; fi; ls -l'],
 'real-linux-capacity-space-inodes': ['work=$(mktemp -d "$HOME/capacity-space.XXXXXX"); cd "$work" && pwd',
                                      'df -Pk .; df -Pi .; du -sk .',
                                      "printf '%s\\n' 'SYNTHETIC cases; not this VM' 'case available_KiB "
                                      "free_inodes' 'A 1024 500000' 'B 1048576 0' > shortages.txt",
                                      'cat shortages.txt',
                                      'du -sk .; ls -l'],
 'real-linux-capacity-trends': ['work=$(mktemp -d "$HOME/capacity-trends.XXXXXX"); cd "$work" && pwd',
                                "printf '%s\\n' 'day used_MiB' '0 200' '7 270' '14 340' '21 410' > "
                                'history.txt',
                                'cat history.txt',
                                'awk \'NR>1 {printf "day %2d %4d MiB ",$1,$2; for(i=0;i<int($2/50);i++) '
                                'printf "#"; print ""}\' history.txt > chart.txt; cat chart.txt',
                                'awk \'NR==2 {day=$1; used=$2; next} NR>2 {printf "days %d-%d: %g '
                                'MiB/day\\n",day,$1,($2-used)/($1-day); day=$1; used=$2}\' history.txt'],
 'real-linux-capacity-forecast': ['work=$(mktemp -d "$HOME/capacity-forecast.XXXXXX"); cd "$work" && pwd',
                                  "printf '%s\\n' 'day used_MiB' '0 200' '7 270' '14 340' '21 410' > "
                                  'history.txt',
                                  "awk 'NR==2 {first_day=$1; first_used=$2} NR>1 {last_day=$1; last_used=$2} "
                                  'END {rate=(last_used-first_used)/(last_day-first_day); limit=1000; '
                                  'reserve=100; if(rate<=0) {print "insufficient positive trend"; exit 1}; '
                                  'remaining=limit-reserve-last_used; printf "rate=%g MiB/day; headroom=%g '
                                  'MiB; days_after_last=%g; '
                                  'threshold_day=%g\\n",rate,remaining,remaining/rate,last_day+remaining/rate}\' '
                                  'history.txt > forecast.txt; cat forecast.txt',
                                  "printf '%s\\n' 'day used_MiB' '0 200' '7 190' '14 300' '21 210' > "
                                  'irregular.txt',
                                  'cat irregular.txt'],
 'real-linux-capacity-recommendation': ['work=$(mktemp -d "$HOME/capacity-recommendation.XXXXXX"); cd '
                                        '"$work" && pwd',
                                        '{ date -Is; nproc; uptime; free -m; df -Pk .; df -Pi .; } > '
                                        'baseline.txt; cat baseline.txt',
                                        "printf '%s\\n' 'day used_MiB' '0 200' '7 270' '14 340' '21 410' > "
                                        'history.txt',
                                        "awk 'NR==2 {first_day=$1; first_used=$2} NR>1 {last_day=$1; "
                                        'last_used=$2} END '
                                        '{rate=(last_used-first_used)/(last_day-first_day); limit=1000; '
                                        'reserve=100; if(rate<=0) {print "insufficient positive trend"; exit '
                                        '1}; remaining=limit-reserve-last_used; printf "rate=%g MiB/day; '
                                        'headroom=%g MiB; days_after_last=%g; '
                                        'threshold_day=%g\\n",rate,remaining,remaining/rate,last_day+remaining/rate}\' '
                                        'history.txt > forecast.txt; cat forecast.txt',
                                        "printf '%s\\n' 'LIVE FACTS: replace with dated observations' "
                                        "'SYNTHETIC PLAN: 10 MiB/day; 490 MiB headroom; 49 days after day "
                                        "21' 'ASSUMPTIONS: unchanged growth; 100 MiB reserve' "
                                        "'RECOMMENDATION: review before day 70; justify timing' 'MISSING "
                                        "EVIDENCE: workload changes and longer history' 'CLEANUP: no "
                                        "practice workload remains' > recommendation.txt",
                                        'nano recommendation.txt',
                                        'cat recommendation.txt; jobs -l']}
