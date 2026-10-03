"""Read-only validation of self-contained scenario JSON using the installed engine."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from learning_lab.portable import LIMIT, load_portable
from learning_lab.domain.validation import ValidationError


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packs',nargs='+',type=Path)
    args=parser.parse_args();failed=False
    for path in args.packs:
        try:
            if not path.is_file():raise ValidationError('Expected a regular JSON file.')
            with path.open('rb') as stream:raw=stream.read(LIMIT+1)
            scenario=load_portable(raw)
            print(f'VALID {path}: {scenario.identity.scenario_id} {scenario.identity.content_version} '
                  f'{scenario.pin["engine"]["behavior_version"]} {scenario.identity.content_digest}')
        except (OSError,ValidationError) as exc:
            print(f'INVALID {path}: {exc}',file=sys.stderr);failed=True
    return int(failed)


if __name__=='__main__':raise SystemExit(main())
