"""App-owned JSON storage. Archives are retained, never automatically pruned."""
import json
import os
from pathlib import Path
import re
import tempfile
from uuid import UUID

from .domain.validation import decode, keys, require, applied_state, ValidationError

MAX_RECORD = 10 * 1024 * 1024


class NewerSchema(ValidationError):
    pass


def _validate_record(raw, pack, *, hint_limit=3):
    data = decode(raw, MAX_RECORD)
    require(isinstance(data, dict), "Invalid progress object.")
    expected_version = 2 if 'firewall' in pack else 1
    if type(data.get("schema_version")) is int and data["schema_version"] > expected_version:
        raise NewerSchema("Progress uses a newer schema. The original file is preserved; this session is read-only.")
    keys(data, {"schema_version", "attempt"}, "progress")
    require(type(data["schema_version"]) is int and data["schema_version"] == expected_version, "Unsupported progress schema; no migration exists.")
    a = data["attempt"]
    keys(a, {"id", "lab_id", "content_version", "mode", "started", "updated", "ended", "end_reason",
             "applied", "draft", "revision", "hints", "console", "commands", "assessments"}, "attempt")
    require(isinstance(a["id"], str), "Invalid attempt ID.")
    try:
        require(str(UUID(a["id"])) == a["id"], "Noncanonical attempt ID.")
    except (ValueError, AttributeError) as exc:
        raise ValidationError("Invalid attempt ID.") from exc
    require(a["lab_id"] == pack["lab_id"], "Saved lab ID does not match the installed pack.")
    if a["content_version"] != pack["content_version"]:
        raise NewerSchema("Saved pack version differs from the installed pack. Original progress is preserved; this session is read-only.")
    require(a["mode"] in ("Learn", "Challenge"), "Invalid attempt mode.")
    for field in ("started", "updated", "ended"):
        require((a[field] is None and field == "ended") or (isinstance(a[field], str) and len(a[field]) <= 64), "Invalid timestamp.")
        if a[field] is not None:
            from datetime import datetime
            try:
                require(datetime.fromisoformat(a[field]).tzinfo is not None, "Timestamp must include timezone.")
            except ValueError as exc:
                raise ValidationError("Invalid timestamp.") from exc
    require(a["end_reason"] in (None, "reset", "mode-change"), "Invalid attempt end reason.")
    require(applied_state(pack, a["applied"]) == a["applied"], "Invalid applied state.")
    source = next(iter(pack["initial_state"]))
    editable = set(pack["editable_fields"][source])
    fixed = {k: v for k, v in pack["initial_state"][source].items() if k not in editable}
    require(all(a["applied"][k] == v for k, v in fixed.items()), "Saved fixed setting differs from the scenario.")
    require(isinstance(a["draft"], dict) and set(a["draft"]) <= editable | ({'firewall'} if 'firewall' in pack else set()), "Invalid drafts.")
    require(all(isinstance(v, str) and len(v) <= 128 for k,v in a["draft"].items() if k != 'firewall'), "Invalid draft value.")
    if 'firewall' in a['draft']:
        from .domain.firewall import draft_policy
        draft_policy(a['draft']['firewall'])
    require(type(a["revision"]) is int and a["revision"] >= 0, "Invalid revision.")
    require(type(a["hints"]) is int and 0 <= a["hints"] <= hint_limit, "Invalid hints.")
    require(a["mode"] == "Learn" or a["hints"] == 0, "Challenge attempt cannot contain hint usage.")
    for field, limit, length in (("console", 500, 2048), ("commands", 100, 512)):
        require(isinstance(a[field], list) and len(a[field]) <= limit and all(isinstance(v, str) and len(v) <= length for v in a[field]), "Invalid console history.")
    require(isinstance(a["assessments"], dict), "Invalid assessment history.")
    from .domain.engine import Engine
    for rev, result in a["assessments"].items():
        require(re.fullmatch(r"0|[1-9][0-9]*", rev) is not None and len(rev) <= 12 and int(rev) <= a["revision"], "Invalid assessment revision.")
        keys(result, {"score", "complete", "objectives", "revision", "submitted", "hints_at_submission", "applied"}, "assessment")
        require(type(result["revision"]) is int and result["revision"] == int(rev), "Revision mismatch.")
        require(type(result["hints_at_submission"]) is int and 0 <= result["hints_at_submission"] <= a["hints"], "Invalid submission hints.")
        require(isinstance(result["submitted"], str) and len(result["submitted"]) <= 64, "Invalid submission date.")
        saved_state = applied_state(pack, result["applied"])
        require(all(saved_state[k] == v for k, v in fixed.items()), "Submission changed a fixed setting.")
        if int(rev) == a["revision"]:
            require(saved_state == a["applied"], "Current submission does not match applied settings.")
        grade = Engine(pack, saved_state).grade()
        require(all(result[k] == grade[k] for k in ("score", "complete", "objectives")), "Saved rubric does not match applied state.")
    return a


