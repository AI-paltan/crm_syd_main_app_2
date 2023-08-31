import pandas as pd
import numpy as np
import re
import openpyxl
from dateutil import parser
from typing import List
from datetime import date
from functools import reduce
from typing import Optional
from fuzzywuzzy import fuzz

def find_column_numbers(df):
    col_len = len(df.columns)
    return col_len


def get_note_column(df):
    notes_regex = '(?:note(?:|s))'
    note_row_num = -1
    note_col_num = -1
    try:
        for idx,row in df.iterrows():
            bool_row = row.str.contains(notes_regex, flags=re.IGNORECASE,regex=True)
            if bool_row.any():
                note_row_num = idx
                res = [i for i, val in enumerate(bool_row) if val==True]
                note_col_num = res[0]
                break
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: get_note_column")
        Logger.logr.error(f"error occured: {e}")
    try:
        def is_number_repl_isdigit(s):
            """ Returns True if string is a number. """
            try:
                # print(s)
                return s.replace('.','',1).isdigit()
            except:
                return False
        
        if note_row_num == -1 and note_col_num == -1:
            # print(df.info())
            # df.iloc[:,1] = df.iloc[:,1].astype(float)
            # df.iloc[:,1] = pd.to_numeric(df.iloc[:,1], errors='coerce',downcast="float")
            # df = df.replace(np.nan, 0, regex=True)
            # print(df.info())
            for i in range(len(df)):
                if is_number_repl_isdigit(df.iloc[i,1]):
                    df.iat[i,1] = float(df.iloc[i,1])
                else:
                    df.iat[i,1] = None
            total = df.iloc[:,1].sum()
            # print(total)
            if total>10.0:
                note_col_num = 1
                note_row_num = 0
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: get_note_column")
        Logger.logr.error(f"error occured: {e}")
        print(e)
    return note_row_num,note_col_num

def get_years_and_positions_with_notes(df,notes_indices):
    def get_regex_year(val):
        year_val = -1
        regex = '(\d{4}|\d{2})'
        match = re.findall(regex, val)
        match.sort(key=len, reverse=True) 
        if len(match) > 0:
            for value in match:
                if len(value) == 4:
                    year_val = value
                elif len(value) == 2:
                    year_val = '20'+str(value)
                if int(year_val) <= int(date.today().year) and int(year_val)>=(int(date.today().year)-6):
                    return str(year_val)        
        else:
            return year_val
    
    note_x = notes_indices[0]
    note_y = notes_indices[1]
    year_list: list = []
    year_indices: List(List) = []
    raw_year_text:list = []
    try:
        for idx,row in df.iterrows():
            year_list: list = []    ## to make sure that both year columns lies in one row
            year_indices: List(List) = []  ## BFE file issue as one year found in first row which is wrong and second year found in second row which is correct but not considering next column as len of year_list fullfils
            raw_year_text:list = []
            if (note_x-2) <= idx <= (note_x+2):
                for col_idx, item in row.iteritems():
                    if col_idx > note_y:
                        ## old logic
                        # try:
                        #     year = parser.parse(str(item), fuzzy=True).year
                        # except:
                        #     year = get_regex_year(str(item))
                        ## new logic; BFE ; because 31 march is giving as 2023 year output in old logic
                        year = get_regex_year(str(item))
                        if year:  #to avoid Nonetype issue
                            if int(year) > 0:
                                year_list.append(int(year))
                                year_indices.append([idx,col_idx])
                                raw_year_text.append(item)
            if len(year_list) == (len(df.columns) - note_y-1):
                break
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: get_years_and_positions_with_notes")
        Logger.logr.error(f"error occured: {e}")
    return year_list,year_indices,raw_year_text


