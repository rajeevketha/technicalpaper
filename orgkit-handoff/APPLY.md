# Apply OrgKit 1.8.1 Org Compare updates to chromeplugins

This cloud agent run was attached to `rajeevketha/technicalpaper` and cannot push to `rajeevketha/chromeplugins`.

## Apply onto PR #6 branch

```bash
git clone https://github.com/rajeevketha/chromeplugins.git
cd chromeplugins
git checkout cursor/orgkit-org-compare-047e
git pull --ff-only
git bundle unbundle path/to/orgkit-org-compare-1.8.1.bundle
# or
git am path/to/orgkit-org-compare-1.8.1.patch
git push origin cursor/orgkit-org-compare-047e
```

Version: **1.8.1** (Session Workbench 1.8.0 + Org Compare UX)
