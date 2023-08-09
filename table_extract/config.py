from pydantic import BaseSettings
from dotenv import load_dotenv
from os import path
import os

class Settings(BaseSettings):
    database_hostname: str = "localhost"
    database_port: str = "5432"
    database_password: str = "admin"
    database_name: str="crm_syd_dev"
    database_username: str="jayesh"


class CoreSettings(BaseSettings):
    file_storage :str=os.path.join(path.dirname(__file__),'../','FILE_DB/FILES')
    page_storage: str= os.path.join(path.dirname(__file__),'../','FILE_DB/PAGES')
    table_storage: str= os.path.join(path.dirname(__file__),'../','FILE_DB/TABLES')
    excel_ouput_file:str = os.path.join(path.dirname(__file__),'../EXCEL_OUPUT')
    deepdoctection_config_file:str = os.path.join(path.dirname(__file__),'../assets/deepdoctection_configs/conf_dd_one_custom_4.yaml')
    # deepdoctection_config_file:str = os.path.join(path.dirname(__file__),'../assets/deepdoctection_configs/conf_dd_one_custom.yaml')

    # file_storage :str=os.path.join(path.dirname(__file__),'..','FILE_DB/FILES')
    # page_storage: str= os.path.join(path.dirname(__file__),'..','FILE_DB/PAGES')
    # ocr_backend:str='tesseract'
    # label_map : dict = {"0":"cbs","1":"cpl","2":"ccf","-1":"other"}
    # region_settings: dict = {"sydeny":{"seq":{"0":"cpl","1":"cbs","2":"ccf"},
    #                                     "diff": 3
    #                                     },
    #                         "india":{"seq":{"0":"cbs","1":"cpl","2":"ccf"},
    #                                     "diff": 3
    #                                     },
    #                         }



settings = Settings()
core_settings = CoreSettings()
