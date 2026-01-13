import re
import pandas as pd
import logging
from tqdm import tqdm  # <-- Progress bar

# Setup logger
logging.basicConfig(filename='parse_vss_report.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_vss_reports(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:

        content = file.read()

    reports = re.split(r"(?=REPORT ID:\s+(VSS-120|VSS-116))", content)
    extracted_rows = []
    unmatched_lines = []

    # Transaction category mapping based on your examples
    txn_category_mapping = {
        "QUASI-CASH": ["QUASI-CASH", "TOTAL QUASI-CASH"],
        "ORIGINAL SALE": ["TOTAL ORIGINAL SALE", "ORIGINAL SALE"],
        "PURCHASE": ["PURCHASE", "TOTAL PURCHASE", "NET PURCHASE"],
        "DISPUTE FIN": ["DISPUTE FIN"],
        "DISPUTE RESP FIN": ["DISPUTE RESP FIN"],
    }
    
    for report in tqdm(reports, desc="Parsing reports", unit="report"):
        if not report.strip().startswith("REPORT ID:  VSS-120"):
            continue

        # Extract metadata
        report_id_match = re.search(r"REPORT ID:\s+(VSS-120|VSS-116)", report)
        report_id = report_id_match.group(1) if report_id_match else "Unknown"

        logging.info(f"Processing report: {report_id}")

        reporting_for = re.search(r"REPORTING FOR:\s+(\d+)", report)
        reporting_for = reporting_for.group(1) if reporting_for else ""

        rollup_to = re.search(r"ROLLUP TO:\s+([A-Z0-9 ]+)", report)
        rollup_to = rollup_to.group(1).strip().split()[0] if rollup_to else ""

        funds_xfer = re.search(r"FUNDS XFER ENTITY:\s+(\d+)", report)
        funds_xfer = funds_xfer.group(1) if funds_xfer else ""

        proc_date = re.search(r"PROC DATE:\s+(\d{2}[A-Z]{3}\d{2})", report)
        proc_date = proc_date.group(1) if proc_date else ""

        report_date = re.search(r"REPORT DATE:\s+(\d{2}[A-Z]{3}\d{2})", report)
        report_date = report_date.group(1) if report_date else ""

        set_currency = re.search(r"SETTLEMENT CURRENCY:\s+([A-Z]+)", report)
        set_currency = set_currency.group(1) if set_currency else ""

        clear_currency = re.search(r"CLEARING CURRENCY:\s+([A-Z]+)", report)
        clear_currency = clear_currency.group(1) if clear_currency else ""

        business_type_issuer = re.search(r"ISSUER TRANSACTIONS",report)
        business_type_acquirer = re.search(r"ACQUIRER TRANSACTIONS",report)
        if business_type_acquirer:

            business_type = business_type_acquirer.group(0) 
        elif    business_type_issuer:
            business_type = business_type_issuer.group(0)
        else:
            pass

        #print(business_type)
        # Transaction blocks
                    
        txn_lines_1 = re.findall(
            r"^\s*(?:(?P<type>[A-Z \-]+(?:\s+[A-Z]+))\s+)?(?:(?P<rate>A\d{4})\s+)?(?P<count>[\d,]+)\s+(?P<amount>[0-9,]+(?:\.\d{2})?(?:CR|DB)?)?(?:\s+(?P<credit>[0-9,]+(?:\.\d{2})?))?(?:\s+(?P<debit>[0-9,]+(?:\.\d{2})?))?",
            report, re.MULTILINE)

        txn_lines_2 = re.findall(
            r"^\s*(?:(?P<type>[A-Z]+\s+))?(?:(?P<rate>A\d{4})\s+)?(?P<count>[\d,]+)\s+(?P<amount>[0-9,]+(?:\.\d{2})?(?:CR|DB)?)?(?:\s+(?P<credit>[0-9,]+(?:\.\d{2})?))?(?:\s+(?P<debit>[0-9,]+(?:\.\d{2})?))?",
            report, re.MULTILINE)
        


        if not txn_lines_1:
            logging.warning(f"No transaction lines found in report {report_id}")

        current_txn_type = ""
        for line in txn_lines_1:
            txn_type, rate_id, count, amount, credit, debit = line
            #print(txn_type, rate_id, count, amount, credit, debit)
            if txn_type:
                current_txn_type = txn_type.strip()
            

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

            is_original_sale = "TOTAL ORIGINAL SALE" in txn_type.upper()

            if not count or not amount:
                unmatched_lines.append(line)
                logging.warning(f"Unmatched or incomplete line in report {report_id}: {line}")
                continue

            # Determine Transaction Category
            txn_category = "UNKNOWN"  # Default category if no match
            for category, txn_list in txn_category_mapping.items():
                if any(txn in txn_type.upper() for txn in txn_list):
                    txn_category = category
                    break

            extracted_rows.append({
                "Report ID": report_id,
                "Reporting For": reporting_for,
                "Rollup To": rollup_to,
                "Funds Xfer Entity": funds_xfer,
                "Proc Date": proc_date,
                "Report Date": report_date,
                "Settlement Currency": set_currency,
                "Clearing Currency": clear_currency,
                "Acq/Issuer": business_type,
                "Txn Type": current_txn_type,
                "Rate Table ID": rate_id.strip() if rate_id else "",
                "Count": (count),
                "Clearing Amount": parse_amount(amount),
                "Interchange Credit": float(credit.replace(",", "")) if credit else 0.0,
                "Interchange Debit": float(debit.replace(",", "")) if debit else 0.0,
                #"Transaction Category": tran_category,  # New column added for the category
                "Original Sale": is_original_sale
            })
            
 
        df = pd.DataFrame(extracted_rows)
        df.to_excel("E:\Automation - Copy\Card_recon\extracted_reports\parsed_vss_report_with_original_sale.xlsx", index=False, engine='openpyxl')
    #print("Data inserted")

    if unmatched_lines:
        print("\n--- Unmatched Lines ---")
        for line in unmatched_lines:
            print('line',line)

    return df

# === USAGE ===
if __name__ == "__main__":
    input_path = "E:\Automation - Copy\Card_recon\original reports\ep747b.txt"
    output_path = "vss-120_report.xlsx"
    parse_vss_reports(input_path)
