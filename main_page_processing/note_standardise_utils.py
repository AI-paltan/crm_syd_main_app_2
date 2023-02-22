from fuzzywuzzy import fuzz
import re
import pandas as pd
import numpy as np




## given df find date location in first column using pd.to_datetime
### else find in each row and get location of first row
def find_date_location(df):
    ## returns (col_index_list,row_index_list,year,raw_text)
    ## find if first column contains any date
    def get_regex_year(val):
        year_val = -1
        regex = '(\d{4}|\d{2})'
        match = re.findall(regex, val)
        match.sort(key=len, reverse=True) 
    #     print(match)
        if len(match) > 0:
            for value in match:
                if len(value) == 4:
                    year_val = value
#                     return str(year_val)
                elif len(value) == 2:
                    year_val = '20'+str(value)
#                     return str(year_val)
                if int(year_val) <= int(date.today().year):
                    return str(year_val)        
        else:
            return year_val
    columns_number = []
    row_numbers = []
    raw_text = []
    extracted_year = []
    first_col_date_flag = df.iloc[:,0].transform(pd.to_datetime,errors='coerce').notnull().any()
    if first_col_date_flag:
        ## find all indices and return 
        columns_number.append(0)
        date_present_rows_indices_for_col0 = sorted(df.iloc[:,0][df.iloc[:,0].transform(pd.to_datetime,errors='coerce').notnull()].index.to_list())
        row_numbers.append(date_present_rows_indices_for_col0)
        if len(row_numbers) > 1:
            raw_text_lst = df.iloc[:,0][df.iloc[:,0].transform(pd.to_datetime,errors='coerce').notnull()].to_list()
            extracted_year_lst = df.iloc[:,0][df.iloc[:,0].transform(pd.to_datetime,errors='coerce').notnull()].transform(pd.to_datetime,errors='coerce').dt.year.to_list()
            raw_text.append(raw_text_lst)
            extracted_year.append(extracted_year_lst)
            first_col_date_flag = False
    row_date_flag = False
    for idx,row in df.iterrows():
        index_thresh = min(date_present_rows_indices_for_col0)-1 if first_col_date_flag else 10
        if idx <= index_thresh:
            row_date_flag = df.iloc[idx].transform(pd.to_datetime,errors='coerce').notnull().any()
            regex_year_found = False
            year_list = []
            year_indices = []
            raw_year_text = []
            for col_idx, item in row.iteritems():
                if col_idx > 0:
                    year = get_regex_year(str(item))
                    if  int(year) > 0:
                        regex_year_found = True
                        year_list.append(int(year))
                        year_indices.append([idx,col_idx])
                        raw_year_text.append(item)
            if row_date_flag:
                date_present_column_indices_for_row = sorted(df.iloc[idx][df.iloc[idx].transform(pd.to_datetime,errors='coerce').notnull()].index.to_list())
                raw_text_lst = df.iloc[idx][df.iloc[idx].transform(pd.to_datetime,errors='coerce').notnull()].to_list()
                extracted_year_lst = df.iloc[idx][df.iloc[idx].transform(pd.to_datetime,errors='coerce').notnull()].transform(pd.to_datetime,errors='coerce').dt.year.to_list()
                for col,raw_year,extract_year in zip(date_present_column_indices_for_row,raw_text_lst,extracted_year_lst):
                    columns_number.append(col)
                    row_numbers.append([idx])
                    raw_text.append([raw_year])
                    extracted_year.append([extract_year])
                break
            elif regex_year_found:
                for col,raw_year,extract_year in zip(year_indices,raw_year_text,year_list):
                    columns_number.append(col)
                    row_numbers.append([idx])
                    raw_text.append([raw_year])
                    extracted_year.append([extract_year])
    return columns_number,row_numbers,raw_text,extracted_year


## given df first clean all cells using the rules used in main page processing 
## and then convert to numeric. and find top left and down right coordinates
def find_data_block_location(note_df,date_block_coordinates):
    ## verify the location with date cooridnates if found as header column mean colum more than 1
    def find_first_col(df,first_row_number):
        for i in range(len(df.columns)):
            col_found = df.iloc[:,i].transform(pd.to_numeric,errors='coerce').notnull().any()
            if col_found and i > 0:
                return i
    def find_particulars_start_row(df,particulars_end_col,data_start_row):
