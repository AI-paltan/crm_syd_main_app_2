import pandas as pd
import numpy as np
import re



def append_main_page_line_item_with_notes_items():
    ### for fields like other current assets, other noncurrent assets, other liabilities etc.
    ###
    pass


def remove_main_page_line_items_if_no_notes_items(df):
    ### for fields like rent in P&L statements
   pass


def extract_positive_values_rows(df):
    df = df.reset_index(drop=True)
    other_col = ["line_item","Particulars","Notes"]
    # main_page_other_cols = []
    year_cols = [i for i in df.columns if i not in other_col]
    positive_indices = []
    negative_indices = []
    for idx,row in df.iterrows():
        positive_flag = False
        for year in year_cols:
            if row[year] >= 0:
                positive_flag = True
            else:
                positive_flag = False
        if positive_flag:
            positive_indices.append(idx)
        else:
            negative_indices.append(idx)
    positive_df =  df.iloc[positive_indices]
    negative_df =  df.iloc[negative_indices]
    positive_df = positive_df.reset_index(drop=True)
    negative_df = negative_df.reset_index(drop=True)
    return positive_df,negative_df



def interest_income_filter(temp_dict):
    ## check if note df
    ## if note df present extracts only positive value rows.
    ## if not extract only positive value rows from main pages
    std_hrzntl_note_df = temp_dict["notes_horizontal_table_df"]
    main_page_cropped_df = temp_dict["main_page_cropped_df"]
    positive_note_df = pd.DataFrame()
    postive_main_page_df = pd.DataFrame()
    if len(std_hrzntl_note_df) > 0:
        if isinstance(std_hrzntl_note_df,pd.DataFrame):
            positive_note_df,negative_df = extract_positive_values_rows(std_hrzntl_note_df)
        else:
            postive_main_page_df,negative_df = extract_positive_values_rows(main_page_cropped_df)
    else:
        postive_main_page_df,negative_df = extract_positive_values_rows(main_page_cropped_df)

    if len(positive_note_df) > 0 :
        temp_dict["notes_horizontal_table_df"] = positive_note_df
    
    if len(postive_main_page_df) > 0 : 
        temp_dict["main_page_cropped_df"] = postive_main_page_df

    return temp_dict

    

def interest_expense_filter(temp_dict):
    std_hrzntl_note_df = temp_dict["notes_horizontal_table_df"]
    main_page_cropped_df = temp_dict["main_page_cropped_df"]
    negaive_note_df = pd.DataFrame()
    negative_main_page_df = pd.DataFrame()
    if len(std_hrzntl_note_df) > 0:
        if isinstance(std_hrzntl_note_df,pd.DataFrame):
            positive_df,negaive_note_df = extract_positive_values_rows(std_hrzntl_note_df)
        else:
            postive_df,negative_main_page_df = extract_positive_values_rows(main_page_cropped_df)
    else:
        postive_df,negative_main_page_df = extract_positive_values_rows(main_page_cropped_df)

    if len(negaive_note_df) > 0 :
        temp_dict["notes_horizontal_table_df"] = negaive_note_df
    if len(negative_main_page_df) > 0 :
        temp_dict["main_page_cropped_df"] = negative_main_page_df

    return temp_dict






