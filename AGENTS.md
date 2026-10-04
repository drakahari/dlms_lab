# Learning Lab agent guidance

## Work and scope
- Work in this repository; preserve unrelated changes and neighboring projects.
- Inspect Git status, the requested baseline, and applicable instructions first.
  Before application changes, create or verify a recovery snapshot. Keep personal
  profile backups outside the source tree; enforce writer consistency.
- Own routine implementation, instructional review, grading, persistence,
  compatibility and regression testing. Continue through authorized checkpoints
  when their criteria pass. Owner UAT is optional, not a routine completion or
  commit gate. Request a targeted owner check only for a material verification gap.
- Stop and explain before an unapproved engine/contract extension, data migration,
  backup-format change, identity change or substantial architecture expansion.
  A content-only task permits none of those changes.

## Safety and compatibility
- Existing engines run learner commands only against trusted simulated state and
  virtual files. A future VM backend requires separate explicit authorization and
  architecture review; this standalone VM proof does not authorize app integration.
  Never execute learner commands on the host or let them access host files,
  processes or networks. Any authorized VM practice must remain inside the guest
  with declared isolation and reset boundaries. Real GNU reference commands belong
  only in static developer fixtures, outside learner runtime.
- Scenario packs are bounded, validated, versioned data, never executable code.
  Reject unsupported syntax, capabilities and versions explicitly; document the
  supported subset without implying full Linux or full LPIC objective coverage.
- Preserve accepted pack identities, versions and canonical content unless the
  task explicitly authorizes a change. Preserve older contracts, pinned attempts,
  Learn/Challenge distinction, drafts, history and supported backup compatibility.
  Never fabricate legacy provenance or silently replace imports or visibility.
- Preserve the approved UI. Keep domain behavior independent of QML and storage.
  Do not touch real profiles or the working installation during development.
  Mutating tests use disposable data/config directories and isolated fixtures.

## Verified repository commands
Run these from `app/` with the project's Python/PySide6 environment:

```bash
python3 -B -m unittest discover -s tests -v
python3 -B tools/validate_scenario.py path/to/scenario.lab.json
PYTHONPATH=. python3 -B tests/text_gnu_reference.py
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME='' QT_QUICK_BACKEND=software QT_SCALE_FACTOR=1 \
  python3 -B tests/text_unit_acceptance.py --offscreen --expected-dpr 1 --label text-review-100
```

- Run the full suite for a feature/commit review and relevant targeted suites.
  For UI changes, use affected acceptance scripts at 100/150/200% and supported
  compact/wide sizes; match `QT_SCALE_FACTOR` and `--expected-dpr`.
- For packaging changes, build/install the actual wheel in separate temporary
  environments; copy `tools/installed_smoke.py` outside the checkout and run it
  using that wheel-installed venv's `python -I -B ... --require-icon`.
  Follow `docs/user-installation.md`; never substitute a source import for this.
- Report exact results, runtime and evidence. Separate offscreen QtTest input,
  native rendering, physical keyboard and accessibility checks. Record owner
  feedback only for the reported workflows. Keep unverified checks outstanding;
  investigate warnings rather than suppressing them.

## Authorization and delivery
- Routine source edits and isolated tests within an approved task need no repeated
  acknowledgement. Ask before deleting/migrating real data, installing system-wide
  software, provisioning VMs/containers, creating credentials or changing groups,
  services, networking, security or desktop settings.
- Stage/commit/push only when explicitly authorized in the session. Review exact
  candidate paths for secrets, personal data and generated artifacts; preserve
  excluded local files. Verify staged paths and bytes, then run
  `git diff --cached --check`. Do not force-push.
- Use normal elevated approval requests for blocked Git commands. Never change
  permissions, remove locks or initialize/replace/repair Git metadata to bypass
  restrictions. If blocked, provide exact reviewed paths/hashes and host commands.
- A source commit or push does not authorize installation, deployment or publishing.
  Updating the working app needs separate authorization; retain its profile paths
  and installer preparation/rollback safeguards.
- Finish with changed files, test results, limitations, Git status and concise
  launch/import or acceptance instructions where relevant.
