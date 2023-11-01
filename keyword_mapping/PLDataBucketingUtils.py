import pandas as pd
import numpy as np
import re
from .DataBucketingUtils import *



def append_main_page_line_item_with_notes_items():
    ### for fields like other current assets, other noncurrent assets, other liabilities etc.
    ###
    pass


def remove_main_page_line_items_if_no_notes_items(df):
    ### for fields like rent in P&L statements
   pass


def extract_positive_values_rows(df):
    df = df.reset_index(drop=True)
    other_col = ["line_item","Particulars","Notes","Note"]
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



# def interest_income_filter_old(temp_dict):
#     ## check if note df
#     ## if note df present extracts only positive value rows.
#     ## if not extract only positive value rows from main pages
#     std_hrzntl_note_df = temp_dict["notes_horizontal_table_df"]
#     main_page_cropped_df = temp_dict["main_page_cropped_df"]
#     positive_note_df = pd.DataFrame()
#     postive_main_page_df = pd.DataFrame()
#     if len(std_hrzntl_note_df) > 0:
#         if isinstance(std_hrzntl_note_df,pd.DataFrame):
#             positive_note_df,negative_df = extract_positive_values_rows(std_hrzntl_note_df)
#         else:
#             postive_main_page_df,negative_df = extract_positive_values_rows(main_page_cropped_df)
#     else:
#         postive_main_page_df,negative_df = extract_positive_values_rows(main_page_cropped_df)

#     if len(positive_note_df) > 0 :
#         temp_dict["notes_horizontal_table_df"] = positive_note_df
    
#     if len(postive_main_page_df) > 0 : 
#         temp_dict["main_page_cropped_df"] = postive_main_page_df

#     return temp_dict


def interest_expense_filter(temp_dict):
    not_found_main_page_particular = temp_dict["main_page_notes_notfound_main_page_particular"]
    check_str = "finance cost"
    temp = '\t'.join(not_found_main_page_particular)
    res = check_str in temp.lower()
    std_hrzntl_note_df = temp_dict['notes_horizontal_table_df']
    if res:
        if isinstance(std_hrzntl_note_df,pd.DataFrame):
            std_hrzntl_note_df.reset_index(drop=True,inplace=True)
            keywords = ['cost','expense']
            indices = []
            std_hrzntl_note_df = std_hrzntl_note_df.reset_index(drop=True)
            for idx,row in std_hrzntl_note_df.iterrows():
                for kwrd in keywords:
                    if kwrd in row["line_item"].lower():
                        indices.append(idx)
        
        if len(indices)>0:
            std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)

    temp_dict['notes_horizontal_table_df'] = temp_dict['notes_horizontal_table_df']

    return temp_dict
    
def exclude_net_keyword_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keywords = ['Net','net']
        indices = []
        std_hrzntl_note_df = std_hrzntl_note_df.reset_index(drop=True)
        for idx,row in std_hrzntl_note_df.iterrows():
            for kwrd in keywords:
                if kwrd in row["line_item"].lower():
                    indices.append(idx)
        
        if len(indices)>0:
            # std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
            std_hrzntl_note_df = std_hrzntl_note_df.iloc[~std_hrzntl_note_df.index.isin(indices)] 
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
    return std_hrzntl_note_df

def net_keyword_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keywords = ['Net','net']
        indices = []
        std_hrzntl_note_df = std_hrzntl_note_df.reset_index(drop=True)
        for idx,row in std_hrzntl_note_df.iterrows():
            for kwrd in keywords:
                if kwrd in row["line_item"].lower():
                    indices.append(idx)
        
        if len(indices)>0:
            std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
    return std_hrzntl_note_df


def interest_income_filter(temp_dict):
    not_found_main_page_particular = temp_dict["main_page_notes_notfound_main_page_particular"]
    check_str = "finance income"
    temp = '\t'.join(not_found_main_page_particular)
    res = check_str in temp.lower()
    std_hrzntl_note_df = temp_dict['notes_horizontal_table_df']
    if res:
        if isinstance(std_hrzntl_note_df,pd.DataFrame):
            std_hrzntl_note_df.reset_index(drop=True,inplace=True)
            keywords = ['income']
            indices = []
            std_hrzntl_note_df = std_hrzntl_note_df.reset_index(drop=True)
            for idx,row in std_hrzntl_note_df.iterrows():
                for kwrd in keywords:
                    if kwrd in row["line_item"].lower():
                        indices.append(idx)
        
            if len(indices)>0:
                std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
        # if len(indices)>1:
        #     std_hrzntl_note_df = exclude_net_keyword_filter(std_hrzntl_df=std_hrzntl_note_df)
        #     std_hrzntl_note_df.reset_index(drop=True,inplace=True)

    temp_dict['notes_horizontal_table_df'] = temp_dict['notes_horizontal_table_df']

    return temp_dict 
    

