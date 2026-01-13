CREATE TABLE All_outgoing (
ORIGID VARCHAR(255), 
ID VARCHAR(25), 
NETWORK VARCHAR(25), 
ORIGTRANID VARCHAR(25), 
EXPTRANID VARCHAR(255), 
ORIGSEQ VARCHAR(25), 
TRANNUMBER VARCHAR(25), 
TRANTYPE VARCHAR(25), 
TRANCODE VARCHAR(25),  
EXPBATCHID VARCHAR(25), 
ORIGINALAMT DECIMAL(18,2), 
ORIGINALCCY VARCHAR(10), 
PAN VARCHAR(25), 
TERMNAME VARCHAR(255), 
CARDACCEPTORID VARCHAR(25), 
APPROVALCODE VARCHAR(50), 
EXPARN VARCHAR(255), 
ORIGTIME DATETIME, 
BUSINESS_DAY DATETIME, 
PSTRANID VARCHAR(255), 
RRN VARCHAR(25),



    PRIMARY KEY (ORIGID, ID, EXPTRANID) 
);

 
     INSERT INTO main_loe (
        `Date`, `DocNo`, `No`, `Debit_External`, `Debit_Account`, `Cur_D`, `Debit_Amount`, 
        `Credit_External`, `Credit_Account`, `Cur_C`, `Credit_Amount`, `Entry_Identifier`, 
        `PAN`, `Card_product`, `Additional_Customer_info`
    ) 
    VALUES (
        p_Date, p_DocNo, p_No, p_Debit_External, p_Debit_Account, p_Cur_D, p_Debit_Amount, 
        p_Credit_External, p_Credit_Account, p_Cur_C, p_Credit_Amount, p_Entry_Identifier, 
        p_PAN, p_Card_Product, p_Additional_Customer_Info
    );
    
    
CREATE TABLE main_loe (
Date VARCHAR(20),
 DocNo int,
 No_  VARCHAR(50),
 Debit_External VARCHAR(25),
 Debit_Account VARCHAR(25),
 Cur_D INTEGER(3),
 Debit_Amount DECIMAL(60,2),
 Credit_External VARCHAR(25),
 Credit_Account VARCHAR(25),
 Cur_C INT,
 Credit_Amount DECIMAL(60 ,2),
 Entry_Identifier TEXT,
 PAN VARCHAR(25),
 Card_product VARCHAR (50),
 Additional_Customer_info VARCHAR(50),
 PRIMARY KEY ( Date,DocNo,No_)
 );