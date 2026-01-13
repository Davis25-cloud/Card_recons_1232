import os
import re
import csv
from db_handler import insert_transactions_to_db

def parse_txt_file_to_csv_and_db(filepath, config, logger):
    logger.info(f"Parsing transaction file: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    transactions = []
    current_txn = []
    print("Lines:", lines)

    for line in lines:
        if 'Acct Number & Extension' in line:
                transaction = {}

                # Clean txn_lines
                txn_lines = txn_lines.replace('\n', ' ').replace('\r', '')

                # Extract using regex patterns
                transaction['report_id'] = re.search(r'REPORT (EP-\d+)', txn_lines).group(1)
                transaction['proc_date'] = re.search(r'E/P PROC\. DATE\s+(\d{2}/\d{2}/\d{2})', txn_lines).group(1)
                transaction['acct_number'] = re.search(r'Acct Number & Extension\s+(\d+)', txn_lines).group(1)
                transaction['acquirer_ref'] = re.search(r'Acquirer Reference Nbr\s+(\d+)', txn_lines).group(1)
                transaction['business_id'] = re.search(r"Acquirer's Business ID\s+(\d+)", txn_lines).group(1)
                transaction['purchase_date'] = re.search(r'Purchase Date\s+(\d+)', txn_lines).group(1)
                transaction['source_amount'] = re.search(r'Source Amount\s+(\d+)', txn_lines).group(1)
                transaction['source_currency'] = re.search(r'Source Currency Code\s+(\d+)', txn_lines).group(1)
                transaction['merchant_name'] = re.search(r'Merchant Name\s+([A-Z0-9\s&\-\']+?)\s{2,}', txn_lines).group(1).strip()
                transaction['merchant_city'] = re.search(r'Merchant City\s+([A-Z\s\-]+)', txn_lines).group(1).strip()
                transaction['merchant_country'] = re.search(r'Merchant Country Code\s+([A-Z]{2})', txn_lines).group(1)
                transaction['central_proc_date'] = re.search(r'Central Processing Date\s+(\d+)', txn_lines).group(1)
                transaction['merchant_cat_code'] = re.search(r'Merchant Category Code\s+(\d+)', txn_lines).group(1)
                transaction['terminal_id'] = re.search(r'Terminal ID\s+([A-Z0-9]+)', txn_lines).group(1)
                transaction['card_acceptor_id'] = re.search(r'Card Acceptor ID\s+([A-Z0-9]+)', txn_lines).group(1)

                return transaction
        current_txn.append(transactions)
        print(current_txn)
            # if current_txn:
            #     transactions.append(current_txn)
            #     current_txn = []
        if line.strip():
            current_txn.append(line.strip())

    if current_txn:
        transactions.append(current_txn)

    parsed_data = []
    for txn in transactions:
        data = extract_fields(txn)
        if data:
            parsed_data.append(data)

    if not parsed_data:
        logger.warning("No transactions parsed.")
        return

    output_dir = config['FILES']['output_dir']
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'parsed_transactions.csv')

    fieldnames = list(parsed_data[0].keys())
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_data)

    logger.info(f"Saved parsed transactions to {output_path}")
    insert_transactions_to_db(parsed_data, config, logger)

