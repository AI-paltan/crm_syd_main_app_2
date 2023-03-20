from .standard_OCR.OCR import OCR
from .machine_learning.data_prediction import DataPrediction
from .machine_learning.data_preprocessing import dataPreprocessing
from .machine_learning.prediction_refinement import PredictionRefinement
from .clf_config import core_settings,settings
from PyPDF2 import PdfFileWriter, PdfFileReader
import shutil
import uuid
import os
from ..database.database import get_db, get_db1
from ..database import db_models
from typing import List,Dict
import logging
from ..logging_module.logging_wrapper import Logger

db = get_db1()
ocr = OCR(core_settings.ocr_backend)



class ClfCoreFlow():
    def __init__(self) -> None:
        self.region: str="sydeny"
        self.file_save_path:str
        self.file_uuid : str
        self.filename :str
        self.page_cnt : int
        self.page_uuid:str
        self.page_save_path:str
        self.page_fname:str
        self.page_width:int
        self.page_height:int
        self.input_pdf = ''
        self.predicted_cbs_pages : List(int) = []
        self.predicted_cpl_pages : List(int) = []
        self.predicted_ccf_pages : List(int)=[]
        self.filtered_cbs_pages : List(int)=[]
        self.filtered_cpl_pages : List(int)=[]
        self.filtered_ccf_pages : List(int)=[]
        self.raw_text:str
        self.ocr_df = ''
        self.page_type_id:int
        self.page_type_class:int
     


    def process_pdf(self,file_id:str):
        Logger.logr.debug("module: Classification_service , File:clf_core.py,  function: process_pdf")
        self.__get_basic_info_file(file_id)
        self.__save_basic_info_file_db()
        for i in range(self.page_cnt):
            self.__process_page(i)
            self.__save_page_log_db(i)
            self.__save_ocr_dump()
            self.__save_text()
        self.__filtered_pages()
        self.__update_filtered_pages_db()
        Logger.logr.debug("function: process_pdf completed successfully")
    def process_single_page(self):
        pass

    def __filtered_pages(self):
        predict_refine = PredictionRefinement()
        reg_seq = core_settings.region_settings[self.region]["seq"]
        reg_diff = core_settings.region_settings[self.region]["diff"]
        sequence_dict : Dict = {"cbs":self.predicted_cbs_pages,
                                    "cpl":self.predicted_cpl_pages,
                                    "ccf":self.predicted_ccf_pages
                                    }
        first_seq = sequence_dict.get(reg_seq.get("0"))
        second_seq = sequence_dict.get(reg_seq.get("1"))
        third_seq = sequence_dict.get(reg_seq.get("2"))
        three_seq,two_first_second_seq,two_second_third_seq,two_first_third_seq = predict_refine.filter_sequences(first_seq,second_seq,third_seq,reg_diff)
        final_seq:List = []
        if len(three_seq)>0:
            if len(three_seq)>1:
                final_seq = three_seq[-1]
            else:
                final_seq = three_seq[0]
        elif len(two_first_second_seq)>0:
            if len(two_first_second_seq)>1:
                final_seq = two_first_second_seq[-1]
            else:
                final_seq = two_first_second_seq[-1]
        elif len(two_second_third_seq)>0:
            if len(two_second_third_seq)>1:
                final_seq = two_second_third_seq[-1]
            else:
                final_seq = two_second_third_seq[-1]
        elif len(two_first_third_seq)>0:
            if len(two_first_third_seq)>1:
                final_seq = two_first_third_seq[-1]
            else:
                final_seq = two_first_third_seq[-1]    
        self.filtered_cbs_pages = list(set(final_seq).intersection(set(self.predicted_cbs_pages)))
        self.filtered_cpl_pages = list(set(final_seq).intersection(set(self.predicted_cpl_pages)))
        self.filtered_ccf_pages = list(set(final_seq).intersection(set(self.predicted_ccf_pages)))
        ## solving issue of cbs appearing first in sequence
        if (len(self.filtered_cbs_pages) == 0) & (len(self.filtered_cpl_pages)>0):
            self.temp_cbs_lst = [i for i in self.predicted_cbs_pages if (i < self.filtered_cpl_pages[0])&(i>=self.filtered_cpl_pages[0]-3)]
            self.filtered_cbs_pages = list(self.temp_cbs_lst)


    def __update_filtered_pages_db(self):
        Logger.logr.debug("module: Classification_service , File:clf_core.py,  function: __update_filtered_pages_db")
        file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == self.file_uuid)
        temp_dict = {}
        temp_dict['predicted_cbs_pages'] = self.predicted_cbs_pages
        temp_dict['predicted_cpl_pages'] = self.predicted_cpl_pages
        temp_dict['predicted_ccf_pages'] = self.predicted_ccf_pages
        temp_dict['filtered_cbs_pages'] = self.filtered_cbs_pages
        temp_dict['filtered_cpl_pages'] = self.filtered_cpl_pages
        temp_dict['filtered_ccf_pages'] = self.filtered_ccf_pages
        file_query.update(temp_dict, synchronize_session=False)
        Logger.logr.debug(temp_dict)
        Logger.logr.debug("function: __update_filtered_pages_db completed")
        db.commit()

    def __get_basic_info_file(self,file_id:str):
        Logger.logr.debug("module: Classification_service , File:clf_core.py,  function: __get_basic_info_file")
        file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == file_id).first()
        self.file_uuid = file_id
        self.filename = file_query.filename
        self.file_save_path = file_query.filepath
        self.input_pdf = PdfFileReader(open(self.file_save_path, "rb"),strict=False)
        self.page_cnt = self.input_pdf.numPages
        Logger.logr.debug("__get_basic_info_file() completed.")
        # self.filename = os.path.basename(file)
        # self.file_uuid = str(uuid.uuid4())
        # self.file_save_path = f'{core_settings.file_storage}/{self.filename}'
        # shutil.copy(file,self.file_save_path)
        # self.input_pdf = PdfFileReader(open(self.file_save_path, "rb"),strict=False)
        # self.page_cnt = self.input_pdf.numPages

    def __save_basic_info_file_db(self):
        Logger.logr.debug("module: Classification_service , File:clf_core.py,  function: __save_basic_info_file_db")
        file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == self.file_uuid)
        temp_dict = {}
        # temp_dict['fileid'] = self.file_uuid
        # temp_dict['filename'] = self.filename
        # temp_dict['filepath'] = self.file_save_path
        temp_dict['page_count'] = self.page_cnt
        temp_dict['region'] = self.region
        file_query.update(temp_dict, synchronize_session=False)
        Logger.logr.debug("__save_basic_info_file_db() completed. and file data (page_cnt,region) updated in db")
        db.commit()
        # new_file = db_models.FileLogs(**temp_dict)
        # db.add(new_file)
        # db.commit()
        # db.refresh(new_file)

    def __process_page(self,page_idx):
        dataPreProcess = dataPreprocessing()
        dataPredict = DataPrediction()
        self.page_uuid = str(uuid.uuid4())
        output = PdfFileWriter()
        output.addPage(self.input_pdf.getPage(page_idx))
        self.page_save_path = f'{core_settings.page_storage}/{self.filename}_document-page-{page_idx}.pdf'
        self.page_fname = f'{self.filename}_document-page-{page_idx}.pdf'
        with open(self.page_save_path, "wb") as outputStream:
            output.write(outputStream)
        data,dimensions = ocr.get_data(self.page_save_path)
        text = ocr.get_processed_text()
        for k,v in data.items():
            self.ocr_df = v
        for k,v in dimensions.items():
            self.page_width = v['width']
            self.page_height= v['height']
        for k,v in text.items():
            self.raw_text = v
        corpus = dataPreProcess.data_preprocessing(self.raw_text)
        y_pred = dataPredict.predict(corpus)
        self.page_type_id = y_pred
        y_class = core_settings.label_map[str(y_pred)]
        self.page_type_class=y_class
        if y_class == "cbs":
            self.predicted_cbs_pages.append(page_idx)
        if y_class=="cpl":
            self.predicted_cpl_pages.append(page_idx)
        if y_class=="ccf":
            self.predicted_ccf_pages.append(page_idx)


        

    def __save_page_log_db(self,page_idx):
        temp_dict={}
        temp_dict['fileid'] = self.file_uuid
        temp_dict['pageid'] = self.page_uuid
        temp_dict['page_number'] = page_idx
        temp_dict['page_path'] = self.page_save_path
        temp_dict['page_filename'] = self.page_fname
        temp_dict['width']=self.page_width
        temp_dict['height'] = self.page_height
        temp_dict['predicted_type_id'] = self.page_type_id
        temp_dict['predicted_type_name'] = self.page_type_class
        new_page = db_models.PageLogs(**temp_dict)
        db.add(new_page)
        db.commit()
        db.refresh(new_page)

    def __save_ocr_dump(self):
        data = self.ocr_df
        data['pageid'] = self.page_uuid
        listToWrite = data.to_dict(orient='records')
        # new_ocr_dump = db_models.OCRDump(**listToWrite)
        obj_list = []
        for record in listToWrite:
            data_obj= db_models.OCRDump(**record)
            obj_list.append(data_obj)
        db.add_all(obj_list)
        db.commit()
        # db.refresh(new_ocr_dump)

    def __save_text(self):
        temp_dict = {}
        temp_dict['pageid'] = self.page_uuid
        temp_dict['raw_text'] = self.raw_text
        new_text = db_models.OCRText(**temp_dict)
        db.add(new_text)
        db.commit()