def validate_record(raw, pack, *, hint_limit=3):
    try:
        return _validate_record(raw, pack, hint_limit=hint_limit)
    except (TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise ValidationError("Malformed progress structure.") from exc


def encode(attempt):
    version = 2 if isinstance(attempt.get('applied'), dict) and 'firewall' in attempt['applied'] else 1
    return json.dumps({"schema_version": version, "attempt": attempt}, ensure_ascii=False, indent=2).encode()


def atomic_write(path, raw):
    path = Path(path)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, root, pack):
        self.root = Path(root)
        self.pack = pack
        self.root.mkdir(parents=True, exist_ok=True)
        self.archives = self.root / "attempts"
        self.archives.mkdir(exist_ok=True)
        self.current = self.root / "current.json"
        self.backup = self.root / "current.backup.json"
        self.read_only = False
        self.notice = ""

    def encode_record(self, attempt):
        return encode(attempt)

    def validate_record(self, raw):
        return validate_record(raw, self.pack)

    def read(self, path):
        with Path(path).open("rb") as stream:
            raw = stream.read(MAX_RECORD + 1)
        return raw, self.validate_record(raw)

    def load(self):
        if not self.current.exists():
            if not self.backup.exists():
                return None
            self.notice = "Current progress was missing. Recovered the last-known-good backup."
            try:
                raw, attempt = self.read(self.backup)
                atomic_write(self.current, raw)
                return attempt
            except (OSError, ValidationError) as exc:
                self.read_only = True
                self.notice = f"Recovery required: {exc} Files are preserved."
                return None
        try:
            return self.read(self.current)[1]
        except NewerSchema as exc:
            self.read_only = True
            self.notice = str(exc)
            return None
        except (OSError, ValidationError) as exc:
            try:
                raw, attempt = self.read(self.backup)
                # Preserve the exact damaged primary before replacing it.
                from datetime import datetime, timezone
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                preserved = self.root / f"current.corrupt-{stamp}.json"
                os.replace(self.current, preserved)
                atomic_write(self.current, raw)
                self.notice = f"Recovered the last-known-good backup. Damaged progress preserved as {preserved.name}. The newest unsaved changes may be absent."
                return attempt
            except (OSError, ValidationError):
                self.read_only = True
                self.notice = f"Recovery required: {exc} Current and backup files are preserved. Close the app and follow docs/recovery.md."
                return None

    def save(self, attempt):
        if self.read_only:
            raise ValidationError("Progress is read-only. Original files remain preserved.")
        raw = self.encode_record(attempt)
        self.validate_record(raw)
        if self.current.exists():
            previous, _ = self.read(self.current)
            atomic_write(self.backup, previous)
        else:
            atomic_write(self.backup, raw)
        atomic_write(self.current, raw)

    def archive(self, attempt):
        if self.read_only:
            raise ValidationError("Progress is read-only.")
        raw = self.encode_record(attempt)
        self.validate_record(raw)
        path = self.archives / f"{attempt['id']}.json"
        if path.exists():
            previous, _ = self.read(path)
            if previous == raw:
                return
        atomic_write(path, raw)

    def history(self, current_id, page=0):
        # Read only one page of attempt bodies; disk records are never pruned.
        files = sorted(self.archives.glob("*.json"), key=lambda p: p.stat().st_mtime_ns, reverse=True)
        rows, warnings = [], []
        filtered = [p for p in files if p.stem != current_id]
        for path in filtered[page * 25:(page + 1) * 25]:
            try:
                _, attempt = self.read(path)
                rows.append(attempt)
            except (OSError, ValidationError) as exc:
                warnings.append(f"Preserved unreadable history {path.name}: {exc}")
        return rows, len(filtered), warnings
