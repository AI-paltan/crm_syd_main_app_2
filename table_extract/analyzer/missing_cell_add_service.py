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

__all__ = ["MissingCellAddService"]

doctr_word_detection = detection_predictor(pretrained=True)

def get_doctr_predictions(img):
    #doctr_word_detection = detection_predictor(pretrained=True)
    raw_output = doctr_word_detection([img])
    return raw_output[0]

def get_nonoverlapped_items(doctr_output,cell_ann,threshold):
    iou_matrix = iou(doctr_output, cell_ann)
    remove_indices= np.where((iou_matrix > threshold) & (iou_matrix != 1))[0]
    remaining_doctr = doctr_output[~np.isin(np.arange(len(doctr_output)), remove_indices)]
    return remaining_doctr


def retreive_relative_coordinates(ann_dict):
    ulx = list(ann_dict['image']['embeddings'].values())[-2]['ulx']
    uly = list(ann_dict['image']['embeddings'].values())[-2]['uly']
    lrx = list(ann_dict['image']['embeddings'].values())[-2]['lrx']
    lry = list(ann_dict['image']['embeddings'].values())[-2]['lry']
    return ulx,uly,lrx,lry



@pipeline_component_registry.register("MissingCellAddService")
class MissingCellAddService(PipelineComponent):
    def __init__(
        self,
        #threshold_iou: float,
    ):
        self.threshold_iou = 0.01,
        self._table_name = LayoutType.table
        self._cell_names = [CellType.header, CellType.body, LayoutType.cell]
        self._item_names = [LayoutType.row, LayoutType.column]  # row names must be before column name
        self._sub_item_names = [CellType.row_number, CellType.column_number]
        super().__init__("cell_add")
        
    def serve(self, dp: Image) -> None:
        table_anns = dp.get_annotation(category_names=self._table_name)
        for table in table_anns:
            if table.image is None:
                raise ValueError("table.image is None, but must be an image")
            #plt.imshow(table.image.image)
            #print(table.annotation_id)
            doctr_predictions = get_doctr_predictions(table.image.image)
            doctr_lits = []
            x= table.image.width
            y = table.image.height
            for i in range(len(doctr_predictions)):
                tmp_lst = []
                tmp_lst.append(doctr_predictions[i][0]*x)
                tmp_lst.append(doctr_predictions[i][1]*y)
                tmp_lst.append(doctr_predictions[i][2]*x)
                tmp_lst.append(doctr_predictions[i][3]*y)
                doctr_lits.append(tmp_lst)
            doctr_predictions_array = np.array(doctr_lits)
            cells_ann = dp.get_annotation(category_names="cell")
            cell_ann_lst = []
            for cell in cells_ann:
                ulx,uly,lrx,lry = retreive_relative_coordinates(cell.as_dict())
                cell_ann_lst.append([ulx,uly,lrx,lry])
            cell_ann_array = np.array(cell_ann_lst)
            #print("doctr_ann: ", doctr_predictions_array)
            #print("cells_ann: ", cell_ann_array)
            if len(doctr_lits) > 0:
                filtered_doctr_cell = get_nonoverlapped_items(doctr_predictions_array,cell_ann_array,0.05)
                detect_result_lst = []
                for filtered_result in filtered_doctr_cell:
                    detect_result_lst.append(
                            DetectionResult(
                                box=filtered_result,
                                class_id=1,
                                class_name=LayoutType.cell,
                                score=1.0,
                            )
                    )
                
                for detect_result in detect_result_lst:
                    self.dp_manager.set_image_annotation(detect_result, table.annotation_id)

            
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
                ("image_annotations", [LayoutType.cell]),
                ("sub_categories", {}),
                # implicit setup of relations by using set_image_annotation with explicit annotation_id
                ("relationships", {parent: {Relationships.child} for parent in self._table_name}),
                ("summaries", []),
            ]
        )