from .analyzer.TableExtract import TableExtract
from ..database.database import get_db, get_db1
from ..database import db_models
from typing import List,Dict
from .config import core_settings
import cv2
import os


db = get_db1()


class TECore:
    def __init__(self) -> None:
        self.page_uuid : str
        self.file_uuid : str
        self.page_filename:str
        self.filename:str
        self.page_save_path : str
        self.result_page = ''
        self.table_dict : Dict = {}
        self.table_filename:str
        self.tableid : str
        self.obj_list_cell: List = []
        self.obj_list_rc:List=[]

    def process_pdf(self,pageid:str):
        self.__get_basic_info_pageFile(pageid)
        self.__analyze_pdf()
        self.__save_table_logs()
        self.__update_page_logs()

    @property
    def get_page(self):
        return self.result_page
    
    @property
    def get_table(self):
        return self.table_dict


    def __get_basic_info_pageFile(self,pageid):
        page_query = db.query(db_models.PageLogs).filter(db_models.PageLogs.pageid == pageid).order_by(db_models.PageLogs.time.desc()).first()
        file_query = db.query(db_models.FileLogs).filter(db_models.FileLogs.fileid == page_query.fileid).order_by(db_models.FileLogs.time.desc()).first()
        self.page_uuid = pageid
        self.page_save_path = page_query.page_path
        self.page_filename = page_query.page_filename
        self.filename = file_query.filename

    def __analyze_pdf(self):
        TE = TableExtract()
        self.table_dict,self.result_page = TE.process_page(self.page_save_path)

    def __update_page_logs(self):
        page_query = db.query(db_models.PageLogs).filter(db_models.PageLogs.pageid == self.page_uuid).order_by(db_models.PageLogs.time.desc()).first()
        # temp_dict = {}
        # temp_dict['width_TE'] = self.result_page.width
        # temp_dict['height_TE'] = self.result_page.height
        page_query.width_TE  = self.result_page.width
        page_query.height_TE = self.result_page.height
        # page_query.update(temp_dict, synchronize_session=False)
        db.commit()

    def __save_table_logs(self):
        tables = self.result_page.get_annotation(category_names='table')
        obj_list = []
        for idx,table in enumerate(tables):
            if table.score > 0 and table.image is not None:
                temp_dict :dict = {}
                temp_dict['pageid'] = self.page_uuid
                temp_dict['tableid'] = table.annotation_id
                self.tableid = table.annotation_id
                temp_dict['left'] = int(table.bbox[0])
                temp_dict['top'] = int(table.bbox[1])
                temp_dict['right'] = int(table.bbox[2])
                temp_dict['down'] = int(table.bbox[3])
                temp_dict['width'] = int(table.image.width)
                temp_dict['height'] = int(table.image.height)
                temp_dict['conf'] = table.score
                fname = f"{self.filename}_{self.page_filename}_table{idx}.png"
                self.table_filename = os.path.join(core_settings.table_storage,fname)
                _ = cv2.imwrite(self.table_filename,table.image.image)
                temp_dict['table_img_save_path'] = self.table_filename
                temp_dict['html_string'] = table.html
                data_obj= db_models.TableLogs(**temp_dict)
                obj_list.append(data_obj)
                self.__add_Cell_logs(table)
                self.__add_row_col_logs(table)
        if len(obj_list) > 0:
            db.add_all(obj_list)
            db.commit()
            self.__save_cell_rc_data()

    def retreive_relative_coordinates(self,element):
        ulx = int(list(element.image.embeddings.values())[1].ulx)
        uly = int(list(element.image.embeddings.values())[1].uly)
        lrx = int(list(element.image.embeddings.values())[1].lrx)
        lry = int(list(element.image.embeddings.values())[1].lry)
        return ulx,uly,lrx,lry

    def __add_Cell_logs(self,table):
        cells = table.image.get_annotation(category_names="cell")
        obj_list_cell = []
        for idx,cell in enumerate(cells):
            if cell.score > 0 and cell.image is not None:
                temp_dict:Dict = {}
                temp_dict['cellid'] = cell.annotation_id
                temp_dict['tableid'] = self.tableid
                temp_dict['left_img'] = int(cell.bbox[0])
                temp_dict['top_img'] = int(cell.bbox[1])
                temp_dict['right_img'] = int(cell.bbox[2])
                temp_dict['down_img'] = int(cell.bbox[3])
                temp_dict['width'] = int(cell.image.width)
                temp_dict['height'] = int(cell.image.height)
                ulx,uly,lrx,lry = self.retreive_relative_coordinates(cell)
                temp_dict['left_table'] = ulx
                temp_dict['top_table'] = uly
                temp_dict['right_table'] = lrx
                temp_dict['down_table'] = lry
                temp_dict['conf'] = cell.score
                temp_dict['row_number'] = int(cell.sub_categories.get("row_number").category_id)
                temp_dict['col_number'] = int(cell.sub_categories.get("column_number").category_id)
                temp_dict['row_span'] = int(cell.sub_categories.get("row_span").category_id)
                temp_dict['col_span'] = int(cell.sub_categories.get("column_span").category_id)
                data_obj= db_models.CellLogs(**temp_dict)
                self.obj_list_cell.append(data_obj)
        # db.add_all(obj_list_cell)
        # db.commit()

    def __add_row_col_logs(self,table):
        rows = table.image.get_annotation(category_names="row")
        columns = table.image.get_annotation(category_names="column")
        # obj_list_rc = []
        for idx,row in enumerate(rows):
            if row.score >0 and row.image is not None:
                temp_dict:Dict = {}
                temp_dict['row_col_id'] = row.annotation_id
                temp_dict['tableid'] = self.tableid
                temp_dict['type'] = 'row'
                temp_dict['left_img'] = int(row.bbox[0])
                temp_dict['top_img'] = int(row.bbox[1])
                temp_dict['right_img'] = int(row.bbox[2])
                temp_dict['down_img'] = int(row.bbox[3])
                temp_dict['width'] = int(row.image.width)
                temp_dict['height'] = int(row.image.height)
                ulx,uly,lrx,lry = self.retreive_relative_coordinates(row)
                temp_dict['left_table'] = ulx
                temp_dict['top_table'] = uly
                temp_dict['right_table'] = lrx
                temp_dict['down_table'] = lry
                temp_dict['conf'] = row.score
                temp_dict['row_col_num'] = int(row.sub_categories.get("row_number").category_id)
                data_obj= db_models.RowColLogs(**temp_dict)
                self.obj_list_rc.append(data_obj)
        for idx,column in enumerate(columns):
            if column.score > 0 and column.image is not None:
                temp_dict:Dict = {}
                temp_dict['row_col_id'] = column.annotation_id
                temp_dict['tableid'] = self.tableid
                temp_dict['type'] = 'column'
                temp_dict['left_img'] = int(column.bbox[0])
                temp_dict['top_img'] = int(column.bbox[1])
                temp_dict['right_img'] = int(column.bbox[2])
                temp_dict['down_img'] = int(column.bbox[3])
                temp_dict['width'] = int(column.image.width)
                temp_dict['height'] = int(column.image.height)
                ulx,uly,lrx,lry = self.retreive_relative_coordinates(column)
                temp_dict['left_table'] = ulx
                temp_dict['top_table'] = uly
                temp_dict['right_table'] = lrx
                temp_dict['down_table'] = lry
                temp_dict['conf'] = column.score
                temp_dict['row_col_num'] = int(column.sub_categories.get("column_number").category_id)
                data_obj= db_models.RowColLogs(**temp_dict)
                self.obj_list_rc.append(data_obj)
        # db.add_all(obj_list_rc)
        # db.commit()

    def __save_cell_rc_data(self):
        db.add_all(self.obj_list_cell)
        db.add_all(self.obj_list_rc)
        db.commit()