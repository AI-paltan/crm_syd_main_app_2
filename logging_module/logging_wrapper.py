import logging
from logging import FileHandler
import logging.config
import os
from .logging_service_conf import log_settings

def singleton(cls):
    instances = {}
    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


@singleton
class Logger():
    def __init__(self):
        logging.config.fileConfig(log_settings.log_config)
        self.logr = logging.getLogger('sLogger')

# @singleton
# class Logger():
#     def __init__(self):
#         # logging.config.fileConfig('logging.conf')
#         # self.logr = logging.getLogger('root')
#         print("hi logger init")
#         self.filename = None
#         self.logger = None
#         self.filpath = None
    
#     def set_logger_file(self,filename_uid):
#         self.filename = filename_uid
#         logdir = os.path.join(log_settings.log_storage,filename_uid)
#         self.filepath = os.path.join(logdir,self.filename)
#         try:
#             os.mkdir(logdir)
#         except:
#             pass
    
#     def set_logger(self,filename_uuid):
#         print("hi setting up logger")
#         self.set_logger_file(filename_uid=filename_uuid)
#         logger = logging.getLogger(self.filename)
#         logger.SetLevel(logging.DEBUG)
#         handler = FileHandler(self.filepath,mode = 'a')
#         formatter = logging.Formatter(fmt=f"[%(asctime)s]%(levelname)s %(message)s" , datefmt ="%Y-%m-%d %H:%M:%S%z")
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#         self.logger = logger
    
#     def get_logger(self):
#         return self.logger


def set_main_logger(filename_uid):
    filename = filename_uid
    logdir = os.path.join(log_settings.log_storage,filename_uid)
    filepath = os.path.join(logdir,f"{filename}.txt")
    try:
        os.mkdir(logdir)
    except:
        pass
    handler = FileHandler(filepath,mode = 'a')
    formatter = logging.Formatter(fmt=f"[%(asctime)s]%(levelname)s %(message)s" , datefmt ="%Y-%m-%d %H:%M:%S%z")
    handler.setFormatter(formatter)
    # logging.addHandler(handler)
    # logging.SetLevel(logging.DEBUG)
    logging.basicConfig(handlers=handler,level=logging.DEBUG)


