import pandas as pd
import numpy as np
import re


def second_filter_PPE(std_hrzntl_note_df,month):
    ## this function will filter PPE note further for month of given annual statemnt
    month_indices = []
    for idx,row in std_hrzntl_note_df.iterrows():
        if month in row["line_item"].lower():
            month_indices.append(idx)
    # print(month_indices)
    if len(month_indices)>0:
        std_hrzntl_note_df = std_hrzntl_note_df.iloc[month_indices]
    std_hrzntl_note_df.reset_index(drop=True,inplace=False)
    return std_hrzntl_note_df

def gross_PPE_filter(std_hrzntl_note_df):
    keywords = ['cost','gross']
    indices = []
    for idx,row in std_hrzntl_note_df.iterrows():
        for kwrd in keywords:
            if kwrd in row["line_item"].lower():
                indices.append(idx)
    
    if len(indices)>0:
        std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
    std_hrzntl_note_df.reset_index(drop=True,inplace=False)
    return std_hrzntl_note_df


def accumulation_PPE_filter(std_hrzntl_note_df):
    keywords = ['depreciatio','accumulated depreciation']
    indices = []
    for idx,row in std_hrzntl_note_df.iterrows():
        for kwrd in keywords:
            if kwrd in row["line_item"].lower():
                indices.append(idx)
    
    if len(indices)>0:
        std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
    std_hrzntl_note_df.reset_index(drop=True,inplace=False)
    return std_hrzntl_note_df


