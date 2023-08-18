from dataclasses import dataclass
from typing import List, Literal, Optional, Sequence, Union

import numpy as np
from matplotlib import pyplot as plt
from deepdoctection.datapoint.annotation import ImageAnnotation
from deepdoctection.datapoint.box import BoundingBox, iou
from deepdoctection.datapoint.image import Image
from deepdoctection.mapper.maputils import MappingContextManager
from deepdoctection.mapper.match import match_anns_by_intersection
from deepdoctection.utils.detection_types import JsonDict
from deepdoctection.utils.settings import CellType, LayoutType, ObjectTypes, Relationships
from deepdoctection.pipe.base import PipelineComponent
from deepdoctection.pipe.registry import pipeline_component_registry
from doctr.models.detection.predictor import DetectionPredictor
from doctr.models.detection.zoo import detection_predictor
from deepdoctection.extern.base import DetectionResult, ObjectDetector, PdfMiner

__all__ = ["MissingColAddService"]


def get_nonoverlapped_items(doctr_output,cell_ann,threshold):
    iou_matrix = iou(doctr_output, cell_ann)
    remove_indices= np.where((iou_matrix > threshold) & (iou_matrix != 1))[0]
    remaining_doctr = doctr_output[~np.isin(np.arange(len(doctr_output)), remove_indices)]
    return remaining_doctr

def retreive_relative_coordinates(ann_dict):
    # print(ann_dict['image']['embeddings'])
    ulx = list(ann_dict['image']['embeddings'].values())[-1]['ulx']
    uly = list(ann_dict['image']['embeddings'].values())[-1]['uly']
    lrx = list(ann_dict['image']['embeddings'].values())[-1]['lrx']
    lry = list(ann_dict['image']['embeddings'].values())[-1]['lry']
    return ulx,uly,lrx,lry


@pipeline_component_registry.register("MissingColAddService")
class MissingColAddService(PipelineComponent):
    def __init__(
        self,
        #threshold_iou: float,
    ):
        self.threshold_iou = 0.01,
        self._table_name = LayoutType.table
        self._cell_names = [CellType.header, CellType.body, LayoutType.cell]
        self._item_names = [LayoutType.row, LayoutType.column]  # row names must be before column name
        self._sub_item_names = [CellType.row_number, CellType.column_number]
        super().__init__("col_add")


    def serve(self, dp: Image) -> None:
        table_anns = dp.get_annotation(category_names=self._table_name)
        for table in table_anns:
            if table.image is None:
                raise ValueError("table.image is None, but must be an image")
    
            cells_ann = dp.get_annotation(category_names="cell")
            cell_ann_lst = []
            for cell in cells_ann:
                ulx,uly,lrx,lry = retreive_relative_coordinates(cell.as_dict())
                cell_ann_lst.append([ulx,uly,lrx,lry])
            cell_ann_array = np.array(cell_ann_lst)

            cols_ann = dp.get_annotation(category_names="column")
            # print(cols_ann)
            col_ann_lst = []
            for row in cols_ann:
                ulx,uly,lrx,lry = retreive_relative_coordinates(row.as_dict())
                col_ann_lst.append([ulx,uly,lrx,lry])
            col_ann_array = np.array(col_ann_lst)

            # print(col_ann_array)
            col_left_cords_x =  10000
            col_down_cords_y = 0
            for cols_ann in col_ann_array:
                if cols_ann[0] < col_left_cords_x:
                    col_left_cords_x = cols_ann[0]
                    col_down_cords_y = cols_ann[3]
                    # print(f"col_left_cords_x = {col_left_cords_x}")

            detect_result_lst = []
            table_lef_cords_x = table.bounding_box.ulx
            table_right_cord_x = table.bounding_box.lrx
            table_width  = abs(table_right_cord_x-table_lef_cords_x)
            first_col_distance_from_left_side_of_table = abs(col_left_cords_x-table_lef_cords_x)
            # print(f"table_lef_cords_x = {table_lef_cords_x}")
            # print(f"table_right_cord_x = {table_right_cord_x}")
            # print(f"table_width = {table_width}")
            # print(f"first_col_distance_from_left_side_of_table = {first_col_distance_from_left_side_of_table}")
            if first_col_distance_from_left_side_of_table > table_width *0.2:
                # bbox = [table.bounding_box.ulx+2.0,table.bounding_box.uly,col_left_cords_x-1.0,col_down_cords_y]
                bbox = [0,0,abs(col_left_cords_x-table.bounding_box.ulx),abs(col_down_cords_y-table.bounding_box.uly)]
                detect_result_lst.append(
                        DetectionResult(
                            box=bbox,
                            class_id=2,
                            class_name=LayoutType.column,
                            score=1.0,
                            absolute_coords=True
                        )
                    )
            
            # print(f"detect_result_lst={detect_result_lst}")
            for detect_result in detect_result_lst:
                    self.dp_manager.set_image_annotation(detect_result, table.annotation_id)


            # filtered_cell = get_nonoverlapped_items(cell_ann_array,row_ann_array,0.005)
            # row_add_bbox = []
            # for filtered_result in filtered_cell:
            #     bbox = [table.bounding_box.ulx,filtered_result[1],table.bounding_box.lrx,filtered_result[3]]
            #     row_add_bbox.append(bbox)   
            # row_add_bbox_array = np.array(row_add_bbox)
            # if len(row_add_bbox) > 0:
            #     filtered_add_row = get_nonoverlapped_items(row_add_bbox_array,row_ann_array,0.05)
            #     # print("filtered cells:",filtered_cell)
            #     # print("row_ann_array:",row_ann_array)
            #     if len(filtered_add_row)>0:
            #         detect_result_lst = []
            #         for filtered_result1 in filtered_add_row:
            #             # bbox = [table.bounding_box.ulx,filtered_result[1],table.bounding_box.lrx,filtered_result[3]]
            #             bbox = [0,abs(filtered_result1[1]-table.bounding_box.uly),abs(table.bounding_box.lrx-table.bounding_box.ulx),abs(filtered_result1[3]-table.bounding_box.uly)]
            #             detect_result_lst.append(
            #                     DetectionResult(
            #                         box=bbox,
            #                         class_id=1,
            #                         class_name=LayoutType.row,
            #                         score=1.0,
            #                     )
            #             )
                
            #         for detect_result in detect_result_lst:
            #             self.dp_manager.set_image_annotation(detect_result, table.annotation_id)

    def clone(self) -> PipelineComponent:
        return self.__class__(
            self.threshold_iou,
            self._table_name,
            self._cell_names,
            self._item_names,
            self._sub_item_names,
        )

    def get_meta_annotation(self) -> JsonDict:
        #assert isinstance(self.predictor, (ObjectDetector, PdfMiner))
        return dict(
            [
                ("image_annotations", [LayoutType.column]),
                ("sub_categories", {}),
                # implicit setup of relations by using set_image_annotation with explicit annotation_id
                ("relationships", {parent: {Relationships.child} for parent in self._table_name}),
                ("summaries", []),
            ]
        )