def get_years_and_positions_without_notes(df):
    ## this is without notes column
    def get_regex_year(val):
        year_val = -1
        regex = '(\d{4}|\d{2})'
        match = re.findall(regex, val)
        match.sort(key=len, reverse=True) 
        if len(match) > 0:
            for value in match:
                if len(value) == 4:
                    year_val = value
                elif len(value) == 2:
                    year_val = '20'+str(value)
                if int(year_val) <= int(date.today().year) and int(year_val)>=(int(date.today().year)-6):
                    return str(year_val)        
        else:
            return year_val

    year_list: list = []
    year_indices: List(List) = []
    raw_year_text:list = []
    try:
        for idx,row in df.iterrows():
            # if (note_x-2) < idx < (note_x+2):
            year_list: list = []
            year_indices: List(List) = []
            raw_year_text:list = []
            for col_idx, item in row.iteritems():
                if col_idx > 0:
                    # try:
                    #     year = parser.parse(str(item), fuzzy=True).year
                    # except:
                    #     year = get_regex_year(str(item))
                    year = get_regex_year(str(item))
                    if year:  #to avoid Nonetype issue
                        if year and int(year) > 0:
                            year_list.append(int(year))
                            year_indices.append([idx,col_idx])
                            raw_year_text.append(item)
            if len(year_list) == 2:
                break
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: get_years_and_positions_without_notes")
        Logger.logr.error(f"error occured: {e}")
    return year_list,year_indices,raw_year_text


def get_data_chunk_span_with_notes(df,notes_indices,years_indices):
    data_start_x = -1
    particulars_y = -1
    data_start_y = -1
    data_end_y = -1
    # print(df.info())
    try:
        notes_x = notes_indices[0]
        notes_y = notes_indices[1]
        max_year_x = list(np.max(np.array(years_indices),axis=0))[0]#max(years_indices,key=max)[0]
        min_year_y = list(np.min(np.array(years_indices),axis=0))[1]#min(years_indices,key=min)[1]
        max_year_y = list(np.max(np.array(years_indices),axis=0))[1]#max(years_indices,key=max)[1]
        # print(f"max_year_x = {max_year_x}")
        # print(f"min_year_y = {min_year_y}")
        # print(f"max_year_y = {max_year_y}")
        max_header = max([notes_x,max_year_x])
        # print(f"max_header={max_header}")
        for i in range(max_header+1,len(df)):
            # print(f"inside loop = {df.iat[i,notes_y-1]}")
            if not pd.isnull(df.iat[i,notes_y-1]):
                data_start_x = i
                particulars_y = notes_y-1
                data_start_y = min_year_y
                data_end_y = max_year_y
                break
        # print(f"data_start_x={data_start_x}")
        # print(f"particulars_y={particulars_y}")
        # print(f"data_start_y={data_start_y}")
        # print(f"data_end_y={data_end_y}")
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: get_data_chunk_span_with_notes")
        Logger.logr.error(f"error occured: {e}")
        # print(e)
    return data_start_x,data_start_y,data_end_y,particulars_y
    

def get_data_chunk_span_without_notes(df,years_indices):
    data_start_x = -1
    particulars_y = -1
    data_start_y = -1
    data_end_y = -1
    try:
        max_year_x = list(np.max(np.array(years_indices),axis=0))[0]#max(years_indices,key=max)[0]
        min_year_y = list(np.min(np.array(years_indices),axis=0))[1]#min(years_indices,key=min)[1]
        max_year_y = list(np.max(np.array(years_indices),axis=0))[1]#max(years_indices,key=max)[1]
        max_header = max_year_x
        for i in range(max_header+1,len(df)):
            if not pd.isnull(df.loc[i,min_year_y-1]):
                data_start_x = i
                particulars_y = min_year_y-1
                data_start_y = min_year_y
                data_end_y = max_year_y
                break
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: get_data_chunk_span_without_notes")
        Logger.logr.error(f"error occured: {e}")
    return data_start_x,data_start_y,data_end_y,particulars_y

