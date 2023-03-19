import pickle
import numpy as np
import pandas as pd
from .ml_config import ml_settings
from ...logging_module.logging_wrapper import Logger

model = pickle.load(open(ml_settings.sydeny_model, 'rb'))

class DataPrediction:
    def __init__(self) -> None:
        self.y_pred = -1

    def predict(self,data):
        Logger.logr.debug("module: Classification_service , submodule: machine_learning, File:data_prediction.py,  function: predict")
        y_pred_proba = model.predict_proba([data])
        argmax = np.argmax(y_pred_proba)
        self.y_pred = -1
        if y_pred_proba[0][argmax] > ml_settings.prob_threshold:
            self.y_pred = argmax
        Logger.logr.debug("function: predict completed.")
        return int(self.y_pred)
