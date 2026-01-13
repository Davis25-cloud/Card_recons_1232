import pandas as pd
from pathlib import Path
import pytest

from mc_recon import clean_loe, clean_outgoing, filter_mc_acquiring, build_keys, match_and_flag, export_reports


def make_sample_loe():
    data = {
        'Debit External': [' KES1403441530001 ', 'USD1403441530001'],
        'Credit External': ['KES1666600010001', ' USD1666600010001 '],
        'PAN': ['4000000000000001', '4000000000000002'],
        'Debit Amount': [100.0, 200.0],
        'Entry Identifier': ['normal', 'ADJUSTMENT']
    }
    return pd.DataFrame(data)


def make_sample_out():
    data = {
        'PAN': ['4000000000000001', '4000000000000003'],
        'ORIGINALAMT': ['100.0', '300.0'],
        'EXPTRANID': ['abc0000000012345xxxxx', 'def0000000023456xxxxx'],
        'NETWORK': [22, 22],
        'ORIGID': ['KCBK', 'KCBK']
    }
    return pd.DataFrame(data)


def test_clean_loe_strips():
    df = make_sample_loe()
    out = clean_loe(df.copy())
    assert out['Debit External'].iloc[0] == 'KES1403441530001'
    assert out['Credit External'].iloc[1] == 'USD1666600010001'


def test_clean_outgoing_types():
    df = make_sample_out()
    out = clean_outgoing(df.copy())
    assert out.loc[0, 'ORIGINALAMT'] == 100.0
    assert out.loc[1, 'EXPTRANID'] == 'def0000000023456xxxxx'[:25]


def test_filter_mc_acquiring_and_filter_adjustment():
    df = make_sample_loe()
    accounts = ["KES1403441530001", "KES1666600010001","USD1403441530001", "USD1666600010001"]
    mc = filter_mc_acquiring(df, accounts)
    # One row should be filtered out because Entry Identifier is ADJUSTMENT
    assert mc.shape[0] == 1
    assert mc['Debit External'].iloc[0] == 'KES1403441530001'


def test_build_keys_and_match():
    loe = make_sample_loe()
    out = make_sample_out()
    loe_clean = clean_loe(loe.copy())
    out_clean = clean_outgoing(out.copy())
    accounts = ["KES1403441530001", "KES1666600010001","USD1403441530001", "USD1666600010001"]
    mc_loe = filter_mc_acquiring(loe_clean, accounts)
    mc_out = out_clean.copy()
    mc_loe, mc_out = build_keys(mc_loe, mc_out)
    mc_loe = match_and_flag(mc_loe, mc_out)
    assert 'key' in mc_loe.columns
    assert 'Status' in mc_loe.columns


def test_export_reports(tmp_path):
    df = pd.DataFrame({'a': [1,2]})
    reports = {'r1': df}
    saved = export_reports(reports, tmp_path)
    assert saved['r1'] is not None
    assert Path(saved['r1']).exists()
