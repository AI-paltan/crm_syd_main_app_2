from pydantic import BaseSettings
from dotenv import load_dotenv
from os import path
import os


class DataDumpCoreSettings(BaseSettings):
    cdm_template :str= os.path.join(path.dirname(__file__),'../assets/cdm_excel_template','CCIF_CDM_Input_Company name_date_Sydney_latest_template v3.0.xlsx')
    bs_breakdown_particular_colidx = 2
    pl_breakdown_particular_colidx = 2
    cdm_template_save_dir : str = os.path.join(path.dirname(__file__),"../CDM_Output")
    client_list : str = os.path.join(path.dirname(__file__),"../assets/client_list/Client_names_for_Sydney_Region.xlsx")
    
datadump_core_settings = DataDumpCoreSettings()