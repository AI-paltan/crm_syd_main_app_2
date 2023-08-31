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



def interest_income_filter_old(temp_dict):
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
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)

    temp_dict['notes_horizontal_table_df'] = temp_dict['notes_horizontal_table_df']

    return temp_dict 
    

def interest_expense_filter_old(temp_dict):
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
    return main_pg_cropped_df




def SMR_TAXES_filter(temp_dict):
    notes_horizontal_df = temp_dict["notes_horizontal_table_df"]
    main_page_df = temp_dict["main_page_cropped_df"]
    main_page_notes_notfound_main_page_particular = temp_dict["main_page_notes_notfound_main_page_particular"]
    main_non_year_cols = ["Particulars","Notes","statement_section","statement_sub_section"]
    main_page_df.reset_index(drop=True,inplace=True)
    if len(main_page_df)>0:
        year_cols = []
        if len(main_page_df)>0:
            year_cols = [int(i) for i in main_page_df.columns if i not in main_page_df]
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
        new_horizontal_note_df = pd.DataFrame(columns=col_list)



