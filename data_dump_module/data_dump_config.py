from pydantic import BaseSettings
from dotenv import load_dotenv
from os import path
import os


class DataDumpCoreSettings(BaseSettings):
    cdm_template :str= os.path.join(path.dirname(__file__),'../assets/cdm_excel_template','')
    
datadump_core_settings = DataDumpCoreSettings()