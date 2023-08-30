import re     
from ..database import get_db, get_db1
from ..database import db_models
from .data_dump_config import datadump_core_settings
import pandas as pd




db = get_db1()

def get_client_nd_currency(fileid):
    client_name = ''
    client_currency = ''
    inputted_units_pattern = r"\$\'000|thousand|million|\$m|lakh|billion|hundred|crore"
    input_units = ""

    file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == fileid).order_by(db_models.FileLogs.time.desc()).first()
    page_query = db.query(db_models.PageLogs).filter(db_models.PageLogs.fileid == fileid).order_by(db_models.PageLogs.time.desc())
    pages = page_query.all()

    report_pg1n2_text = ""
    balance_sheet_page_number = sorted(file_query.filtered_cbs_pages)[0]

    #taking text data from first 2 pages of annual report
    for page in pages:
        if page.page_number < 2:
            ocr_query = db.query(db_models.OCRText).filter(db_models.OCRText.pageid == page.pageid)
            ocr_text_iter = ocr_query.all()
            for it1 in ocr_text_iter:            
                pg_txt = it1.raw_text
                report_pg1n2_text = report_pg1n2_text + pg_txt
        #extracting text from balance sheet page for various Input Units formats
        elif page.page_number == balance_sheet_page_number:
            ocr_query = db.query(db_models.OCRText).filter(db_models.OCRText.pageid == page.pageid)
            ocr_text_iter = ocr_query.all()
            for it1 in ocr_text_iter:            
                bs_pg_txt = it1.raw_text
                break

    #get all client data from asset folder to search for client name & currency
    client_data = pd.read_excel(datadump_core_settings.client_list)
    for idx,row in client_data.iterrows():
        #different cliets have different way of specifying Pty Ltd and Pvt Limited
        split_keywords = ['PTY LIMITED', 'PRIVATE LIMITED']

        for keys in split_keywords:
            client_name_to_search = (row['Client Name'].split(keys)[0].strip())

            if client_name_to_search.lower() in report_pg1n2_text.lower():
                client_name = row['Client Name']
                client_currency = row['Currency']
                break

    detected_units = list(set(re.findall(inputted_units_pattern, bs_pg_txt, re.IGNORECASE)))

    unit_mapping = {
        "hundred" : "Hundreds", "$'000" : 'Thousands', "thousand" : "Thousands", "lakh" : "Lakhs",  
            "million" : "Millions", "$m" : "Millions", "crore" : "Crores", "billion" : "Billions" 
        }

    if len(input_units) > 0:
        input_units = unit_mapping[detected_units[0]]
    else:
        input_units = "Full Value"
    print("client_name,client_currency,input_units", client_name,client_currency,input_units)

    return client_name,client_currency,input_units




