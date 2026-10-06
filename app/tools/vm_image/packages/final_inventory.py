"""Pure developer-build admission check; never an app or lesson execution path."""
import re

BEGIN = 'LEARNING_LAB_INVENTORY_BEGIN'
END = 'LEARNING_LAB_INVENTORY_END'
DONE = 'LEARNING_LAB_IMAGE_FINALIZED'
ROW = re.compile(r'[a-z0-9][a-z0-9+.:~-]*\t[^\s]+\t[^\s]+\t[^\s]+')


def finalized_inventory(console, expected):
    if len(console.encode('utf-8')) > 4 * 1024 * 1024:
        raise ValueError('Finalization log exceeds limit')
    if any(console.count(marker) != 1 for marker in (BEGIN, END, DONE)):
        raise ValueError('Missing or repeated finalization marker')
    start = console.index(BEGIN) + len(BEGIN)
    end = console.index(END)
    if not start < end < console.index(DONE):
        raise ValueError('Finalization markers out of order')
    rows = console[start:end].strip('\r\n').splitlines()
    if not rows or any(ROW.fullmatch(row) is None for row in rows):
        raise ValueError('Malformed final inventory')
    actual = ('\n'.join(rows) + '\n').encode('ascii')
    if actual != expected:
        raise ValueError('Exact finalized package inventory differs; no admission')
    return actual
