import re

def extract_transaction(text):
    transaction = {}

    # Clean text
    text = text.replace('\n', ' ').replace('\r', '')

    # Extract using regex patterns
    transaction['report_id'] = re.search(r'REPORT (EP-\d+)', text).group(1)
    transaction['proc_date'] = re.search(r'E/P PROC\. DATE\s+(\d{2}/\d{2}/\d{2})', text).group(1)
    transaction['acct_number'] = re.search(r'Acct Number & Extension\s+(\d+)', text).group(1)
    transaction['acquirer_ref'] = re.search(r'Acquirer Reference Nbr\s+(\d+)', text).group(1)
    transaction['business_id'] = re.search(r"Acquirer's Business ID\s+(\d+)", text).group(1)
    transaction['purchase_date'] = re.search(r'Purchase Date\s+(\d+)', text).group(1)
    transaction['source_amount'] = re.search(r'Source Amount\s+(\d+)', text).group(1)
    transaction['source_currency'] = re.search(r'Source Currency Code\s+(\d+)', text).group(1)
    transaction['merchant_name'] = re.search(r'Merchant Name\s+([A-Z0-9\s&\-\']+?)\s{2,}', text).group(1).strip()
    transaction['merchant_city'] = re.search(r'Merchant City\s+([A-Z\s\-]+)', text).group(1).strip()
    transaction['merchant_country'] = re.search(r'Merchant Country Code\s+([A-Z]{2})', text).group(1)
    transaction['central_proc_date'] = re.search(r'Central Processing Date\s+(\d+)', text).group(1)
    transaction['merchant_cat_code'] = re.search(r'Merchant Category Code\s+(\d+)', text).group(1)
    transaction['terminal_id'] = re.search(r'Terminal ID\s+([A-Z0-9]+)', text).group(1)
    transaction['card_acceptor_id'] = re.search(r'Card Acceptor ID\s+([A-Z0-9]+)', text).group(1)

    return transaction
with open("e:\Automation - Copy/Card_recon/visa_out_reports/outgoing/reports/25.06.2025 796346 REV/ep725.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

transaction = extract_transaction(text)
print(transaction)

#     return transactions
# if __name__ == "__main__":
#     # Example usage
#     filepath = "/Automation - Copy/Card_recon/visa_out_reports/outgoing/reports/25.06.2025 796346 REV/ep725.txt"
#     transactions = extract_transactions_from_txt(filepath=filepath)
#     for txn in transactions:
#         print(transactions)