import pandas as pd
from typing import List
from .ml_config import pred_refine_settings
from .utils import *


class PredictionRefinement:
    def __init__(self) -> None:
        self.first_seq : List[int] = []
        self.second_seq:List[int] = []
        self.third_seq:List[int] = []
        self.page_diff:int = pred_refine_settings.sydeny_page_diff_thresh
        self.three_seq:List[List[int]] 
        self.two_first_second_seq:List[List[int]]
        self.two_first_third_seq:List[List[int]]
        self.two_second_third_seq:List[List[int]]
        self.first_seq_first_page: int

    def filter_sequences(self,first_seq,second_seq,third_seq,diff_threshold):
        self.first_seq = first_seq
        self.second_seq = second_seq
        self.third_seq =third_seq
        self.first_seq.sort()
        self.second_seq.sort()
        self.third_seq.sort()
        self.first_seq_first_page = find_first_page(self.first_seq)
        #print(first_seq_first_page)
        self.second_seq = [i for i in self.second_seq if i > self.first_seq_first_page]
        self.third_seq = [i for i in self.third_seq if i>self.first_seq_first_page]
        #print(first_seq,second_seq,third_seq)
        self.three_seq,self.two_first_second_seq,self.two_second_third_seq,self.two_first_third_seq = find_seq(self.first_seq,self.second_seq,self.third_seq,diff_threshold)
        return self.three_seq,self.two_first_second_seq,self.two_second_third_seq,self.two_first_third_seq




        