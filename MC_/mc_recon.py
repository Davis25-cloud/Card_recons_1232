import pandas as pd
from pathlib import Path
from typing import Tuple, List
import logging

logger = logging.getLogger('mc_recon')


def load_files(loe_path: Path, outgoing_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load LOE and outgoing Excel files into DataFrames."""
    loe = pd.read_excel(str(loe_path), sheet_name=1, engine='openpyxl')
    out = pd.read_excel(str(outgoing_path), sheet_name=0, engine='openpyxl', header=1)
    return loe, out


def validate_columns(df: pd.DataFrame, required: List[str], name: str = 'df') -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        logger.error(f"Missing columns in {name}: {missing}")
        raise KeyError(f"Missing columns in {name}: {missing}")


def clean_loe(df_loe: pd.DataFrame) -> pd.DataFrame:
    # Strip strings in object columns
    for col in df_loe.select_dtypes(include=['object', 'string']).columns:
        df_loe[col] = df_loe[col].astype(str).str.strip()
    df_loe.columns = df_loe.columns.str.strip()
    return df_loe


def clean_outgoing(df_out: pd.DataFrame) -> pd.DataFrame:
    df_out = df_out.copy()
    df_out['ORIGINALAMT'] = pd.to_numeric(df_out.get('ORIGINALAMT', 0), errors='coerce').fillna(0.0).abs()
    df_out['ORIGTIME'] = pd.to_datetime(df_out.get('ORIGTIME'), errors='coerce').fillna(pd.Timestamp('1970-01-01'))
    df_out['BUS. DAY'] = pd.to_datetime(df_out.get('BUS. DAY'), errors='coerce').fillna(pd.Timestamp('1970-01-01'))
    if 'EXPTRANID' in df_out.columns:
        df_out['EXPTRANID'] = df_out['EXPTRANID'].astype(str).str[:25]
    return df_out


def filter_mc_acquiring(df_loe: pd.DataFrame, accounts: List[str]) -> pd.DataFrame:
    df_loe = df_loe.copy()
    df_loe['Debit External'] = df_loe['Debit External'].astype(str).str.strip()
    df_loe['Credit External'] = df_loe['Credit External'].astype(str).str.strip()
    df_loe['Entry Identifier'] = df_loe['Entry Identifier'].astype(str).str.strip()
    mc = df_loe[df_loe['Debit External'].isin(accounts) & df_loe['Credit External'].isin(accounts)].copy()
    mc = mc[~mc['Entry Identifier'].str.upper().eq('ADJUSTMENT')]
    mc = mc.reset_index(drop=True)
    return mc


def build_keys(mc_loe: pd.DataFrame, mc_out: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    mc_loe = mc_loe.copy()
    mc_out = mc_out.copy()
    mc_loe.loc[:, 'key'] = mc_loe['PAN'].astype(str).str.strip() + mc_loe['Debit Amount'].astype(str)
    mc_out.loc[:, 'key'] = mc_out['PAN'].astype(str).str.strip() + mc_out['ORIGINALAMT'].astype(str)
    return mc_loe, mc_out


def match_and_flag(mc_loe: pd.DataFrame, mc_out: pd.DataFrame) -> pd.DataFrame:
    mc_loe = mc_loe.copy()
    mc_loe.loc[:, 'Status'] = mc_loe['key'].isin(mc_out['key']).map({True: 'matched', False: 'Non-matched'})
    return mc_loe


def analytics(mc_loe: pd.DataFrame, mc_out: pd.DataFrame) -> pd.DataFrame:
    # Minimal analytics summary, similar to notebook
    usd_debit = ['USD1403441530001']
    usd_credit = ['USD1666600010001']
    loe_usd_sale = mc_loe[mc_loe['Debit External'].isin(usd_debit)]
    loe_usd_rev = mc_loe[mc_loe['Debit External'].isin(usd_credit)]
    total_usd = loe_usd_sale['Debit Amount'].sum() - loe_usd_rev['Debit Amount'].sum()
    count_usd = loe_usd_sale.shape[0] + loe_usd_rev.shape[0]

    kes_debit = ['KES1403441530001']
    kes_credit = ['KES1666600010001']
    loe_kes_sale = mc_loe[mc_loe['Debit External'].isin(kes_debit)]
    loe_kes_rev = mc_loe[mc_loe['Debit External'].isin(kes_credit)]
    total_kes = loe_kes_sale['Debit Amount'].sum() - loe_kes_rev['Debit Amount'].sum()
    count_kes = loe_kes_sale.shape[0] + loe_kes_rev.shape[0]

    data = {
        'Reports': ['LOE', '', 'Total_', 'Outgoing', '', 'Total', 'Diffs Total', ''],
        'Currency': ['USD', 'KES', '', 'USD', 'KES', '', 'USD', 'KES'],
        'Count': [count_usd, count_kes, count_usd+count_kes, None, None, None, None, None],
        'Amount': [total_usd, total_kes, None, None, None, None, None, None]
    }
    return pd.DataFrame(data)


def export_reports(reports: dict, report_dir: Path) -> dict:
    """Given a dict name->DataFrame, save them to report_dir and return mapping name->path."""
    saved = {}
    for name, df in reports.items():
        if df is None:
            continue
        path = report_dir / f"{name}.xlsx"
        try:
            df.to_excel(path, index=False)
            saved[name] = str(path)
            logger.info(f"Saved report {name} -> {path}")
        except Exception as e:
            logger.exception(f"Failed to save report {name}: {e}")
            saved[name] = None
    return saved
