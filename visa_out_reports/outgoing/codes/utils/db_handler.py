import mysql.connector

def init_db(config, logger):
    try:
        conn = mysql.connector.connect(
            host=config['DATABASE']['host'],
            user=config['DATABASE']['user'],
            password=config['DATABASE']['password'],
            database=config['DATABASE']['database']
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255),
                file_type VARCHAR(50),
                status VARCHAR(50),
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"DB Init error: {str(e)}")

def log_to_db(filename, file_type, status, config, logger):
    try:
        conn = mysql.connector.connect(
            host=config['DATABASE']['host'],
            user=config['DATABASE']['user'],
            password=config['DATABASE']['password'],
            database=config['DATABASE']['database']
        )
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO file_logs (filename, file_type, status)
            VALUES (%s, %s, %s)
        """, (filename, file_type, status))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"DB log error: {str(e)}")


def insert_transactions_to_db(parsed_data, config, logger):
    db_cfg = config['DATABASE']
    try:
        conn = mysql.connector.connect(
            host=db_cfg['host'],
            user=db_cfg['user'],
            password=db_cfg['password'],
            database=db_cfg['database']
        )
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO outgoing_txn_logs (
            acct_number, reference_no, purchase_date, source_amount, source_currency,
            authorization_code, merchant_name, merchant_city, merchant_country,
            mcc, terminal_id, card_acceptor_id, auth_response_code, product_id,
            txn_identifier, authorized_amount, surcharge_amount, surcharge_sign,
            surcharge_indicator, transaction_type, pan_token, created_at
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, NOW()
        )
        """

        for txn in parsed_data:
            cursor.execute(insert_query, (
                txn.get("Acct Number & Extension"),
                txn.get("Acquirer Reference Nbr"),
                txn.get("Purchase Date"),
                txn.get("Source Amount"),
                txn.get("Source Currency Code"),
                txn.get("Authorization Code"),
                txn.get("Merchant Name"),
                txn.get("Merchant City"),
                txn.get("Merchant Country Code"),
                txn.get("Merchant Category Code"),
                txn.get("Terminal ID"),
                txn.get("Card Acceptor ID"),
                txn.get("Authorization Response Cd"),
                txn.get("Product Id"),
                txn.get("Transaction Identifier"),
                txn.get("Authorized Amount"),
                txn.get("Surcharge Amount"),
                txn.get("Interchange Fee Sign"),
                txn.get("Surcharge Credit/Dbt Ind"),
                txn.get("Transaction Type"),
                txn.get("PAN Token")
            ))

        conn.commit()
        logger.info(f"{cursor.rowcount} transactions inserted.")
        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"DB insert failed: {e}")