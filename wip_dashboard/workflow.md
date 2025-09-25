# Excel Pivot Dashboard – Refresh Workflow

This document outlines the end-to-end flow to refresh the Excel workbook (with Power Query) and view the embedded dashboard, plus how to diagnose issues.

## Files
- `wip_dashboard/dashboard.html` – Embedded Excel view with Refresh/Open buttons.
- `wip_dashboard/refresh_excel.ps1` – PowerShell automation (Excel Desktop) to Refresh All and save.
- `wip_dashboard/README.md` – Setup and scheduling notes.
- `wip_dashboard/workflow.md` – This workflow.

## Prerequisites
- Excel Desktop installed on the machine running the script.
- Access to the workbook in SharePoint/OneDrive.
- Recommended: if using OneDrive local path, set the file to "Always keep on this device".
- Alternatively, use the direct SharePoint URL ending with `.xlsx`.

## Step-by-step Workflow
1. Obtain workbook location
   - Option A (local OneDrive path): `C:\Users\<you>\OneDrive - <Org>\Inventory_Overview_live.xlsx`
   - Option B (SharePoint URL): `https://<tenant>.sharepoint.com/sites/<site>/.../Inventory_Overview_live.xlsx`

2. Optional: Close all Excel instances to avoid locks/prompts
   ```powershell
   Get-Process EXCEL -ErrorAction SilentlyContinue | Stop-Process -Force
   ```

3. Run the refresh script
   ```powershell
   # From project root: SQL_agent
   powershell -NoProfile -ExecutionPolicy Bypass -File .\wip_dashboard\refresh_excel.ps1 -WorkbookUrl "<path or URL to .xlsx>" -TimeoutSeconds 1800
   ```

4. Monitor the log
   ```powershell
   Get-Content .\wip_dashboard\refresh_log.txt -Wait
   ```
   - You should see:
     - "Starting refresh for ..."
     - "Calling Workbook.RefreshAll()"
     - Heartbeats: `Heartbeat: t=XXs CalcState=... RefreshingConns=...`
     - "Refresh completed. Saving..."
     - "Saved workbook. Closing..."

5. Validate the result
   - Check workbook last write time:
     ```powershell
     (Get-Item "<path to .xlsx>").LastWriteTime
     ```
   - Open `wip_dashboard/dashboard.html` and click Refresh.

6. Schedule (optional)
   - Use Task Scheduler to run `refresh_excel.ps1` on an always-on machine (server/VM).

## Current Blocking Step (Marked)
- **[BLOCKER] Step 3 – Run the refresh script**
  - Symptom from console: `Invoke-WithRetry : The term 'Invoke-WithRetry' is not recognized...` (CommandNotFoundException)
  - Root cause: in `wip_dashboard/refresh_excel.ps1`, the helper function `Invoke-WithRetry` is used to open the workbook before the function is defined. This ordering causes the call to fail.
  - Temporary workaround:
    - Use the previous `Workbooks.Open(...)` line without the retry wrapper, or run after we patch the file to move the `Invoke-WithRetry` definition above the first use.
  - Proposed fix (to apply next):
    - Move the `Invoke-WithRetry { ... }` function block above any calls to it (notably the initial `Workbooks.Open`), or avoid using it for that call.

## Troubleshooting Guide
- **Excel busy (0x800AC472)**
  - The script now retries and sets calculation to manual during refresh. If still stuck, close Excel instances and rerun.
- **Excel cannot access the file**
  - Ensure the OneDrive file is locally available (Always keep on this device) or use the SharePoint `.xlsx` URL.
  - Make sure the file is not open in another Excel instance.
- **Credentials/Privacy prompts**
  - Manually open the workbook in Excel Desktop → Data → Refresh All once, approve dialogs, save, close Excel, then rerun the script.
- **No logs or UNC path error**
  - Logging now writes to `wip_dashboard/refresh_log.txt`. The log path is resolved next to the script; folders are created automatically.

## Success Criteria
- Log shows: `Refresh completed. Saving...` followed by `Excel closed. Done.`
- Workbook LastWriteTime updates to the current run time.
- Dashboard displays the latest values after clicking Refresh in `dashboard.html`.