# def interest_expense_filter_old(temp_dict):
#     std_hrzntl_note_df = temp_dict["notes_horizontal_table_df"]
#     main_page_cropped_df = temp_dict["main_page_cropped_df"]
#     negaive_note_df = pd.DataFrame()
#     negative_main_page_df = pd.DataFrame()
#     if len(std_hrzntl_note_df) > 0:
#         if isinstance(std_hrzntl_note_df,pd.DataFrame):
#             positive_df,negaive_note_df = extract_positive_values_rows(std_hrzntl_note_df)
#         else:
#             postive_df,negative_main_page_df = extract_positive_values_rows(main_page_cropped_df)
#     else:
#         postive_df,negative_main_page_df = extract_positive_values_rows(main_page_cropped_df)

#     if len(negaive_note_df) > 0 :
#         temp_dict["notes_horizontal_table_df"] = negaive_note_df
#     if len(negative_main_page_df) > 0 :
#         temp_dict["main_page_cropped_df"] = negative_main_page_df

#     return temp_dict


def interest_income_expense_filter_advance(temp_dict,datapoint_flag):
    net_kywrds = ["net","Net"]
    main_page_notes_found_main_page_particular = temp_dict["main_page_notes_found_main_page_particular"]
    main_page_notes_notfound_main_page_particular = temp_dict["main_page_notes_notfound_main_page_particular"]
    net_flag_notes_found = False
    net_flag_notes_not_found = False
    for i in main_page_notes_found_main_page_particular:
        if "net" in i.lower():
            if not net_flag_notes_found:
                net_flag_notes_found = True
    for i in main_page_notes_notfound_main_page_particular:
        if "net" in i.lower():
            if not net_flag_notes_not_found:
                net_flag_notes_not_found = True
    # print(f"net_flag_notes_found = {net_flag_notes_found}")
    # print(f"net_flag_notes_not_found = {net_flag_notes_not_found}")

    if net_flag_notes_not_found:
        ### if net finance income note not found then ignore net wala line item and consider finance income/cost/expense line items
        std_hrzntl_df = temp_dict["notes_horizontal_table_df"]
        std_hrzntl_df = exclude_net_keyword_filter(std_hrzntl_note_df=std_hrzntl_df)
        temp_dict["notes_horizontal_table_df"] = std_hrzntl_df
        if datapoint_flag == "smr_interest_income":
            temp_dict = interest_income_filter(temp_dict=temp_dict)

        if datapoint_flag == "smr_interest_expense":
            temp_dict = interest_expense_filter(temp_dict=temp_dict)


    if net_flag_notes_found:
        ### if net finance income note found then ignore finance income/cost/expense line items and consider net wala line
        main_page_notes_notfound_main_page_particular = temp_dict['main_page_notes_notfound_main_page_particular']
        std_hrzntl_df = temp_dict["notes_horizontal_table_df"]
        exclude_indices = []
        # print(f"main_page_notes_notfound_main_page_particular= {main_page_notes_notfound_main_page_particular}")
        # print(f"std_hrzntl_df={std_hrzntl_df}")
        for particular in main_page_notes_notfound_main_page_particular:
            for idx,row in std_hrzntl_df.iterrows(): 
                if particular in row["line_item"] and int(row["Note"]) == 0:
                    exclude_indices.append(idx)
        # print(f"exclude_indices={exclude_indices}")
        if len(exclude_indices)>0:
            std_hrzntl_df = std_hrzntl_df.iloc[~std_hrzntl_df.index.isin(exclude_indices)] 
        std_hrzntl_df.reset_index(drop=True,inplace=True)
        temp_dict["notes_horizontal_table_df"] = std_hrzntl_df

    return temp_dict

        





# def net_keyword_filtering_interest_income(temp_dict):
#     std_hrzntl_note_df = temp_dict["notes_horizontal_table_df"]



