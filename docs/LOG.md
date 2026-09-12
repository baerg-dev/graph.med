# Log

One entry per session, newest first. Past about 200 lines, move the oldest
entries to `docs/LOG-ARCHIVE.md`, newest first there too; never delete.

## 2026-09-12 — agent
Packages touched: WP-0001 … WP-0016 (registered)
Branch: conventions/work-packages
Notable: migrated the register from `data/PROGRESS.yaml` (passes and chunks per
source) via a short-lived `WORK.yaml` to `docs/work/`, one markdown file per
package with the handoff and history layers kept apart (`docs/HANDOFF.md`,
`docs/LOG.md`); see ADR-0001. Nothing lost: every deferred item is in
`docs/work/LATER.md` or a package. The physician's review of 2026-09-11 was
partitioned into the four initiatives under `docs/work/initiatives/`.
