from pydantic import BaseSettings
from dotenv import load_dotenv
from os import path
import os


class DataDumpCoreSettings(BaseSettings):
    cdm_template :str= os.path.join(path.dirname(__file__),'../assets/cdm_excel_template','CDM_new_template.xlsx')
    bs_breakdown_particular_colidx = 2
    pl_breakdown_particular_colidx = 2
    cdm_template_save_dir : str = os.path.join(path.dirname(__file__),"../CDM_Output")
    
datadump_core_settings = DataDumpCoreSettings()