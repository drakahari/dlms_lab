"""Trusted child launcher; contains no shell or lesson-input interpreter."""
import os
import resource
import signal
import sys

if __name__=='__main__':
    ceiling=int(sys.argv[1])
    if not 1024*1024<=ceiling<=18*1024**3:raise ValueError('Invalid file ceiling')
    if sys.argv[2]!='/usr/bin/qemu-system-x86_64' or os.getuid()==0:
        raise ValueError('Expected trusted QEMU as an ordinary user')
    resource.setrlimit(resource.RLIMIT_FSIZE,(ceiling,ceiling))
    # EFBIG reaches QEMU's explicit werror=stop instead of SIGXFSZ killing it.
    # Ignored signal disposition persists through exec; verified by real I/O tests.
    signal.signal(signal.SIGXFSZ,signal.SIG_IGN)
    os.execv(sys.argv[2],sys.argv[2:])
