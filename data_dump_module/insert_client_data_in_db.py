import pandas as pd
import json, re
from sqlalchemy import MetaData, Table, create_engine
from ..database import get_db1, engine
from ..database import db_models
import os
from os import path

db = get_db1()


def get_client_details_from_CCIF(fileid):

    mizuho_ccif, cust_full_nm, currency, input_units, CCIF_num = '','','','',''
    #get mizuho_ccif, client name, currency
        # json_file = open(r"enate_client_info.json")
    json_file = open(os.path.join(path.dirname(__file__),'./enate_client_info.json'))
    enate_data = json.load(json_file)
    json_file.close()
    CCIF_num = int(enate_data['CCIFNumber'])

    
    # query = 'SELECT * FROM public."Client_Financial_Dump"'
    # client_data_sql = pd.read_sql_query(query, con=engine)
    query = db.query(db_models.Client_Financial_Dump)
    client_data_sql = pd.read_sql(query.statement, query.session.bind)
    # print(f"client_data_sql = {client_data_sql}")
    mizuho_ccif = client_data_sql[client_data_sql['cif_no']==CCIF_num]['mizuho_ccif'][0]
    cust_full_nm = client_data_sql[client_data_sql['cif_no']==CCIF_num]['cust_full_nm'][0].strip()
    currency = client_data_sql[client_data_sql['cif_no']==CCIF_num]['ccy_cd'][0]
    # print(client_data_sql[client_data_sql['cif_no']==CCIF_num])

    #find inputted units format
    file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == fileid).order_by(db_models.FileLogs.time.desc()).first()
    page_query = db.query(db_models.PageLogs).filter(db_models.PageLogs.fileid == fileid).order_by(db_models.PageLogs.time.desc())
    pages = page_query.all()
    try:
        balance_sheet_page_number = sorted(file_query.filtered_cbs_pages)[0]
    except:
        balance_sheet_page_number = sorted(file_query.filtered_cpl_pages)[0]

    
    try:
        for page in pages:
            #extracting text from balance sheet page for various Input Units formats
            if page.page_number == balance_sheet_page_number:
                ocr_query = db.query(db_models.OCRText).filter(db_models.OCRText.pageid == page.pageid)
                ocr_text_iter = ocr_query.all()
                for it1 in ocr_text_iter:            
                    bs_pg_txt = it1.raw_text
                    break

        inputted_units_pattern = r"\$\'000|\$000|thousand|million|\$m|lakh|billion|hundred|crore"

        detected_units = list(set(re.findall(inputted_units_pattern, bs_pg_txt, re.IGNORECASE)))

        unit_mapping = {
            "hundred" : "Hundreds", "$'000" : 'Thousands', "$000" : 'Thousands', "thousand" : "Thousands", "lakh" : "Lakhs",  
                "million" : "Millions", "$m" : "Millions", "crore" : "Crores", "billion" : "Billions" 
            }

        if len(detected_units) > 0:
            input_units = unit_mapping[detected_units[0]]
        else:
            input_units = "Full Value"
    except Exception as e:
        mizuho_ccif, cust_full_nm, currency, input_units, CCIF_num = '','','','',''
        pass
    print(mizuho_ccif, cust_full_nm, currency, input_units, CCIF_num)
    return mizuho_ccif, cust_full_nm, currency, input_units, CCIF_num

 


# with open(r'UAT_app\assets\cdm_excel_template\FINANCIAL Dump.csv') as f:
#     client_data_dump = pd.read_csv(f)
#     reqd_cols = ['MIZUHO_CCIF', 'CIF_NO', 'CUST_FULL_NM', 'CCY_CD']
#     client_data_dump = client_data_dump[reqd_cols]
#     client_data_dump.drop_duplicates(inplace=True)
#     client_data_dump.dropna(inplace=True)
#     client_data_dump['MIZUHO_CCIF'] = client_data_dump['MIZUHO_CCIF'].astype(int)
#     client_data_dump['CIF_NO'] = client_data_dump['CIF_NO'].astype(int)
#     client_data_dump.shape
#     client_data_dump.to_csv(r'UAT_app\assets\cdm_excel_template\cleaned_FINANCIAL Dump.csv', header=True, index=False)











# ### do not use
# #first delete existing rows in db
# conn = create_engine('postgresql+psycopg2://postgres:admin@203.90.50.26:5432/crm_syd_dev').connect()#.raw_connection()
# table = Table('Client_Financial_Dump', MetaData())
# conn.execute(table.delete())


# client_data_dump = pd.read_csv(r'UAT_app\assets\cdm_excel_template\FINANCIAL Dump.csv')
# reqd_cols = ['MIZUHO_CCIF', 'CIF_NO', 'CUST_FULL_NM', 'CCY_CD']
# client_data_dump = client_data_dump[reqd_cols]
# client_data_dump.drop_duplicates(inplace=True)
# client_data_dump.dropna(inplace=True)
# client_data_dump['MIZUHO_CCIF'] = client_data_dump['MIZUHO_CCIF'].astype(int)
# client_data_dump['CIF_NO'] = client_data_dump['CIF_NO'].astype(int)
# client_data_dump.shape
# client_data_dump.to_csv(r'UAT_app\assets\cdm_excel_template\cleaned_FINANCIAL Dump.csv', header=True, index=False)




# # import data from csv into db table
# with open(r'UAT_app\assets\cdm_excel_template\cleaned_FINANCIAL Dump.csv') as f:    
#     conn = create_engine('postgresql+psycopg2://postgres:admin@203.90.50.26:5432/crm_syd_dev').raw_connection()
#     cursor = conn.cursor()
#     cmd = 'COPY public."Client_Financial_Dump"(mizuho_ccif, cif_no, cust_full_nm, ccy_cd) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)'
#     cursor.copy_expert(cmd, f)
#     conn.commit()
