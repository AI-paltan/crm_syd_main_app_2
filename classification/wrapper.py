import os
import uuid
import shutil
from .clf_config import core_settings,settings
from ..database import db_models
from ..database.database import get_db, get_db1

from .clf_core import ClfCoreFlow
import logging
# from ..logging_module.logging_wrapper import set_main_logger,Logger
import configparser

db = get_db1()


def save_file(file):
    filename = os.path.basename(file)
    file_uuid = str(uuid.uuid4())
    # set_main_logger(filename_uid=file_uuid)
    set_log_file_path(file_uid=file_uuid)
    from ..logging_module.logging_wrapper import Logger
    Logger.logr.debug("module: Classification_service , File:wrapper.py,  function: Save_file")
    file_save_path = f'{core_settings.file_storage}/{filename}'
    shutil.copy(file,file_save_path)
    temp_dict = {}
    temp_dict['fileid'] = file_uuid
    temp_dict['filename'] = filename
    temp_dict['filepath'] = file_save_path
    new_file = db_models.FileLogs(**temp_dict)
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    Logger.logr.debug(temp_dict)
    Logger.logr.debug("save file completed")
    return file_uuid


def process_file(file):
    # log_obj = Logger()
    # from ..logging_module.logging_wrapper import Logger
    # Logger.logr.debug("module: Classification_service , File:wrapper.py,  function: process_file")
    clf_core = ClfCoreFlow()
    fileid = save_file(file=file)
    from ..logging_module.logging_wrapper import Logger
    clf_core.process_pdf(fileid)
    Logger.logr.debug("process file completed")
    return fileid

def set_log_file_path(file_uid):
    # print(core_settings.log_config)
    filename = file_uid
    logdir = os.path.join(core_settings.log_storage,file_uid)
    filename_full = f"{filename}.txt"
    try:
        os.mkdir(logdir)
    except:
        pass
    config = configparser.RawConfigParser()
    config.read(core_settings.log_config)
    config.set("handler_fileHandler","args",f"('{os.path.join(logdir,filename_full)}', 'a')")                         
    cfgfile = open(core_settings.log_config,'w')
    config.write(cfgfile, space_around_delimiters=False)  # use flag in case case you need to avoid white space.
    cfgfile.close()