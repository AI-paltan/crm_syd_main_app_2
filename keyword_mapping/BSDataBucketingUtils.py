import pandas as pd
import numpy as np
import re


def second_filter_PPE(std_hrzntl_note_df,month):
    ## this function will filter PPE note further for month of given annual statemnt
    month_indices = []
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df = std_hrzntl_note_df.reset_index(drop=True)
        for idx,row in std_hrzntl_note_df.iterrows():
            if month in row["line_item"].lower():
                month_indices.append(idx)
        # print(month_indices)
        if len(month_indices)>0:
            std_hrzntl_note_df = std_hrzntl_note_df.iloc[month_indices]
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
    return std_hrzntl_note_df

def gross_PPE_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keywords = ['cost','gross']
        indices = []
        for idx,row in std_hrzntl_note_df.iterrows():
            for kwrd in keywords:
                if kwrd in row["line_item"].lower():
                    indices.append(idx)
        
        if len(indices)>0:
            std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
    return std_hrzntl_note_df


def accumulation_PPE_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keywords = ['depreciatio','accumulated depreciation']
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

def ppe_total_keyword_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keywords = ['total']
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


def carrying_amount_keyword_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keywords = ['carrying amount','carrying amounts','carryingamount', 'carryingamounts']
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

def current_word_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keyword = ['current']
        exclude_keywords = ['non-current','noncurrent']
        indices = []
        exclude_indices = []
        for idx,row in std_hrzntl_note_df.iterrows():
            for kwrd in keyword:
                if kwrd in row["line_item"].lower():
                    indices.append(idx)
            for exclude_kwd in exclude_keywords:
                if exclude_kwd in row["line_item"].lower():
                    exclude_indices.append(idx)

        current_indices = list(set(indices).difference(set(exclude_indices)))
        
        if len(current_indices)>0:
            std_hrzntl_note_df = std_hrzntl_note_df.iloc[current_indices]
        
        # if len(indices)>0:
        #     std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
    return std_hrzntl_note_df

def noncurrent_word_filter(std_hrzntl_note_df):
    if isinstance(std_hrzntl_note_df,pd.DataFrame):
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
        keyword = ['non-current','noncurrent']
        indices = []
        for idx,row in std_hrzntl_note_df.iterrows():
            for kwrd in keyword:
                if kwrd in row["line_item"].lower():
                    indices.append(idx)
        
        if len(indices)>0:
            std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
        std_hrzntl_note_df.reset_index(drop=True,inplace=True)
    return std_hrzntl_note_df


def append_main_page_line_item_with_notes_items():
    ### for fields like other current assets, other noncurrent assets, other liabilities etc.
    ###
    pass


def remove_main_page_line_items_if_no_notes_items():
    ### for fields like rent in P&L statements
    pass



def accrued_word_filter(temp_dict):
    hrznt_df = temp_dict["notes_horizontal_table_df"]
    remaining_hrznt_df = temp_dict["remaining_notes_horizontal_table_df"]
    if isinstance(remaining_hrznt_df,pd.DataFrame):
        remaining_hrznt_df.reset_index(drop=True,inplace=True)
        hrznt_df.reset_index(drop=True,inplace=True)
        keywords = ['accrued','accrual']
        indices = []
        for idx,row in remaining_hrznt_df.iterrows():
            for kwrd in keywords:
                if kwrd in row["line_item"].lower():
                    indices.append(idx)
        
        if len(indices)>0:
            hrznt_df.reset_index(drop=True,inplace=True)
            if len(hrznt_df) > 0:
                # std_hrzntl_note_df = std_hrzntl_note_df.iloc[indices]
                filter_df = remaining_hrznt_df.iloc[indices]
                hrznt_df.append(filter_df)
                temp_dict["notes_horizontal_table_df"] = hrznt_df
            else:
                temp_dict["notes_horizontal_table_df"] = remaining_hrznt_df.iloc[indices]
    return temp_dict