def split_numbers(number,threshold=60):
    ### this function is ued to split combined noted number
    #  eg: 1214 -> 12,14
    def split_by_n( seq, n ):
        """A generator to divide a sequence into chunks of n units."""
        seq = str(seq)
        while seq:
            yield int(seq[:n])
            seq = seq[n:]
    num_list = []
    try:
        if len(number) <= 3:
            if int(number[1:]) > threshold:
                num_list.append(number[0:2])
                num_list.append(number[2:])
            else:
                num_list.append(number[0])
                num_list.append(number[1:])
        else:
            number_split = list(split_by_n(number,2))
            for split in number_split:
                if split>threshold:
                    more_split = list(split_by_n(split,1))
                    num_list.extend(more_split)
                else:
                    num_list.extend([split])
    except Exception as e:
        num_list.append(number)
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: split_numbers")
        Logger.logr.error(f"error occured: {e}")
    return num_list

def find_note_subnote_number(number):
    note = ''
    subnote = ''
    try:
        if bool(re.match(r'\d+.\d+',str(number))):
            note = str(number).split('.')[0]
            subnote = str(number).split('.')[1]
        elif bool(re.match(r'\d+\(\w+\)',str(number))):
                note = str(number).split('(')[0]
                subnote = "(" + str(number).split('(')[1]
        elif bool(re.match(r'\d+[A-Za-z]+',str(number))):
                res = re.findall(r'[A-Za-z]+|\d+', str(number))
                note = res[0]
                subnote = res[1]
        elif bool(re.match(r'\d+',str(number))):
                note = number
                subnote = ''
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: find_note_subnote_number")
        Logger.logr.error(f"error occured: {e}")
    return note,subnote

def get_note_pattern(note,subnote):
    if str(subnote).isnumeric():
        note_pattern = str(note)+'.'+str(subnote)
    else:
        note_pattern = str(note)+str(subnote)
    return note_pattern

def notes_number_processing(df,notes_indices,data_start_x,particulars_y,notes_dict):
    
    ###r"and|[\s,-]+" to split by (and comma space and hypen)
    # notes_col = df.iloc[notes_indices[0]+1:,notes_indices[1]]
    notes_col = df['Notes']
    # particulars_col = df.iloc[notes_indices[0]+1:,particulars_y]
    particulars_col = df['Particulars']
    section_col = []
    subsection_col = []
    if 'statement_section' in df.columns:
        section_col = df['statement_section']
        subsection_col = df['statement_sub_section']

    # print(f"section_col = {section_col}")
    # print(f"subsection_col = {subsection_col}")
    year_col_list = [i for i in df.columns if i not in ["Notes","Particulars","statement_section","statement_sub_section"]]
    ref_list : list = []
    try:
        for idx,val in enumerate(notes_col):
            notes_list = []
            if not pd.isnull(val):
                if len(str(val)) > 2 and str(val).isdigit():
                    split_notes_list = split_numbers(val,60)
                    notes_list = split_notes_list
                elif ',' in str(val):
                    split_notes_list = re.split(r',',str(val))
                    notes_list = split_notes_list
                elif 'and' in str(val):
                    split_notes_list = re.split(r'and',str(val))
                    notes_list = split_notes_list
                else:
                    notes_list = [str(val)]
                notes_list = [i.strip() for i in notes_list]
                note_no : list= []
                subnote_no : list = []
                for raw_note in notes_list:
                    note,subnote = find_note_subnote_number(str(raw_note))
                    note_no.extend([note])
                    subnote_no.extend([subnote])
                temp_dict = {}
                temp_dict['particular'] = particulars_col.iloc[idx]
                temp_dict['raw_note_no'] = val
                temp_dict['processed_raw_note'] = notes_list
                temp_dict['main_note_number']=note_no
                temp_dict['subnote_number'] = subnote_no
                if len(section_col)>0:
                    temp_dict['section'] = section_col.iloc[idx]
                    temp_dict['subsection'] = subsection_col.iloc[idx]
                else:
                    temp_dict['section'] = ''
                    temp_dict['subsection'] = ''
                tmp_year_value_dct = {}
                for year in year_col_list:
                    tmp_year_value_dct[year] = df.iloc[idx][year]
                    # tmp_year_value_dct[year] = df.iat[idx][year]
                temp_dict["year_values"] = tmp_year_value_dct
                ref_list.append(temp_dict)
                # print(note_no)
                for noteno,subnoteno in zip(note_no,subnote_no):
                    if notes_dict.get(noteno, {}).get(subnoteno):
                        notes_dict[noteno][subnoteno].append(particulars_col.iloc[idx])
                    else:
                        notes_dict[noteno][subnoteno] = [particulars_col.iloc[idx]]
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: notes_number_processing")
        Logger.logr.error(f"error occured: {e}")
        # print(e)
    # print("ref list:", ref_list)
    return ref_list,notes_dict


