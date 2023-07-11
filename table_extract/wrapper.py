import os
from .TE_core import TECore
from .config import core_settings,settings
from ..database.database import get_db, get_db1
from ..database import db_models
from copy import deepcopy
from typing import List,Dict
import pandas as pd

db = get_db1()



class TEWrapper():
    def __init__(self) -> None:
        self.fileid:str
        self.min_page : int
        self.filename : str
        self.filtered_cbs_pages : List
        self.filtered_cpl_pages : List
        self.filtered_ccf_pages : List
        self.all_filtered_pages : List
        self.table_dict:Dict
        self.page_number : int
        self.page_dict : Dict = {}

    def process_file(self,fileid:str):
        self.fileid=fileid
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: TableExtractionService , File:wrapper.py,  function: process_file")
        Logger.logr.debug("TE process file started")
        self.get_predicted_page_info()
        self.process_pages()
        # file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == self.fileid)
        # temp_dict = {}
        # temp_dict['status'] = 'Table Extraction Completed'
        # file_query.update(temp_dict, synchronize_session=False)
        Logger.logr.debug("TE Proces file completed")

    def process_page(self):
        pass

    def process_cropped_notes(self):
        pass
        #self.process_notes()

    def process_notes(self):
        pass

    def get_predicted_page_info(self):
        file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == self.fileid).order_by(db_models.FileLogs.time.desc()).first()
        self.filename = file_query.filename
        self.filtered_cbs_pages = file_query.filtered_cbs_pages
        self.filtered_cpl_pages = file_query.filtered_cpl_pages
        self.filtered_ccf_pages = file_query.filtered_ccf_pages
        self.all_filtered_pages = deepcopy(self.filtered_cbs_pages)
        self.all_filtered_pages.extend(self.filtered_cpl_pages)
        self.all_filtered_pages.extend(self.filtered_ccf_pages)
        self.min_page = min(self.all_filtered_pages)
        # file_query2 = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == self.fileid)
        # temp_dict = {}
        # temp_dict['status'] = 'Table Extraction in progress'
        # file_query2.update(temp_dict, synchronize_session=False)
        return self.min_page


    def process_pages(self):
        te_core = TECore()
        page_query = db.query(db_models.PageLogs).filter(db_models.PageLogs.fileid == self.fileid).order_by(db_models.PageLogs.time.desc())
        pages = page_query.all()
        paged_dict : Dict = {}
        processed_pages = []
        for page in pages:
            # if page.page_number >= self.min_page:
            if page.page_number not in processed_pages:
                if page.page_number >= self.min_page:
                # if page.page_number == 30:
                    self.page_number = page.page_number
                    te_core.process_pdf(page.pageid)
                    self.table_dict = te_core.get_table
                    paged_dict.update({page.page_number: self.table_dict})
                    processed_pages.append(page.page_number)
        self.page_dict = paged_dict
        self.save_to_excel()

    def save_to_excel(self):
        fname = self.filename.split('.')[0]
        file_save_path = f"{core_settings.excel_ouput_file}/{fname}.xlsx"
        if len(self.page_dict)>0:
            writer = pd.ExcelWriter(file_save_path, engine='xlsxwriter')
            for k,v in self.page_dict.items():
                if len(self.page_dict[k])>0:
                    for p,q in self.page_dict[k].items():
                        df1 = q
                        df1.to_excel(writer, sheet_name=f"page{k}_table{p}",index=False)
            writer.save()