# def get
def get_years_values(df):
    year_dict = {}
    try:
        if len(df) > 0:
            col_avoid = ['Particulars','Notes','statement_section','statement_sub_section']
            year_cols = [i for i in df.columns if i not in col_avoid]
            if len(year_cols) > 0:
                for year in year_cols:
                    year_dict[int(year)] = df[year].sum()
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: get_years_values")
        Logger.logr.error(f"error occured: {e}")   
    return year_dict

def get_toal_current_assets(df):
    year_dict = get_years_values(df)
    return year_dict

def get_toal_noncurrent_assets(df):
    year_dict = get_years_values(df)
    return year_dict

def get_toal_current_liabilities(df):
    year_dict = get_years_values(df)
    return year_dict


def get_toal_noncurrent_liabilities(df):
    year_dict = get_years_values(df)
    return year_dict

def get_total_equity(df):
    year_dict = get_years_values(df)
    return year_dict


def get_subfields_sum(meta_dict):
    year_dict = {}
    try:
        note_df = meta_dict['notes_horizontal_table_df']
        if len(note_df) > 0:
            year_col = [i for i in note_df.columns if i not in ["line_item","Note"]]
            for year in year_col:
                # year = int(year)
                year_dict[int(year)] = note_df[year].sum()
        ### commenting below code 23 aug as we want to consider availbale line items from notes horizontal df only
        else:
            for value,year in zip(meta_dict["main_page_year_total"],meta_dict["main_page_year_list"]):
                # year = int(year)
                year_dict[int(year)] = value  
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: get_subfields_sum")
        Logger.logr.error(f"error occured: {e}")   
        # print(e)
    return year_dict


def get_Current_Section_fields_total(bs_bucketing_dict):
    meta_keywords = ["ca_cash_and_cash_equivalents","ca_account_receivables","ca_inventories","ca_prepaid_expenses"]
    current_assets_section_year_sum = {}
    total_of_all_upper_fields = {}
    try:
        for meta_keyword in meta_keywords:
            if meta_keyword in bs_bucketing_dict.keys():
                meta_dict =  bs_bucketing_dict[meta_keyword]
                year_dict = get_subfields_sum(meta_dict=meta_dict)
                current_assets_section_year_sum[meta_keyword] = year_dict
                for year,value in year_dict.items():
                    if len(total_of_all_upper_fields)==len(list(year_dict.keys())):
                        total_of_all_upper_fields[year] = total_of_all_upper_fields[year]+value
                    else:
                        total_of_all_upper_fields[year] = value
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: get_Current_Section_fields_total")
        Logger.logr.error(f"error occured: {e}")   
    return current_assets_section_year_sum,total_of_all_upper_fields

def get_Non_Current_Section_fields_total(bs_bucketing_dict):
    meta_keywords = ["nca_gross_ppe","nca_accumulated_depreciation","nca_other_tangible_assets","nca_goodwill","nca_intangible_assets","nca_investments","nca_deffered_charges"]
    current_assets_section_year_sum = {}
    total_of_all_upper_fields = {}
    try:
        for meta_keyword in meta_keywords:
            if meta_keyword in bs_bucketing_dict.keys():
                meta_dict =  bs_bucketing_dict[meta_keyword]
                year_dict = get_subfields_sum(meta_dict=meta_dict)
                current_assets_section_year_sum[meta_keyword] = year_dict
                for year,value in year_dict.items():
                    if len(total_of_all_upper_fields)==len(list(year_dict.keys())):
                        if meta_keyword != "nca_accumulated_depreciation":
                            total_of_all_upper_fields[year] = total_of_all_upper_fields[year]+value
                        else:
                            total_of_all_upper_fields[year] = total_of_all_upper_fields[year]-abs(value)
                    else:
                        if meta_keyword != "nca_accumulated_depreciation":
                            total_of_all_upper_fields[year] = value
                        else:
                            total_of_all_upper_fields[year] = - abs(value)
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: get_Non_Current_Section_fields_total")
        Logger.logr.error(f"error occured: {e}")   
    return current_assets_section_year_sum,total_of_all_upper_fields



