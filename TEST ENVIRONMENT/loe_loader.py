import mysql.connector
import pandas as pd

# ✅ Connect to MySQL
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="Davis@25",
    database="Pro_bank"
)
cursor = conn.cursor()
print("Connection made successfully")

# ✅ File List
file_list = [ "RWFLOE20250219.xlsx", "TZSLOE20250219.xlsx", "UGXLOE20250219.xlsx"]

# ✅ Map filename to corresponding stored procedure
procedure_map = {
    "LOE": "InsertLOEData",
    "BIF": "InsertBIFLOEData",
    "TZS": "InsertTZSLOEData",
    "UGX": "InsertUGXLOEData",
    "RWF": "InsertRWFLOEData"
}

# ✅ Process Each File
for file in file_list:
    print(f"\nReading file: {file}")
    df = pd.read_excel(file, sheet_name=1, engine="openpyxl")

    # Clean column names
    df.columns = [col.strip() for col in df.columns]
    df["No"] = df["No"].astype(str).str.replace(",", "").str.strip().astype(int)

    print(f"Processing file: {file}...........")

    # Determine the stored procedure to use
    procedure_prefix = file[:3].upper()  # e.g. "LOE", "BIF"
    procedure_name = procedure_map.get(procedure_prefix)

    if not procedure_name:
        print(f"❌ No procedure mapped for file: {file}. Skipping.")
        continue

    # Convert to list of tuples
    data = [tuple(x) for x in df.itertuples(index=False, name=None)]

    # Execute the stored procedure for each row
    for row in data:
        cursor.callproc(procedure_name, row)
    conn.commit()

    # Status message
    first_column_name = df.columns[0]
    file_date = df[first_column_name].iloc[0]
    print(f"✅ {df.shape[0]} rows inserted successfully for LOE dated {file_date} using procedure `{procedure_name}`.")

# ✅ Close connection
cursor.close()
conn.close()
print("\nAll files processed and connection closed.")
