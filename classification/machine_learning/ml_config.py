from pydantic import BaseSettings
from dotenv import load_dotenv
import os
from os import path

class Settings(BaseSettings):
    prob_threshold = 0.75
    absolute_path :str=  path.dirname(__file__)
    relative_path_sydeny : str= "../../assets/classification_models/sydeny/multinomial_nb_3_classes_v2.sav"
    sydeny_model: str=os.path.join(absolute_path,relative_path_sydeny)

    class Config:
        case_sensitive = False
        # env_file = '.env'


class PredRefineSetting(BaseSettings):
    label_map : dict = {"0":"cbs","1":"cpl","2":"ccf"}
    sydeny_seq:dict = {"0":"cpl","1":"cbs","2":"ccf"}
    sydeny_page_diff_thresh : int = 3
    india_seq:dict = {"0":"cbs","1":"cpl","2":"ccf"}
    india_page_diff_thresh: int = 3


# load_dotenv()
ml_settings = Settings()
pred_refine_settings = PredRefineSetting()