def get_Current_liabilities_Section_fields_total(bs_bucketing_dict):
    meta_keywords = ["cl_short_term_debt","cl_long_term_debt_due_in_year","cl_note_payable_debt","cl_accounts_payable","cl_accrued_expenses","cl_tax_payable"]
    current_assets_section_year_sum = {}
    total_of_all_upper_fields = {}
    try:
        for meta_keyword in meta_keywords:
            if meta_keyword in bs_bucketing_dict.keys():
                meta_dict =  bs_bucketing_dict[meta_keyword]
                year_dict = get_subfields_sum(meta_dict=meta_dict)
                current_assets_section_year_sum[meta_keyword] = year_dict
                for year,value in year_dict.items():
                    if len(total_of_all_upper_fields)==len(list(year_dict.keys())):
                        total_of_all_upper_fields[year] = total_of_all_upper_fields[year]+value
                    else:
                        total_of_all_upper_fields[year] = value
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: get_Current_liabilities_Section_fields_total")
        Logger.logr.error(f"error occured: {e}")   
    return current_assets_section_year_sum,total_of_all_upper_fields


def get_non_Current_liabilities_Section_fields_total(bs_bucketing_dict):
    meta_keywords = ["ncl_long_term_debt","ncl_long_term_borrowing","ncl_bond","ncl_suboardinate_debt","ncl_deferred_taxes","ncl_other_long_term_liabilities","ncl_minority_interest"]
    current_assets_section_year_sum = {}
    total_of_all_upper_fields = {}
    try:
        for meta_keyword in meta_keywords:
            if meta_keyword in bs_bucketing_dict.keys():
                meta_dict =  bs_bucketing_dict[meta_keyword]
                year_dict = get_subfields_sum(meta_dict=meta_dict)
                current_assets_section_year_sum[meta_keyword] = year_dict
                for year,value in year_dict.items():
                    if len(total_of_all_upper_fields)==len(list(year_dict.keys())):
                        total_of_all_upper_fields[year] = total_of_all_upper_fields[year]+value
                    else:
                        total_of_all_upper_fields[year] = value
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: get_non_Current_liabilities_Section_fields_total")
        Logger.logr.error(f"error occured: {e}")   
    return current_assets_section_year_sum,total_of_all_upper_fields



def get_Equity_Section_fields_total(bs_bucketing_dict):
    meta_keywords = ["eqt_common_stock","eqt_additional_paid_in_capital","eqt_retained_earnings","eqt_others","eqt_shareholder_equity"]
    current_assets_section_year_sum = {}
    total_of_all_upper_fields = {}
    try:
        for meta_keyword in meta_keywords:
            if meta_keyword in bs_bucketing_dict.keys():
                meta_dict =  bs_bucketing_dict[meta_keyword]
                # print(meta_keyword)
                # print(f"meta_dict={meta_dict}")
                year_dict = get_subfields_sum(meta_dict=meta_dict)
                # print(f"year_dict={year_dict}")
                current_assets_section_year_sum[meta_keyword] = year_dict
                for year,value in year_dict.items():
                    if len(total_of_all_upper_fields)==len(list(year_dict.keys())):
                        total_of_all_upper_fields[year] = total_of_all_upper_fields[year]+value
                    else:
                        total_of_all_upper_fields[year] = value
                # print(f"total_of_all_upper_fields={total_of_all_upper_fields}")
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: get_Equity_Section_fields_total")
        Logger.logr.error(f"error occured: {e}")   
    return current_assets_section_year_sum,total_of_all_upper_fields

# def get_Noncurrent_Section_fields_total(bs_bucketing_dict

# def formulas():
#     ca_total_current_assets = ca_cash_and_cash_equivalents + ca_account_receivables + ca_inventories + ca_prepaid_expenses
#     nca_total_non_current_assets = nca_gross_ppe -  nca_accumulated_depreciation + nca_other_tangible_assets + nca_goodwill + nca_intangible_assets + nca_investments + nca_deffered_charges




