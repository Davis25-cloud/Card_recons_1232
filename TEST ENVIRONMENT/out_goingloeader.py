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

# ✅ Read Excel File
df = pd.read_excel("All_Outgoing.xlsx", sheet_name=0, engine="openpyxl", header=1)

print("File Read...\nProcessing for loading to DB")

# ✅ Clean Column Names
df.columns = df.columns.str.strip()

print(f"Columns{df.columns}")

# ✅ Convert Data Types
df["ORIGINALAMT"] = pd.to_numeric(df["ORIGINALAMT"], errors="coerce").fillna(0.00)
df["ORIGTIME"] = pd.to_datetime(df["ORIGTIME"], errors="coerce").fillna(pd.Timestamp("1970-01-01"))
df["BUS. DAY"] = pd.to_datetime(df["BUS. DAY"], errors="coerce").fillna(pd.Timestamp("1970-01-01"))

# ✅ Replace NaN with Empty Strings for Text Columns
df.fillna("", inplace=True)

# ✅ Convert DataFrame to List of Tuples
data = [tuple(x) for x in df.itertuples(index=False, name=None)]

print("Parsing file(s) complete... Loading to DB... Please wait...")

# ✅ Execute the Stored Procedure for Each Row
for row in data:
    try:
        cursor.callproc("LoadAllOutgoingData", row)
    except mysql.connector.Error as err:
        print(f"Error inserting row {row}: {err}")

conn.commit()  # ✅ Commit After Batch Processing

# ✅ Close Connection
cursor.close()
conn.close()

print("Data successfully loaded into LoadAllOutgoingData procedure!")
