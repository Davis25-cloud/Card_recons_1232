#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[87]:


print("Processing Files started. This might take a minute... PLEASE WAIT.")
ken_loe = pd.read_excel("E:\Automation\Card_recon\original reports\LOE20250219.xlsx", sheet_name=1, engine="openpyxl")
tzs_loe = pd.read_excel("E:\Automation\Card_recon\original reports\TZSLOE20250219.xlsx", sheet_name=1, engine="openpyxl")
ugx_loe = pd.read_excel("E:\Automation\Card_recon\original reports\UGXLOE20250219.xlsx", sheet_name=1, engine="openpyxl")
rwf_loe = pd.read_excel("E:\Automation\Card_recon\original reports\RWFLOE20250219.xlsx", sheet_name=1, engine="openpyxl")
print("\nLoe file (s) read...\nProceeding to outgoing... PLEASE WAIT")


df_outgoing = pd.read_excel("E:\Automation\Card_recon\original reports\All Outgoing Transaction Details TWI_2025_02_20_080441.xlsx", sheet_name=0, engine="openpyxl", header=1)
print("\nOutgoing file read...\nProceeding to Analysis... PLEASE WAIT")


# In[88]:


def clean_dataframe(df):
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))
    df.columns = df.columns.str.strip()
    return df

ugx_loe = clean_dataframe(ugx_loe)
tzs_loe = clean_dataframe(tzs_loe)
rwf_loe = clean_dataframe(rwf_loe)
ken_loe = clean_dataframe(ken_loe)


# In[89]:


#LOE FILTERS

tzs_acquiring = ["USD1403441530033","TZS1403441530033","USD1666600010033","TZS1666600010066"]
ugx_acquiring = ["UGX1403400010022","UGX1666600010022","USD1666600010022","USD1403441530001"]
rwf_acquiring = ["RWF1666600010044","USD1403441530001","USD1666600010066","RWF1403441530001"]
ken_acquiring = ["KES1666600010001","USD1403441530001","USD1666600010001","KES1403441530001"]

tz_mc_loe = tzs_loe[tzs_loe["Debit External"].isin(tzs_acquiring)&tzs_loe["Credit External"].isin(tzs_acquiring)]

rwf_mc_loe = rwf_loe[rwf_loe["Debit External"].isin(rwf_acquiring)&rwf_loe["Credit External"].isin(rwf_acquiring)]

ugx_mc_loe = ugx_loe[ugx_loe["Debit External"].isin(ugx_acquiring)&ugx_loe["Credit External"].isin(ugx_acquiring)]
ken_mc_loe = ken_loe[ken_loe["Debit External"].isin(ken_acquiring)&ken_loe["Credit External"].isin(ken_acquiring)]

ugx_mc_loe.reset_index(drop=True)



#DATA CLEANING FOR OUTGOING

# ✅ Convert Data Types
df_outgoing["ORIGINALAMT"] = pd.to_numeric(df_outgoing["ORIGINALAMT"], errors="coerce").fillna(0.00).abs()
df_outgoing["ORIGTIME"] = pd.to_datetime(df_outgoing["ORIGTIME"], errors="coerce").fillna(pd.Timestamp("1970-01-01"))
df_outgoing["BUS. DAY"] = pd.to_datetime(df_outgoing["BUS. DAY"], errors="coerce").fillna(pd.Timestamp("1970-01-01"))

df_outgoing["EXPTRANID"] = df_outgoing["EXPTRANID"].astype(str).str[:25]  # Keep only first 25 characters

targ_network = [22]
targ_origid = ['KCBK']
targ_date = ['2025-02-19']
mc_acquiring_out = df_outgoing[
        df_outgoing["NETWORK"].isin(targ_network)#& df_outgoing["ORIGID"].isin(targ_origid)#&df_outgoing["BUS. DAY"].astype(str).isin(targ_date)
]


# In[90]:


currencies = {
    "tz": tz_mc_loe,
    "ug": ugx_mc_loe,
    "rw": rwf_mc_loe,
    'ke': ken_mc_loe
}

# Ensure mc_acquiring_out is not a slice
mc_acquiring_out = mc_acquiring_out.copy()
mc_acquiring_out.loc[:, 'key'] = mc_acquiring_out['PAN'].astype(str) + mc_acquiring_out['ORIGINALAMT'].astype(str)