def calculate_other_current_assets(total_current_assets_df_main_page,bs_bucketing_dict,other_current_assets_meta_dict):
    ## get total current assets
    ##
    try:
        main_page_total_year_sum = get_toal_current_assets(df=total_current_assets_df_main_page)
        current_assets_section_year_sum,total_of_all_upper_fields = get_Current_Section_fields_total(bs_bucketing_dict)
        other_current_year_dict = get_subfields_sum(meta_dict=other_current_assets_meta_dict)
        balanced_amount = {}
        year_list = []
        year_list = list(other_current_year_dict.keys())
        if len(year_list)==0:
            year_list = list(total_of_all_upper_fields.keys())
        for year in year_list:
            balance_val = main_page_total_year_sum[year] - ( total_of_all_upper_fields[year] + other_current_year_dict[year])
            balanced_amount[year] = balance_val
            ### below code adds value only if it is positive : commenting till further confirmation
            # if balance_val > 0:
            #     balanced_amount[year] = balance_val
            # else:
            #     balanced_amount[year] = 0.0
            
        
        add_row = {'line_item':'Other current asset *'}
        for year,value in balanced_amount.items():
            add_row[year]= value
        
        nt_df = other_current_assets_meta_dict['notes_horizontal_table_df']
        if len(nt_df) > 0:
            nt_df = nt_df.append(add_row,ignore_index=True)
        else:
            nt_df = pd.DataFrame(add_row,index=[0])
        other_current_assets_meta_dict['notes_horizontal_table_df'] = nt_df
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: calculate_other_current_assets")
        Logger.logr.error(f"error occured: {e}")   
    return other_current_assets_meta_dict



def calculate_other_non_current_assets(total_current_assets_df_main_page,bs_bucketing_dict,other_current_assets_meta_dict):
    ## get total current assets
    ##
    try:
        main_page_total_year_sum = get_toal_current_assets(df=total_current_assets_df_main_page)
        current_assets_section_year_sum,total_of_all_upper_fields = get_Non_Current_Section_fields_total(bs_bucketing_dict)
        other_current_year_dict = get_subfields_sum(meta_dict=other_current_assets_meta_dict)
        balanced_amount = {}
        year_list = []
        year_list = list(other_current_year_dict.keys())
        if len(year_list)==0:
            year_list = list(total_of_all_upper_fields.keys())
        for year in year_list:
            balance_val = main_page_total_year_sum[year] - ( total_of_all_upper_fields[year] + other_current_year_dict[year])
            balanced_amount[year] = balance_val
            # if balance_val > 0:
            #     balanced_amount[year] = balance_val
            # else:
            #     balanced_amount[year] = 0.0
            
        add_row = {'line_item':'Other non-current asset *'}
        for year,value in balanced_amount.items():
            add_row[year]= value
        
        nt_df = other_current_assets_meta_dict['notes_horizontal_table_df']
        if len(nt_df) > 0:
            nt_df = nt_df.append(add_row,ignore_index=True)
        else:
            nt_df = pd.DataFrame(add_row,index=[0])
        other_current_assets_meta_dict['notes_horizontal_table_df'] = nt_df

    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: calculate_other_non_current_assets")
        Logger.logr.error(f"error occured: {e}")   
    return other_current_assets_meta_dict