def number_data_processing(df,data_start_x,data_start_y,data_end_y):
    def clean_number(number):
        number = str(number).replace(r',',"")
        number = str(number).replace(r')',"")
        number = str(number).replace(r'(',"-")
        return number
    def split_merge_rows(row):
        pass
    for i in range(data_start_y,data_end_y+1):
        df.iloc[data_start_x:,i] = df.iloc[data_start_x:,i].apply(clean_number).apply(pd.to_numeric , errors='coerce').fillna(0)
        # df.iat[data_start_x:,i] = df.iat[data_start_x:,i].apply(clean_number).apply(pd.to_numeric , errors='coerce').fillna(0)
#     for idx,row in df.iterrows()
    return df


def set_headers(df,data_start_x,data_end_y,headers):
    try:
        subset_df = df.iloc[data_start_x:,:]
        # subset_df = df.iat[data_start_x:,:]
        subset_df.columns = headers
        subset_df = subset_df.reset_index(drop=True)
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: set_headers")
        Logger.logr.error(f"error occured: {e}")
    return subset_df


def check_and_remove_duplicate_column(nte_df):
    try:
        cnt = 0
        row_duplicate = 0
        ratio_duplicate = 0
        # if particular_end_col > 0 and particular_end_col==1:
        for idx,row in nte_df.iterrows():
            if not pd.isnull(row[1]):
                if (fuzz.partial_ratio(str(row[1]),str(row[0])) > 95):
                    row_duplicate = row_duplicate+1
                cnt=cnt+1
        if row_duplicate > 0:
            ratio_duplicate = (row_duplicate/cnt)*100
            if ratio_duplicate >= 90:  ## original 90 changed to 80 for kanematsu from 10 files on 26 july for new model as problem with row_col model
                nte_df = nte_df.drop(nte_df.columns[1], axis=1).T.reset_index(drop=True).T
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: check_and_remove_duplicate_column")
        Logger.logr.error(f"error occured: {e}")
    # print(f"ratio_duplicate  = {ratio_duplicate}")
    return nte_df

def check_and_remove_duplicate_column_main_page(nte_df):
    cnt = 0
    row_duplicate = 0
    ratio_duplicate = 0
    # if particular_end_col > 0 and particular_end_col==1:
    for idx,row in nte_df.iterrows():
        if not pd.isnull(row[1]):
            if (fuzz.partial_ratio(str(row[1]),str(row[0])) > 95):
                row_duplicate = row_duplicate+1
            cnt=cnt+1
    if row_duplicate > 0:
        ratio_duplicate = (row_duplicate/cnt)*100
        # print(ratio_duplicate)
        if ratio_duplicate >= 60:  ## original 90 changed to 80 for kanematsu from 10 files on 26 july for new model as problem with row_col model
            ### for mrging data from dropped column to 1st column
            for idx,row in nte_df.iterrows():
                if not pd.isnull(row[1]):
                    if (fuzz.partial_ratio(str(row[1]),str(row[0])) < 95):
                        nte_df.at[idx,0] = nte_df.at[idx,0] + nte_df.at[idx,1]
            nte_df = nte_df.drop(nte_df.columns[1], axis=1).T.reset_index(drop=True).T

    # print(f"ratio_duplicate  = {ratio_duplicate}")
    return nte_df


