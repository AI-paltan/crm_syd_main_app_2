from pydantic import BaseSettings
from dotenv import load_dotenv
from os import path
import os


class LogSettings(BaseSettings):
    log_storage :str=os.path.join(path.dirname(__file__),'../LOGS')
    log_config :str = os.path.join(path.dirname(__file__),'logger_config.ini')

    
log_settings = LogSettings()