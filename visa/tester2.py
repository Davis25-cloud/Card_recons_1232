import os
import re
import pandas as pd
import logging
from tqdm import tqdm
import mysql.connector as mysql

# --- logging setup ---
logging.basicConfig(
    filename='parse_vss_report.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- category mapping ---
txn_category_mapping = {
    "QUASI-CASH": ["QUASI-CASH", "TOTAL QUASI-CASH"],
    "ORIGINAL SALE": ["TOTAL ORIGINAL SALE", "ORIGINAL SALE"],
    "PURCHASE": ["PURCHASE", "TOTAL PURCHASE", "NET PURCHASE"],
    "DISPUTE FIN": ["DISPUTE FIN"],
    "DISPUTE RESP FIN": ["DISPUTE RESP FIN"],
}

def parse_amount(val):
    if not val:
        return 0.0
    val = val.replace(",", "")
    if val.endswith("CR"):
        return float(val[:-2])
    elif val.endswith("DB"):
        return -float(val[:-2])
    else:
        return float(val)

def parse_vss_reports(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    reports = re.split(r"(?=REPORT ID:\s+(VSS-120))", content)
    extracted_rows = []

    for report in tqdm(reports, desc=f"Extracting from {os.path.basename(file_path)}", unit="report", leave=False):

        if not report.strip().startswith("REPORT ID:  VSS-120"):
            continue

        if not re.search(r"REPORT ID:\s+(VSS-120)", report):
            logging.warning(f"Skipping chunk without VSS-120 ID in {file_path}")
            continue

        if not re.search(r"REPORTING FOR:\s+1000671034", report):
            logging.info(f"Skipping report not for 1000671034 in {file_path}")
            continue

        report_id = re.search(r"REPORT ID:\s+(VSS-120)", report).group(1)
        reporting_for = re.search(r"REPORTING FOR:\s+(\d+)", report)
        rollup_to = re.search(r"ROLLUP TO:\s+([A-Z0-9 ]+)", report)
        funds_xfer = re.search(r"FUNDS XFER ENTITY:\s+(\d+)", report)
        proc_date = re.search(r"PROC DATE:\s+(\d{2}[A-Z]{3}\d{2})", report)
        report_date = re.search(r"REPORT DATE:\s+(\d{2}[A-Z]{3}\d{2})", report)
        set_currency = re.search(r"SETTLEMENT CURRENCY:\s+([A-Z]+)", report)
        clear_currency = re.search(r"CLEARING CURRENCY:\s+([A-Z]+)", report)
        acquirer = re.search(r"ACQUIRER TRANSACTIONS", report)
        issuer = re.search(r"ISSUER TRANSACTIONS", report)
        business_type = acquirer.group(0) if acquirer else issuer.group(0) if issuer else ""

        txn_lines = re.findall(
            r"^\s*(?:(?P<type>[A-Z \-]+(?:\s+[A-Z]+))\s+)?(?:(?P<rate>A\d{4})\s+)?(?P<count>[\d,]+)\s+(?P<amount>[0-9,]+(?:\.\d{2})?(?:CR|DB)?)?(?:\s+(?P<credit>[0-9,]+(?:\.\d{2})?))?(?:\s+(?P<debit>[0-9,]+(?:\.\d{2})?))?",
            report, re.MULTILINE)

        for line in tqdm(txn_lines, desc=f"  Parsing lines", unit="txn", leave=False):
            txn_type, rate_id, count, amount, credit, debit = line
            if not count or not amount:
                continue

            txn_type = txn_type.strip() if txn_type else ""
            txn_category = next((cat for cat, lst in txn_category_mapping.items()
                                if any(t in txn_type.upper() for t in lst)), "UNKNOWN")
            is_original_sale = "TOTAL ORIGINAL SALE" in txn_type.upper()

            extracted_rows.append({
                "Source File": os.path.basename(file_path),   # ✅ keep file reference
                "Report ID": report_id,
                "Reporting For": reporting_for.group(1) if reporting_for else "",
                "Rollup To": rollup_to.group(1).strip().split()[0] if rollup_to else "",
                "Funds Xfer Entity": funds_xfer.group(1) if funds_xfer else "",
                "Proc Date": proc_date.group(1) if proc_date else "",
                "Report Date": report_date.group(1) if report_date else "",
                "Settlement Currency": set_currency.group(1) if set_currency else "",
                "Clearing Currency": clear_currency.group(1) if clear_currency else "",
                "Acq/Issuer": business_type,
                "Txn Type": txn_type,
                "Rate Table ID": rate_id.strip() if rate_id else "",
                "Count": count,
                "Clearing Amount": parse_amount(amount),
                "Interchange Credit": float(credit.replace(",", "")) if credit else 0.0,
                "Interchange Debit": float(debit.replace(",", "")) if debit else 0.0,
                "Original Sale": is_original_sale,
                "Transaction Category": txn_category
            })

    return extracted_rows

def load_to_mysql(df):
    try:
        conn = mysql.connect(
            host='127.0.0.1',
            user='Davis',
            password='Admin1998',
            database='pro_bank'
        )
        cursor = conn.cursor()

        # ✅ tqdm for row insert progress
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Loading to MySQL", unit="rows"):
            try:
                cursor.callproc('load_vss120', (
                    row['Report ID'],
                    row['Reporting For'],
                    row['Rollup To'],
                    row['Funds Xfer Entity'],
                    row['Proc Date'],
                    row['Report Date'],
                    row['Settlement Currency'],
                    row['Clearing Currency'],
                    row['Acq/Issuer'],
                    row['Txn Type'][:255],  # truncate if needed
                    row['Rate Table ID'],
                    int(row['Count'].replace(',', '')),
                    float(row['Clearing Amount']),
                    float(row['Interchange Credit']),
                    float(row['Interchange Debit']),
                    row['Original Sale'],
                    row['Transaction Category']
                ))

                logging.info(f"Loaded: Report ID={row['Report ID']} | Proc Date={row['Proc Date']} | Txn Type={row['Txn Type']}")

            except Exception as e:
                logging.error(f"Failed to insert row: Report ID={row['Report ID']} | Error: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("\n✅ Data loaded successfully into MySQL.")

    except Exception as db_error:
        logging.critical(f"MySQL connection failed: {db_error}")
        print("❌ MySQL connection error.")



if __name__ == "__main__":
    input_folder = r"E:\Automation - Copy\Card_recon\original reports"
    output_path = r"E:\Automation - Copy\Card_recon\extracted_reports\parsed_vss_reports_all.csv"

    all_rows = []
    files = [f for f in os.listdir(input_folder) if f.upper().startswith("EP747B 0809") and f.endswith(".txt")]
    total_files = len(files)

    # Outer loop – count progress like 0/3 → 1/3 → 2/3 → 3/3
    for file_idx, fname in enumerate(files, start=1):
        fpath = os.path.join(input_folder, fname)
        print(f"\n📄 Processing file {file_idx}/{total_files}: {fname}")

        # Inner bar – progress while parsing lines of this report
        with open(fpath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        file_rows = []
        for line in tqdm(lines, desc=f"Parsing {fname}", unit="line", leave=False):
            # You already parse whole file in parse_vss_reports,
            # so here we just simulate inner progress
            pass  

        # Now actually parse file and append results
        file_rows.extend(parse_vss_reports(fpath))
        all_rows.extend(file_rows)

        print(f"✅ Finished {fname} ({file_idx}/{total_files}) → Extracted {len(file_rows)} rows")

    
    # Save combined results
    df = pd.DataFrame(all_rows)

    # Load to MySQL
    load_to_mysql(df)

    if not df.empty:
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n✅ Saved {len(df)} rows from {total_files} files to {output_path}")
    else:
        print("\n⚠️ No rows extracted from any file.")

    