def calculate_other_current_liabilities(total_current_assets_df_main_page,bs_bucketing_dict,other_current_assets_meta_dict):
    ## get total current assets
    ##
    try:
        main_page_total_year_sum = get_toal_current_assets(df=total_current_assets_df_main_page)
        current_assets_section_year_sum,total_of_all_upper_fields = get_Current_liabilities_Section_fields_total(bs_bucketing_dict)
        other_current_year_dict = get_subfields_sum(meta_dict=other_current_assets_meta_dict)
        balanced_amount = {}
        year_list = []
        year_list = list(other_current_year_dict.keys())
        if len(year_list)==0:
            year_list = list(total_of_all_upper_fields.keys())
        for year in year_list:
            balance_val = main_page_total_year_sum[year] - ( total_of_all_upper_fields[year] + other_current_year_dict[year])
            balanced_amount[year] = balance_val
            # if balance_val > 0:
            #     balanced_amount[year] = balance_val
            # else:
            #     balanced_amount[year] = 0.0
            
        
        add_row = {'line_item':'Other current liabilities *'}
        for year,value in balanced_amount.items():
            add_row[year]= value
        
        nt_df = other_current_assets_meta_dict['notes_horizontal_table_df']
        if len(nt_df) > 0:
            nt_df = nt_df.append(add_row,ignore_index=True)
        else:
            nt_df = pd.DataFrame(add_row,index=[0])
        other_current_assets_meta_dict['notes_horizontal_table_df'] = nt_df

    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: calculate_other_current_liabilities")
        Logger.logr.error(f"error occured: {e}")   

    return other_current_assets_meta_dict

def calculate_other_non_current_liabilities(total_current_assets_df_main_page,bs_bucketing_dict,other_current_assets_meta_dict):
    ## get total current assets
    ##
    try:
        main_page_total_year_sum = get_toal_current_assets(df=total_current_assets_df_main_page)
        current_assets_section_year_sum,total_of_all_upper_fields = get_non_Current_liabilities_Section_fields_total(bs_bucketing_dict)
        other_current_year_dict = get_subfields_sum(meta_dict=other_current_assets_meta_dict)
        balanced_amount = {}
        year_list = []
        year_list = list(other_current_year_dict.keys())
        if len(year_list)==0:
            year_list = list(total_of_all_upper_fields.keys())
        for year in year_list:
            balance_val = main_page_total_year_sum[year] - ( total_of_all_upper_fields[year] + other_current_year_dict[year])
            balanced_amount[year] = balance_val
            # if balance_val > 0:
            #     balanced_amount[year] = balance_val
            # else:
            #     balanced_amount[year] = 0.0
            
        
        add_row = {'line_item':'Other non-current liabilities *'}
        for year,value in balanced_amount.items():
            add_row[year]= value
        
        nt_df = other_current_assets_meta_dict['notes_horizontal_table_df']
        if len(nt_df) > 0:
            nt_df = nt_df.append(add_row,ignore_index=True)
        else:
            nt_df = pd.DataFrame(add_row,index=[0])
        other_current_assets_meta_dict['notes_horizontal_table_df'] = nt_df

    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: calculate_other_non_current_liabilities")
        Logger.logr.error(f"error occured: {e}")   
    return other_current_assets_meta_dict


def calculate_other_Reserves_equity(total_current_assets_df_main_page,bs_bucketing_dict,other_current_assets_meta_dict):
    ## get total current assets
    ##
    try:
        main_page_total_year_sum = get_toal_current_assets(df=total_current_assets_df_main_page)
        current_assets_section_year_sum,total_of_all_upper_fields = get_Equity_Section_fields_total(bs_bucketing_dict)
        other_current_year_dict = get_subfields_sum(meta_dict=other_current_assets_meta_dict)
        balanced_amount = {}
        year_list = []
        year_list = list(other_current_year_dict.keys())
        if len(year_list)==0:
            year_list = list(total_of_all_upper_fields.keys())
        # print(f"main_page_total_year_sum = {main_page_total_year_sum}")
        # print(f"total_of_all_upper_fields={total_of_all_upper_fields}")
        # print(f"other_current_year_dict = {other_current_year_dict}")
        for year in year_list:
            balance_val = main_page_total_year_sum[year] - ( total_of_all_upper_fields[year] + other_current_year_dict[year])
            balanced_amount[year] = balance_val
            # if balance_val > 0:
            #     balanced_amount[year] = balance_val
            # else:
            #     balanced_amount[year] = 0.0
            
        # print(f"balanced_amount={balanced_amount}")
        add_row = {'line_item':'Other Reserves *'}
        for year,value in balanced_amount.items():
            add_row[year]= value
        
        nt_df = other_current_assets_meta_dict['notes_horizontal_table_df']
        if len(nt_df) > 0:
            nt_df = nt_df.append(add_row,ignore_index=True)
        else:
            nt_df = pd.DataFrame(add_row,index=[0])
        other_current_assets_meta_dict['notes_horizontal_table_df'] = nt_df
    except Exception as e:
        from ..logging_module.logging_wrapper import Logger
        Logger.logr.debug("module: keyword_mapping , File:BSDataBucketingUtils.py,  function: calculate_other_Reserves_equity")
        Logger.logr.error(f"error occured: {e}")  
    return other_current_assets_meta_dict
