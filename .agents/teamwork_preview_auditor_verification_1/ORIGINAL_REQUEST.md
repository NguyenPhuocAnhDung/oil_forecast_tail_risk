## 2026-07-17T14:19:01Z
Your working directory is /data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_auditor_verification_1/.
Perform a forensic integrity audit on the workspace `/data/quyhv/oil_forecast_tail_risk`.
Specifically:
1. Verify that all 17 Markdown reports exist under `docs/research_os/` (from `stage0_dataset_governance.md` to `stage16_workflow_audit.md`).
2. Run econometric audits to ensure mathematical and data consistency by running the Q1 audit script:
   `.venv\Scripts\python.exe scripts/q1_audit.py`
   Ensure it passes without errors.
3. Run the end-to-end dry run test script:
   `.venv\Scripts\python.exe scripts/e2e_test.py`
   Ensure it compiles and runs successfully.
4. Verify that there is no look-ahead bias or data leakage.
5. Write your forensic audit report to `/data/quyhv/oil_forecast_tail_risk/.agents/teamwork_preview_auditor_verification_1/handoff.md`. In the handoff, specify the audit verdict (CLEAN or VIOLATION) and document the execution logs of the audit scripts.
When done, send a message back to parent conversation ID 53d1d6fc-5e29-43fe-b494-a6aaa3afca7b.