def find_and_remove_all_duplicate_columns(df):
    # first identify all text columns
    ## find all duplicate columns and drop them
    ## take 1st column and find duplicate columns and merge them
    ## then continue this procss from next to duplicate columns:
    ## eg 1 and 2 are duplicate then next time take 3rd column and tsrt finding duplicate
    def is_duplicate_fun(nte_df,col1,col2):
        duplicate_flag  = False
        cnt = 0
        row_duplicate = 0
        ratio_duplicate = 0
        for idx,row in nte_df.iterrows():
            if not pd.isnull(row[col2]):
                if (fuzz.partial_ratio(str(row[col2]),str(row[col1])) > 95):
                    row_duplicate = row_duplicate+1
                cnt=cnt+1
        if row_duplicate > 0:
            ratio_duplicate = (row_duplicate/cnt)*100
            # print(ratio_duplicate)
            if ratio_duplicate >= 50: 
                duplicate_flag = True
        
        return duplicate_flag
    
    def merge_two_columns(nte_df,col1,col2):
        for idx,row in nte_df.iterrows():
                if not pd.isnull(row[col2]):
                    if (fuzz.partial_ratio(str(row[1]),str(row[0])) < 95):
                        nte_df.at[idx,col1] = str(nte_df.at[idx,col1]) + str(nte_df.at[idx,col2])

        return nte_df

    # cnt = 0
    # row_duplicate = 0
    # ratio_duplicate = 0
    try:
        colmns_len = len(df.columns)
        columns_done = 0
        columns_to_drop = []
        # for i in range(len(colmns_len)):
        i = 0
        j = 1
        while i < colmns_len and j < colmns_len:
            is_duplicate = is_duplicate_fun(df,i,j)
            if is_duplicate:
                columns_to_drop.append(j)
                # print(f"i = {i} , j= {j}")
                df = merge_two_columns(df,i,j)
                j=j+1
            else:
                i = j + 1
                j = i + 1

        df = df.drop(df.columns[columns_to_drop], axis=1).T.reset_index(drop=True).T
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: main_page_processing_service , File:utils.py,  function: find_and_remove_all_duplicate_columns")
        Logger.logr.error(f"error occured: {e}")
    return df
    



def main_page_table_preprocessing(table_df):
    if len(table_df) > 0:
        sorted_table_df = table_sorting(table_df)
        cleaned_table_list = []
        for idx,value in sorted_table_df.iterrows():
            tb_df = pd.read_html(value.html_string)[0]
            clean_tb_df  = check_and_remove_duplicate_column_main_page(nte_df=tb_df)
            cleaned_table_list.append(clean_tb_df)
        # print(cleaned_table_list)
        merged_table_df = merge_columnwise_tables(table_df_list=cleaned_table_list)

        return merged_table_df
    else:
        return table_df

       

#remove duplicate columns using generic function taking inspiration from above function : for time being use above function only until new code is born

#sort table using bbox
#if more than 1 table try to merge using columns starting from last
#if merge failes pick top table



def table_sorting(table_df):
    sorted_df = table_df.sort_values(by='top',ignore_index=True)
    return sorted_df

def generic_check_and_remove_duplicate_column(table_df):
    cnt = 0
    row_duplicate = 0
    ratio_duplicate = 0
    


def merge_columnwise_tables(table_df_list):
    ### if column matched then merge columnwise as it it else 
    ## iterate over column and merge from last
    merged_table_df = []
    if len(table_df_list) > 0:
        merged_table_df = [table_df_list[0]]
        if len(table_df_list)>1:
            for table in table_df_list[1:]:
                if len(merged_table_df[0].columns) == len(table.columns):
                    merged_table_df.append(table)
                    # merged_table_df = pd.concat(merged_table_df)
                else:
                    ##check column length for tables (merged_table_df and next table from list)
                    ##table having more columns will get appended from data   
                    # for col1,col2 in zip():
                    pass
    merged_table_df = pd.concat(merged_table_df)
    return merged_table_df
