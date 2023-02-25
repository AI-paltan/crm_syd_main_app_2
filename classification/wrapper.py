import os
import uuid
import shutil
from .clf_config import core_settings,settings
from ..database import db_models
from ..database.database import get_db, get_db1

from .clf_core import ClfCoreFlow


db = get_db1()


def save_file(file):
    filename = os.path.basename(file)
    file_uuid = str(uuid.uuid4())
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
    return file_uuid


def process_file(file):
    clf_core = ClfCoreFlow()
    fileid = save_file(file=file)
    clf_core.process_pdf(fileid)
    return fileid