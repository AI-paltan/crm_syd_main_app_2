import openpyxl
import pandas as pd
import numpy as np
from ..database.database import get_db1
from ..database import db_models
from .data_dump_config import datadump_core_settings

db =get_db1()


class DataDump:
    def __init__(self) -> None:
        self.years_list = None
        self.cbs_resposne_bucket = None
        self.cpl_response_bucket = None
        self.ccf_response_bucket = None
        self.workbook = None

    def trigger_job(self):
        pass

    def get_row_map_from_db(self,meta_keyword):
        meta_query = db.query(db_models.CRM_nlp_bucketing).filter(db_models.CRM_nlp_bucketing.meta_keyword == meta_keyword).first()
        cdm_sheet_name = meta_query.cdm_sheet_name
        cdm_keyword_start_row_map = meta_query.cdm_keyword_start_row_map
        cdm_total_row_map = meta_query.cdm_total_row_map
        return cdm_sheet_name,cdm_keyword_start_row_map,cdm_total_row_map
    
    def load_workbook(self):
        self.workbook = openpyxl.load_workbook(datadump_core_settings.cdm_template)

    def set_year_to_excel(self):
        pass

    def dump_balance_sheet_data(self):
        for page_num,value_dict in self.cbs_resposne_bucket.items():
            for meta_key,meta_dict in value_dict.items():
                notes_table_df = meta_dict['notes_table_df']
                if len(notes_table_df)>0:
                    cdm_sheet_name,cdm_keyword_start_row_map,cdm_total_row_map = self.get_row_map_from_db(meta_keyword=meta_key)


    def dump_cpl_data(self):
        pass

    def dump_ccf_data(self):
        pass

    def insert_df(cdm_sheet_name,cdm_keyword_start_name,cdm_total_row_map,notes_table_df):
        pass