def make_all_positive(temp_dict):
    ## convert values from notes_horizontal_table_df, main_page_cropped_df , main_page_year_total to positive
    notes_horizontal_table_df = temp_dict['notes_horizontal_table_df']
    main_page_cropped_df = temp_dict['main_page_cropped_df']
    main_page_year_total = temp_dict['main_page_year_total']
    notes_cols = ["line_item","Note"]
    main_page_cols = ["Particulars","Notes","statement_section","statement_sub_section"]
    if len(notes_horizontal_table_df) > 0 :
        if isinstance(notes_horizontal_table_df,pd.DataFrame):
            year_cols = [i for i in notes_horizontal_table_df.columns if i not in notes_cols]
            notes_horizontal_table_df[year_cols] = notes_horizontal_table_df[year_cols].abs()
    if len(main_page_cropped_df) > 0:
        if isinstance(main_page_cropped_df,pd.DataFrame):
            year_cols = [i for i in main_page_cropped_df.columns if i not in main_page_cols]
            main_page_cropped_df[year_cols] = main_page_cropped_df[year_cols].abs()
    if len(main_page_year_total)>0:
        main_page_year_total = [abs(x) for x in main_page_year_total]

    temp_dict['notes_horizontal_table_df'] = notes_horizontal_table_df
    temp_dict['main_page_cropped_df'] = main_page_cropped_df
    temp_dict['main_page_year_total'] = main_page_year_total
    return temp_dict
    

def cost_of_sales_additional_keyword_filter(main_pg_cropped_df, main_pg_df):

    #first finding frommain page of PL if "Change in Invemtory" keyword present in any of line items
    try:
        if isinstance(main_pg_df,pd.DataFrame):
            main_pg_df.reset_index(drop=True,inplace=False)
            keywords = ['change in inventory', 'changes in inventory', 'change in inventories', 'changes in inventories']
            indices = []
            main_pg_df = main_pg_df.reset_index(drop=True)
            for idx,row in main_pg_df.iterrows():
                for kwrd in keywords:
                    if kwrd in row["Particulars"].lower():
                        indices.append(idx)
            
            if len(indices)>0:
                main_pg_df = main_pg_df.iloc[indices]
            main_pg_df.reset_index(drop=True,inplace=False)
        
        #appending the above data in main_pg_cropped_df    
        if isinstance(main_pg_cropped_df,pd.DataFrame):
            main_pg_cropped_df.reset_index(drop=True,inplace=False)
            if len(main_pg_cropped_df) > 0:
                main_pg_cropped_df.append(main_pg_df)
            else:
                main_pg_cropped_df = main_pg_df
        main_pg_cropped_df.reset_index(drop=True,inplace=False)
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:PLDataBucketingUtils.py,  function: cost_of_sales_additional_keyword_filter")
        Logger.logr.error(f"error occured: {e}")  
    return main_pg_cropped_df




def SMR_TAXES_filter(temp_dict):
    try:
        notes_horizontal_df = temp_dict["notes_horizontal_table_df"]
        main_page_df = temp_dict["main_page_cropped_df"]
        main_page_notes_notfound_main_page_particular = temp_dict["main_page_notes_notfound_main_page_particular"]
        main_non_year_cols = ["Particulars","Notes","statement_section","statement_sub_section"]
        main_page_df.reset_index(drop=True,inplace=True)
        if len(main_page_df)>0:
            year_cols = []
            if len(main_page_df)>0:
                year_cols = [int(i) for i in main_page_df.columns if i not in main_non_year_cols]
            main_dfcols = []
            for col in main_page_df.columns:
                if col not in main_non_year_cols:
                    main_dfcols.append(int(col))
                else:
                    main_dfcols.append(col)
            main_page_df.columns = main_dfcols
            years = year_cols
            col_list = ["line_item","Note"] #new code to add note
            col_list.extend(years)
            # print(f"col_list={col_list}")
            new_horizontal_note_df = pd.DataFrame(columns=col_list)
            tmp_df = dict.fromkeys(col_list)
            last_row_main_page = main_page_df.tail(1)
            # print(f"last_row_main_page= {last_row_main_page}")
            tmp_df["line_item"] =  last_row_main_page["Particulars"].values[0]
            if "Notes" in last_row_main_page.columns:
                    tmp_df["Note"] = last_row_main_page["Notes"].values[0] #new code to add note
            else:
                    tmp_df["Note"] = ""
            for year in years:
                    tmp_df[year] = last_row_main_page[year].values[0]
            # print(f"tmp_df={tmp_df}")
            new_horizontal_note_df = new_horizontal_note_df.append(tmp_df, ignore_index=True)
            temp_dict["notes_horizontal_table_df"] = new_horizontal_note_df
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:PLDataBucketingUtils.py,  function: SMR_TAXES_filter")
        Logger.logr.error(f"error occured: {e}")
    return temp_dict