#         row_scanning_up = 2
        particulars_start_row = -1
        if df.iloc[data_start_row-1,particulars_end_col+1:].isnull().any():
            if df.iloc[data_start_row-2,particulars_end_col+1:].isnull().any():
                particulars_start_row = data_start_row-2
            else:
                particulars_start_row = data_start_row-1
        else:
            particulars_start_row = data_start_row
        return particulars_start_row
        
    def find_first_row(df,year_rows,year_cols):
        col,row = -1,-1
        particular_col,particular_row = -1,-1
        for idx, value in df.iterrows():
            row_found = df.iloc[idx].transform(pd.to_datetime,errors='coerce').notnull().any()
            if row_found and idx not in year_rows:
                data_present_column_indices_for_row = sorted(df.iloc[idx][df.iloc[idx].transform(pd.to_numeric,errors='coerce').notnull()].index.to_list())
                if min(data_present_column_indices_for_row) > 0:
                    col = min(data_present_column_indices_for_row)
                    row = idx
                    if len(year_cols) > 0:
                        if col == min(year_cols):
                            particular_col=col-1
                        else:
                            particular_col = min(year_cols)-1
                    else:
                        particular_col = 0                    
                else:
                    col = data_present_column_indices_for_row[1]
                    row = idx
                    if col == 1:
                        particular_col = 0
                    else:
                        particular_col = col -1
                return col,row,particular_col
    def get_year_coordinates(date_block_coordinates):
        year_rows = []
        year_cols = []
        if len(date_block_coordinates[0])>0:
            for column,rows in zip(date_block_coordinates[0],date_block_coordinates[1]):
                if column > 0:
                    year_rows.extend(rows)
                    year_cols.extend([column])
        return list(set(year_rows)),list(set(year_cols))
            
    def clean_number(number):
        number = str(number).replace(r',',"")
        number = str(number).replace(r')',"")
        number = str(number).replace(r'(',"-")
        return number
    first_data_col,first_data_row ,particular_col,particular_start_row,last_data_col,last_data_row= -1,-1,-1,-1, -1, -1
    if len(note_df) > 0:
        df = note_df.copy()
        for col in range(len(df.columns)):
            df.iloc[:,col] = df.iloc[:,col].apply(clean_number).apply(pd.to_numeric , errors='coerce')
        year_rows,year_cols = get_year_coordinates(date_block_coordinates=date_block_coordinates)
        try:
            first_data_col, first_data_row ,particular_col= find_first_row(df=df,year_rows=year_rows,year_cols = year_cols)
            particular_start_row = find_particulars_start_row(note_df,particular_col,first_data_row)
            last_data_col = len(df.columns)-1
            last_data_row = len(df)-1
        except:
            pass
    return (first_data_col,first_data_row),particular_col,particular_start_row#,(last_data_col,last_data_row)





##using the coordinates of data block finalize headers
## max 3 rows upside and 2 column left 
def find_col_headers(nte_df,data_block_coordinates_start,particulars_endcol_coordinates,particulars_start_row):
    header_indices = []
    for idx,row in nte_df.iterrows():
        if idx < particulars_start_row:
            if row[particulars_endcol_coordinates+1:].notnull().any():
                header_indices.append(idx)
    return header_indices

## if more than 1 column present left to data block then check if column1 and 2 is duplicate or not. any row.
## if yes remove that row. take the percentage of duplcation with total row
def check_and_remove_duplicate_particulars_column(nte_df,particulars_endcol_coordinates,particulars_start_row):
    cnt = 0
    row_duplicate = 0
    ratio_duplicate = 0
    particular_end_col = particulars_endcol_coordinates
    if particular_end_col > 0 and particular_end_col==1:
        for idx,row in nte_df.iterrows():
            if idx>=particulars_start_row:
                if not pd.isnull(row[1]):
                    if (fuzz.partial_ratio(str(row[1]),str(row[0])) > 95):
                        row_duplicate = row_duplicate+1
                    cnt=cnt+1
    if row_duplicate > 0:
        ratio_duplicate = (row_duplicate/cnt)*100
        if ratio_duplicate > 90:
            nte_df = nte_df.drop(nte_df.columns[1], axis=1).T.reset_index(drop=True).T
            particular_end_col = particular_end_col-1
    return nte_df,particular_end_col