for code, df in currencies.items():
    df = df.copy()  # Ensure you're working with a fresh copy
    df.loc[:, 'key'] = df['PAN'].astype(str).str.strip() + df['Debit Amount'].astype(str)
    df.loc[:, 'Status'] = df['key'].isin(mc_acquiring_out['key']).map({True: 'matched', False: 'Non-matched'})
    #save to excel
    df.to_excel(f"{code}_matched_loe.xlsx", index=False)

    # ✅ Print only non-matched rows
    non_matched = df[df['Status'] == 'Non-matched']
    print(f"\n{code.upper()} - Non-matched Rows ({len(non_matched)} found):")
    print(non_matched)


# In[106]:


loes = {
    "tz": tz_mc_loe,
    "ug": ugx_mc_loe,
    "rw": rwf_mc_loe,
    'ken': ken_mc_loe
}


currency_codes = {
    "USD": {"debit": ['USD1403441530001','USD1403441530033'], "credit": ['USD1666600010001','USD1666600010022','USD1666600010033','USD1666600010066']},
    "KES": {"debit": ['KES1403441530001'], "credit": ['KES1666600010001']},
    "RWF": {"debit": ['RWF1403441530001'], "credit": ['RWF1666600010044']},
    "TZS": {"debit": ['TZS1403441530033'], "credit": ['TZS1666600010066']},
    "UGX": {"debit": ['UGX1403400010022'], "credit": ['UGX1666600010022']}
}

results ={}
for curr, acc in currency_codes.items():

    debit_codes = acc['debit']
    credit_codes = acc['credit']
    
    for country, loe in loes.items():

        loe_sale = loe[loe['Debit External'].isin(debit_codes)&loe['Credit External'].isin(credit_codes)]
        loe_rev = loe[loe['Credit External'].isin(debit_codes)&loe['Debit External'].isin(credit_codes)]

        sale_amt = loe_sale['Debit Amount'].sum()
        sale_count = loe_sale.shape[0]

        if sale_count > 0 or sale_amt > 0:
            results[(country, curr, 'SALE')] = {
                'Count': sale_count,
                'Amount': sale_amt
            }

        rev_count = loe_rev['Debit Amount'].count()
        rev_amt = loe_rev['Debit Amount'].sum()

        if rev_count > 0 or rev_amt > 0:
            results[(country, curr, 'REV')] = {
                'Count': rev_count,
                'Amount': rev_amt
            }

        if sale_amt != 0 or rev_amt != 0:
            print(f"{country.upper()} - {curr}: SALE count: {sale_count:,}, Amount: {sale_amt:,.2f} | REV count: {rev_count:,}, Amount: {rev_amt:,.2f}")


# In[117]:


rwf_sale = results.get(('rw', 'RWF', 'SALE'), {'Count': 0, 'Amount': 0})
rwf_rev = results.get(('rw', 'RWF', 'REV'), {'Count': 0, 'Amount': 0})

rwf_sale_usd = results.get(('rw', 'USD', 'SALE'), {'Count': 0, 'Amount': 0})
rwf_rev_usd = results.get(('rw', 'USD', 'REV'), {'Count': 0, 'Amount': 0})

tzs_sale = results.get(('tz','TZS', 'SALE'), {'Count': 0, 'Amount': 0})
tzs_rev = results.get(('tz','TZS', 'REV'), {'Count': 0, 'Amount': 0})

tzs_sale_usd = results.get(('tz','USD', 'SALE'), {'Count': 0, 'Amount': 0})
tzs_rev_usd = results.get(('tz','USD', 'REV'), {'Count': 0, 'Amount': 0})

ugx_sale = results.get(('ug','UGX', 'SALE'), {'Count': 0, 'Amount': 0})
ugx_rev = results.get(('ug','UGX', 'REV'), {'Count': 0, 'Amount': 0})

ugx_sale_usd = results.get(('ug','USD', 'SALE'), {'Count': 0, 'Amount': 0})
ugx_rev_usd = results.get(('ug','USD', 'REV'), {'Count': 0, 'Amount': 0})

ken_sale = results.get(('ke','KES', 'SALE'), {'Count': 0, 'Amount': 0})
ken_rev = results.get(('ke','KES', 'REV'), {'Count': 0, 'Amount': 0})

ken_sale_usd = results.get(('ke','USD', 'SALE'), {'Count': 0, 'Amount': 0})
ken_rev_usd = results.get(('ke','USD', 'REV'), {'Count': 0, 'Amount': 0})

print(f"RWF Sale Amount: {tzs_sale_usd['Amount']:,.2f}")
print(f"RWF Rev Amount: {tzs_rev_usd['Amount']:,.2f}")  # Will show 0 if not found


# In[ ]:




