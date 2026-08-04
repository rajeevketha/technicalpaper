# Apply OrgKit 1.8.1 Org Compare updates to chromeplugins PR #6

This cloud agent run was attached to `rajeevketha/technicalpaper` and cannot push to `rajeevketha/chromeplugins` (GitHub App 403).

Target: branch `cursor/orgkit-org-compare-047e` on https://github.com/rajeevketha/chromeplugins/pull/6

## Recommended: git bundle (includes merge + UX commits)

```bash
git clone https://github.com/rajeevketha/chromeplugins.git
cd chromeplugins
git checkout cursor/orgkit-org-compare-047e
git fetch .
git bundle unbundle path/to/orgkit-org-compare-1.8.1.bundle
git merge --ff-only e3e1061b2e003eb5ce59a2461207e4c766f70bf4
# or: git reset --hard e3e1061b2e003eb5ce59a2461207e4c766f70bf4
git push origin cursor/orgkit-org-compare-047e
```

## Alternative: binary diff against current PR tip (`91b9cca`)

```bash
git checkout cursor/orgkit-org-compare-047e
git apply orgkit-org-compare-1.8.1.binary.diff
git add -A
git commit -m "Merge Workbench + Org Compare UX as 1.8.1"
git push origin cursor/orgkit-org-compare-047e
```

## Test without applying

Unzip `OrgKit-1.8.1-unpacked.zip` → Chrome Load unpacked.

## Versioning

- **1.8.0** — Session Workbench (PR #5)
- **1.8.1** — Workbench + Org Compare dual-org UX (this change)
