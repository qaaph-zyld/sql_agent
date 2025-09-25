# WIP Dashboard (SharePoint Excel)

This folder contains:

- `dashboard.html` — Embedded Excel view with Refresh/Open buttons.
- `refresh_excel.ps1` — PowerShell script to refresh all queries (including Power Query) via Excel Desktop automation and save the workbook.

## Important

- Excel for the web cannot refresh Power Query. The HTML page reloads the embedded view only.
- To run refresh regardless of a specific laptop, schedule `refresh_excel.ps1` on an always-on Windows machine (server/VM) that has Excel installed and access to the SharePoint file.

## Configure `refresh_excel.ps1`

1. Get the direct link to the `.xlsx` file:
   - In SharePoint, open the library → select the workbook → Copy link (ensure it points to the `.xlsx`).
   - If the link ends with `?web=1`, keep it; Excel can open it. If it points to `Doc.aspx`, obtain a direct `.xlsx` link from the file menu.
2. Edit the script or pass the parameter:
   ```powershell
   # Edit inside the script
   $WorkbookUrl = "https://mysite.adient.com/.../YourWorkbook.xlsx"

   # or pass at runtime
   powershell -ExecutionPolicy Bypass -File .\refresh_excel.ps1 -WorkbookUrl "https://mysite.adient.com/.../YourWorkbook.xlsx"
   ```

## Run once (manual)

```powershell
# From this folder
powershell -ExecutionPolicy Bypass -File .\refresh_excel.ps1 -WorkbookUrl "https://mysite.adient.com/.../YourWorkbook.xlsx"
```

## Schedule on a server (Task Scheduler)

1. Ensure Microsoft Excel is installed and licensed for the task account.
2. Create a service account (or use an existing one) with permissions to the SharePoint file.
3. On the server, open Task Scheduler → Create Task.
   - General: Run whether user is logged on or not; Run with highest privileges.
   - Triggers: New → set frequency (e.g., every hour) or at specific times.
   - Actions: New → Program/script:
     ```
     powershell
     ```
     Arguments:
     ```
     -ExecutionPolicy Bypass -File "C:\path\to\wip_dashboard\refresh_excel.ps1" -WorkbookUrl "https://mysite.adient.com/.../YourWorkbook.xlsx"
     ```
     Start in:
     ```
     C:\path\to\wip_dashboard
     ```
   - Conditions/Settings per your policy (e.g., wake the computer, stop if runs longer than X minutes).
4. Test: Right-click the task → Run. Check `refresh_log.txt` for status.

## HTML page

- Place `dashboard.html` in any shared location. It uses your provided embed link and offers:
  - Refresh (reload) — useful if pivots are set to refresh on open and for non-PQ data.
  - Open in Excel Online — for quick edits.
  - Open in Excel Desktop — for full query refresh.

## Troubleshooting

- If the script logs a timeout, increase `-TimeoutSeconds`.
- If the task runs but does not save, confirm the account has edit rights and that the link is a direct `.xlsx` URL.
- If Excel remains in background, add a short delay after `Quit()` or ensure no modal dialogs are shown (DisplayAlerts is off).
- Some environments block `ms-excel` URL scheme in browsers; Task Scheduler/PowerShell does not rely on it.
