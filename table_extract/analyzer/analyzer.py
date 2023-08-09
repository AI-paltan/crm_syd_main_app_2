from os import getcwd, path, environ
import deepdoctection as dd
from deepdoctection.dataflow.serialize import DataFromList
from matplotlib import pyplot as plt
import pandas as pd
import os
import re
import glob
import shutil
import pandas as pd
import numpy as np
from PyPDF2 import PdfFileWriter, PdfFileReader
from IPython.core.display import HTML
from matplotlib import pyplot as plt
from copy import deepcopy
from PIL import Image, ImageDraw
from doctr.models.detection.predictor import DetectionPredictor
from doctr.models.detection.zoo import detection_predictor
from .missing_cell_add_service import MissingCellAddService
from .segment_custom import TableSegmentationService
from ..config import core_settings
from .missing_row_add_service import MissingRowAddService


# config_path = os.path.join(path.dirname(__file__),'deepdoctection_configs/conf_dd_one_custom.yaml')
config_path = core_settings.deepdoctection_config_file
cfg = dd.set_config_by_yaml(config_path)
cfg.freeze(freezed=False)
cfg.DEVICE = "cuda"
cfg.freeze()

# try:
#     dd.ModelCatalog.register("layout/table_detection_iter150000_data70k.pth",dd.ModelProfile(
#                 name="layout/table_detection_iter150000_data70k.pth",
#                 description="Detectron2 layout detection model trained on private datasets",
#                 config="dd/d2/layout/CASCADE_RCNN_R_50_FPN_GN_custom_2.yaml",
#                 size=[274632215],
#                 tp_model=False,
#                 hf_repo_id=environ.get("HF_REPO"),
#                 hf_model_name="table_detection_iter150000_data70k.pth",
#                 hf_config_file=["Base-RCNN-FPN.yaml", "CASCADE_RCNN_R_50_FPN_GN_custom_2.yaml"],
#                 categories={"1": dd.LayoutType.table},
#             ))
# except:
#     pass

try:
    dd.ModelCatalog.register("layout/table_detection_iter170000_custom_data5000.pth",dd.ModelProfile(
                name="layout/table_detection_iter170000_custom_data5000.pth",
                description="Detectron2 layout detection model trained on private datasets",
                config="dd/d2/layout/CASCADE_RCNN_R_50_FPN_GN_custom_2.yaml",
                size=[274632215],
                tp_model=False,
                hf_repo_id=environ.get("HF_REPO"),
                hf_model_name="table_detection_iter170000_custom_data5000.pth",
                hf_config_file=["Base-RCNN-FPN.yaml", "CASCADE_RCNN_R_50_FPN_GN_custom_2.yaml"],
                categories={"1": dd.LayoutType.table},
            ))
except:
    pass



layout_config_path = dd.ModelCatalog.get_full_path_configs(cfg.CONFIG.D2LAYOUT)
layout_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.D2LAYOUT)
# categories_layout = dd.ModelCatalog.get_profile(cfg.WEIGHTS.D2LAYOUTPROFILE).categories
categories_layout = dd.ModelCatalog.get_profile(cfg.WEIGHTS.D2LAYOUT).categories
categories_layout = {"1": dd.LayoutType.table}
assert categories_layout is not None
assert layout_weights_path is not None
d_layout = dd.D2FrcnnDetector(layout_config_path, layout_weights_path, categories_layout, device=cfg.DEVICE)

# cell detector
cell_config_path = dd.ModelCatalog.get_full_path_configs(cfg.CONFIG.D2CELL)
cell_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.D2CELL)
categories_cell = dd.ModelCatalog.get_profile(cfg.WEIGHTS.D2CELLPROFILE).categories
assert categories_cell is not None
d_cell = dd.D2FrcnnDetector(cell_config_path, cell_weights_path, categories_cell, device=cfg.DEVICE)

# row/column detector
item_config_path = dd.ModelCatalog.get_full_path_configs(cfg.CONFIG.D2ITEM)
item_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(cfg.WEIGHTS.D2ITEM)
categories_item = dd.ModelCatalog.get_profile(cfg.WEIGHTS.D2ITEMPROFILE).categories
assert categories_item is not None
d_item = dd.D2FrcnnDetector(item_config_path, item_weights_path, categories_item, device=cfg.DEVICE)

# word detector
det = dd.DoctrTextlineDetector()

# text recognizer
rec = dd.DoctrTextRecognizer()

def build_analyzer():
    pipe_component_list = []
    layout = dd.ImageLayoutService(d_layout, to_image=True, crop_image=True)
    pipe_component_list.append(layout)
    cell = dd.SubImageLayoutService(d_cell, dd.LayoutType.table, {1: 6}, True)
    pipe_component_list.append(cell)
    item = dd.SubImageLayoutService(d_item, dd.LayoutType.table, {1: 7, 2: 8}, True)
    pipe_component_list.append(item)
    
    missing_cell_add = MissingCellAddService()
    pipe_component_list.append(missing_cell_add)
    missing_row_add = MissingRowAddService()
    pipe_component_list.append(missing_row_add)
    table_segmentation = TableSegmentationService(
            cfg.SEGMENTATION.ASSIGNMENT_RULE,
            cfg.SEGMENTATION.IOU_THRESHOLD_ROWS
            if cfg.SEGMENTATION.ASSIGNMENT_RULE in ["iou"]
            else cfg.SEGMENTATION.IOA_THRESHOLD_ROWS,
            cfg.SEGMENTATION.IOU_THRESHOLD_COLS
            if cfg.SEGMENTATION.ASSIGNMENT_RULE in ["iou"]
            else cfg.SEGMENTATION.IOA_THRESHOLD_COLS,
            cfg.SEGMENTATION.FULL_TABLE_TILING,
            cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS,
            cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS,
        )
    pipe_component_list.append(table_segmentation)
    
    table_segmentation_refinement = dd.TableSegmentationRefinementService()
    pipe_component_list.append(table_segmentation_refinement)
    
    d_layout_text = dd.ImageLayoutService(det, to_image=True, crop_image=True)
    pipe_component_list.append(d_layout_text)

    d_text = dd.TextExtractionService(rec, extract_from_roi="WORD")
    pipe_component_list.append(d_text)
    
    match = dd.MatchingService(
            parent_categories=cfg.WORD_MATCHING.PARENTAL_CATEGORIES,
            child_categories=dd.LayoutType.word,
            matching_rule=cfg.WORD_MATCHING.RULE,
            threshold=cfg.WORD_MATCHING.IOU_THRESHOLD
            if cfg.WORD_MATCHING.RULE in ["iou"]
            else cfg.WORD_MATCHING.IOA_THRESHOLD,
        )
    pipe_component_list.append(match)
    
    order = dd.TextOrderService(
            text_containers_to_text_block=True,
            text_container=dd.LayoutType.word,
            floating_text_block_names=[dd.LayoutType.title, dd.LayoutType.text, dd.LayoutType.list ],
            text_block_names=[
                dd.LayoutType.title,
                dd.LayoutType.text,
                dd.LayoutType.list,
                dd.LayoutType.cell,
                dd.CellType.header,
                dd.CellType.body,
            ]            
        )
    pipe_component_list.append(order)
    pipe = dd.DoctectionPipe(pipeline_component_list=pipe_component_list)

    return pipe

  