## find all rows for which particulars text is present but no data number present
def find_row_headers(nte_df,particulars_endcol_coordinates,particulars_start_row):
    row_header_indices = []
    for idx,row in nte_df.iterrows():
        if idx >= particulars_start_row:
            if not row[particulars_endcol_coordinates+1:].notnull().any():
                row_header_indices.append(idx)
    return row_header_indices


def fill_missing_multilevel_header(df,header_indices,particulars_end_col):
#     print(header_indices)
    for header_idx in header_indices:
        df.iloc[header_idx,particulars_end_col+1:] = df.iloc[header_idx,particulars_end_col+1:].fillna(method='ffill')
        df.iloc[header_idx,particulars_end_col+1:] = df.iloc[header_idx,particulars_end_col+1:].fillna(method='bfill')
    return df


### convert all row headers to columns. make blocks of row headers
### until next row header appears or end of df assign row header as the column value of that block
def convert_row_header_to_columns(df,row_header_indices,particular_start_row):
    temp_df = df.copy()
    temp_df['row_header'] = None
    if len(row_header_indices)>0:
#         row_header_indices.append(len(temp_df)-1)
#         row_header_indices = sorted(row_header_indices)
        for idx,row in temp_df.iterrows():
            if idx>= particular_start_row:
                if idx in row_header_indices:
                    temp_df.at[idx,'row_header'] = row[0]
    temp_df['row_header'].fillna(method='ffill',inplace=True)
    return temp_df
                


def convert_col_header_to_columns(df,header_indices,particular_end_col,particular_start_row,databox_end_coordinates):
    temp_df = df.copy()
    final_df = pd.DataFrame()
    final_dict = {}
#     print(header_indices)
    header_indices = sorted(header_indices,reverse=True)
    if len(header_indices)>0:
        for idx,column in enumerate(df):
            if idx>int(particular_end_col) and idx<=int(databox_end_coordinates[0]):
                temp_df = pd.DataFrame()
                temp_df = df.iloc[particular_start_row:,:particular_end_col+1]
                temp_df['row_header'] = df['row_header']
#                 print(temp_df)
                temp_df['value'] = None
                temp_df['value'] = df.iloc[particular_start_row:,idx]
#                 print(temp_df)
                for j,header_idx in enumerate(header_indices):
                    temp_df[f"header_col_{j}"] = None
                    temp_df[f"header_col_{j}"] = df.iloc[header_idx,idx]
                final_df = pd.concat([final_df, temp_df], ignore_index=True)
    for col in final_df.columns:
        final_df.rename(columns={col:f"line_item_{col}" if str(col).isdigit() else col},inplace=True)
    return final_df
    # display.display(final_df)              


def set_year_column_for_final_df(fin_df,date_coordinates,header_indices):
    if len(date_coordinates[0])>0:
        col_subscript = -1
        row_indices = []
        fin_df['year'] = None
        header_indices = sorted(header_indices,reverse=True)
        for column,rows in zip(date_coordinates[0],date_coordinates[1]):
                if column > 0:
                    col_subscript = header_indices.index(rows[0])
                elif column == 0:
                    row_indices = rows
        if col_subscript >=0:
            fin_df['year'] = fin_df[f"header_col_{col_subscript}"].transform(pd.to_datetime).dt.year
        else:
            if fin_df['row_header'].transform(pd.to_datetime,errors="coerce").notnull().any():
                fin_df['year'] = fin_df["row_header"].transform(pd.to_datetime,errors='coerce').dt.year
            else:
                for col_header , line_row in fin_df.filter(like="line_item", axis=1).iteritems():
                    print(line_row)
                    if line_row.transform(pd.to_datetime,errors="coerce").notnull().any():
                        fin_df['year'] = line_row.transform(pd.to_datetime,errors='coerce').dt.year
                        break

        return fin_df