# def calculate_other_noncurrent_assets(total_noncurrent_assets_df_main_page,bs_bucketing_dict,other_noncurrent_assets_meta_dict):
   
    


# def calculate_other_noncurrent_assets(total_noncurrent_assets_df_    





def find_notes_found_line_items_from_hrzntl_df(temp_dict):
    ## find line items from standardized notes df where notes found for main page line items
    main_page_note_found_particulars = temp_dict['main_page_notes_found_main_page_particular']
    main_note_account_mapping_dict = temp_dict['main_note_account_mapping_dict']
    notes_list = []
    for particulars in main_page_note_found_particulars:
        note = str(main_note_account_mapping_dict.get(particulars))
        notes_list.append(note)
    standardized_hrzntl_df = temp_dict['notes_horizontal_table_df']
    standardized_hrzntl_df.reset_index(drop=True,inplace=True)
    include_indices = []
    for idx,row in standardized_hrzntl_df.iterrows():
        try:
            if str(row['Note']) in notes_list:
                include_indices.append(idx)
        except:
            pass
    standardized_hrzntl_df = standardized_hrzntl_df.iloc[include_indices]
    temp_dict['notes_horizontal_table_df'] = standardized_hrzntl_df
    return temp_dict


def remove_notes_not_found_line_items_from_hrzntl_df(temp_dict):
    ## find and remove line items from standardized notes df where notes not found for main page line items
    main_page_note_not_found_particulars = temp_dict['main_page_notes_notfound_main_page_particular']
    main_note_account_mapping_dict = temp_dict['main_note_account_mapping_dict']
    notes_list = []
    for particulars in main_page_note_not_found_particulars:
        note = str(main_note_account_mapping_dict.get(particulars))
        notes_list.append(note)
    standardized_hrzntl_df = temp_dict['notes_horizontal_table_df']
    standardized_hrzntl_df.reset_index(drop=True,inplace=True)
    include_indices = []
    for idx,row in standardized_hrzntl_df.iterrows():
        try:
            if str(row['line_item']) in main_page_note_not_found_particulars:
                include_indices.append(idx)
        except:
            pass
    standardized_hrzntl_df = standardized_hrzntl_df.iloc[~standardized_hrzntl_df.index.isin(include_indices)]
    temp_dict['notes_horizontal_table_df'] = standardized_hrzntl_df
    return temp_dict




def handle_deffred_charges_deffered_taxes(temp_dict):
    ## take only main page value and ignore note values
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
        new_horizontal_note_df = pd.DataFrame(columns=col_list)
        for idx,row in main_page_df.iterrows():
            tmp_df = dict.fromkeys(col_list)
            tmp_df["line_item"] = row["Particulars"]
            if 'Notes' in main_dfcols:
                tmp_df["Note"] = row["Notes"]
            else:
                tmp_df["Note"] = ""
            for year in years:
                tmp_df[year] = row[year]
        # print(f"tmp_df={tmp_df}")
            new_horizontal_note_df = new_horizontal_note_df.append(tmp_df, ignore_index=True)
            
        temp_dict["notes_horizontal_table_df"] = new_horizontal_note_df
        
    return temp_dict