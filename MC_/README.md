Mastercard acquiring recon

Usage

- Set environment variables (optional):
  - `MC_BASE_DIR` - base directory containing input Excel files
  - `MC_LOE_FILE` - LOE filename (default LOE20250219.xlsx)
  - `MC_OUT_FILE` - Outgoing filename
  - `MC_REPORTS_DIR` - output directory for reports (default mc_reports)
  - `MC_LOG_FILE` - path to conversion.log

- Run the CLI:

```bash
python run_recon.py --base-dir "E:\Automation - Copy\Card_recon\original reports" \
    --loe-file LOE20250219.xlsx --out-file "All Outgoing Transaction Details TWI_2025_02_20_080441.xlsx" \
    --report-dir "E:\Automation - Copy\Card_recon\MC_\mc_reports"
```

Files created
- multiple Excel reports saved in `mc_reports`.

Notes
- The notebook `Mastercard_Acquiring.ipynb` references the same functions; prefer running the CLI for repeatable runs.
