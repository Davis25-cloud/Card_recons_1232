#!/usr/bin/env python3
import argparse
from pathlib import Path
import os
from mc_recon import load_files, clean_loe, clean_outgoing, filter_mc_acquiring, build_keys, match_and_flag, analytics, export_reports
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mc_recon')


def main():
    p = argparse.ArgumentParser(description='Run Mastercard acquiring recon')
    p.add_argument('--base-dir', default=os.environ.get('MC_BASE_DIR'), help='Base directory for input files')
    p.add_argument('--loe-file', default=os.environ.get('MC_LOE_FILE'), help='LOE filename')
    p.add_argument('--out-file', default=os.environ.get('MC_OUT_FILE'), help='Outgoing filename')
    p.add_argument('--report-dir', default=os.environ.get('MC_REPORTS_DIR', 'mc_reports'), help='Output report dir')
    args = p.parse_args()

    base = Path(args.base_dir) if args.base_dir else Path.cwd()
    loe_path = base / args.loe_file
    out_path = base / args.out_file
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    df_loe, df_out = load_files(loe_path, out_path)
    df_loe = clean_loe(df_loe)
    df_out = clean_outgoing(df_out)

    accounts = ["KES1403441530001", "KES1666600010001","USD1403441530001", "USD1666600010001"]
    mc_loe = filter_mc_acquiring(df_loe, accounts)
    mc_out = df_out.copy()
    mc_loe, mc_out = build_keys(mc_loe, mc_out)
    mc_loe = match_and_flag(mc_loe, mc_out)

    summary = analytics(mc_loe, mc_out)
    reports = {
        'filter_loe': mc_loe,
        'filter_outgoing': mc_out,
        'matched_loe': mc_loe,
        'Investigation_report': None,
        'analytics_summary': summary
    }
    saved = export_reports(reports, report_dir)
    logger.info(f'Saved reports: {saved}')

if __name__ == '__main__':
    main()
