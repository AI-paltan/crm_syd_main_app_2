import pandas as pd
# from flask import current_app as app
from nltk.stem import PorterStemmer
from .main_page_config import keyword_mapping_settings
# from src.modules.data_processing.DataBucketingGeneric import DataBucketingGeneric
import os
from .TechMagicFuzzy import TechMagicFuzzy
from .DataBucketingUtils import *
from .PLDataBucketingUtils import *


class ProfitLossDataBucketing():
    def __init__(self, df_datasheet, df_nlp_bucket_master,notes_ref_dict,notes_region_meta_data,standardised_cropped_dict,standard_note_meta_dict,transformed_standardised_cropped_dict,month):
        self.df_datasheet = df_datasheet
        self.df_nlp_bucket_master = df_nlp_bucket_master
        self.df_datasheet_cp = df_datasheet.copy()
        self.notes_ref_dict = notes_ref_dict
        self.notes_region_meta_data = notes_region_meta_data    
        self.standardised_cropped_dict = standardised_cropped_dict
        self.standard_note_meta_dict = standard_note_meta_dict
        self.transformed_standardised_cropped_dict = transformed_standardised_cropped_dict
        self.month = month
        self.ps = PorterStemmer()
        self.conf_score_thresh = 80
        self.years_list = []
        self.dict_notes_df = {}
        self.df_response = None
        # self.dict_notes_files = dict_notes_files
        # self.dict_notes_data_pages = {}
        # self.record_dtls = record_dtls
        self.obj_techfuzzy = TechMagicFuzzy()
        self.list_drilldown_flags = {}
        self.pl_bucketing_dict = {}


    def fetch_report(self):
        self.report_data_tuning()
        self.get_REVENUES()
        self.get_COST_OF_SALES()
        self.get_SGNA_EXPENSE()
        self.get_RENT()
        self.get_OTHER_OPR_INCOME()
        self.get_INTEREST_INCOME()
        self.get_INTEREST_EXPENSE()
        self.get_NON_OPR_INCOME_EXPENSE()
        self.get_OTHER_INCOME_EXPENSE()
        self.get_TAXES()
        self.get_MINORITY_INTEREST()
        self.get_EXTRAORDINARY_GAIN_LOSS()
        self.get_OTHERS()
        




        

    def report_data_tuning(self):
        data_column_names = self.df_datasheet.columns.values

        # ignore these columns to fetch years list
        filter_headers = ['Notes', 'Particulars', 'statement_section', 'statement_sub_section']

        # get years list
        years_list = ([int(i) for i in data_column_names if i not in filter_headers])
        years_list.sort()
        self.years_list = [str(i) for i in years_list]

    # def get_cdm_item_data_buckets(self,main_page_targat_keywords):
    #     notes_table_df = pd.DataFrame(columns=["raw_note_no","note_no","subnote_no","line_item","year","value"])
    #     main_page_data_indices = []
    #     main_page_year_total_lst = []
    #     main_page_raw_note_list = []
    #     for year in self.years_list:
    #         # print(year)
    #         main_page_best_match= get_main_page_line_items(df_datasheet=self.df_datasheet,keywords=main_page_targat_keywords,main_page_exclude_keywords,curr_year=year,obj_techfuzzy=self.obj_techfuzzy,conf_score_thresh=self.conf_score_thresh)
    #         # print(f"main_page_best_match:= {main_page_best_match}")
    #         # main_page_data_indices.append(main_page_best_match.get("data_index"))
    #         main_page_data_indices = main_page_best_match.get("data_index")
    #         main_page_year_total_lst.append(main_page_best_match.get("value"))
    #         # print(list(main_page_best_match.get("label")))
    #     # print(f"main_page_best_match:= {main_page_best_match}")
    #     filtered_standardised_tables_dict,filtered_transformed_standardised_tables_dict,raw_note_list,note_number_list,subnote_number_list,tableid_list = get_notes_tables_from_meta_dict_and_standardized_notes_dict(main_page_best_match=main_page_best_match,notes_reference_dict=self.notes_ref_dict,notes_region_meta_data=self.notes_region_meta_data,standardised_cropped_dict=self.standardised_cropped_dict,trasnformed_standardised_cropped_dict=self.transformed_standardised_cropped_dict,statement_type="cbs")
    #     # print(f"1.raw_note_list: {raw_note_list},note_number_list: {note_number_list},sbnoue: {subnote_number_list},tableid:{tableid_list}")
    #     # print(f"len of std dict {len(filtered_standardised_tables_dict)} and len of trasnformed std dict: {len(filtered_transformed_standardised_tables_dict)}")
    #     temp_df = prepare_df_for_dumping(raw_note_list,note_number_list,subnote_number_list,tableid_list,filtered_transformed_standardised_tables_dict)
    #     notes_table_df = pd.concat([notes_table_df,temp_df],ignore_index=True)
    #     main_page_raw_note_list = raw_note_list
    #         # get_notes_pages_line_items()
    #     temp_dict ={}
    #     temp_dict["main_page_row_indices"] = main_page_data_indices
    #     temp_dict["main_page_year_total"] =main_page_year_total_lst
    #     temp_dict["main_page_raw_note"] =main_page_raw_note_list
    #     temp_dict["notes_table_df"] = notes_table_df
    #     return temp_dict

    def get_cdm_item_data_buckets(self,main_page_targat_keywords,main_page_exclude_keywords,match_type,note_page_include_keywords=[],notes_page_exclude_keywords=[]):
        notes_table_df = pd.DataFrame(columns=["raw_note_no","note_no","subnote_no","line_item","year","value"])
        main_page_data_indices = []
        main_page_year_total_lst = []
        main_page_raw_note_list = []
        main_page_note_list = []
        main_page_particular_text_list = []
        main_page_value_list = []
        matched_main_page_df = []
        notes_table_df = []
        temp_horizontal_df = []
        main_page_notes_found_main_page_particular = []
        main_page_notes_notfound_main_page_particular  =[]
        remaning_temp_horizontal_df = []
        temp_hrznt_df_with_meta_data = pd.DataFrame()
        remaining_temp_hrznt_df_with_meta_data = pd.DataFrame()
        main_note_account_mapping_dict = {}
        section = ''
        subsection = ''
        try:
            self.df_datasheet = remove_total_lines_main_pages(df_datasheet=self.df_datasheet,filepath=keyword_mapping_settings.mastersheet_filter_particulars,statement_type='cpl',obj_techfuzzy=self.obj_techfuzzy)
            self.df_datasheet = self.df_datasheet.reset_index(drop=True)
            for year in self.years_list:
                # print(year)
                # main_page_best_match= get_main_page_line_items(df_datasheet=self.df_datasheet,keywords=main_page_targat_keywords,main_page_exclude_keywords,curr_year=year,obj_techfuzzy=self.obj_techfuzzy,conf_score_thresh=self.conf_score_thresh,match_type=match_type)
                main_page_best_match= get_main_page_line_items(df_datasheet=self.df_datasheet,keywords=main_page_targat_keywords,exclude_keywords=main_page_exclude_keywords,curr_year=year,obj_techfuzzy=self.obj_techfuzzy,conf_score_thresh=self.conf_score_thresh,match_type=match_type)
                # print(f"main_page_best_match:= {main_page_best_match}")
                # main_page_data_indices.append(main_page_best_match.get("data_index"))
                main_page_data_indices = main_page_best_match.get("data_index")
                main_page_year_total_lst.append(main_page_best_match.get("value"))
                main_page_particular_text_list = main_page_best_match.get("line_item_label")
                main_page_value_list.append(main_page_best_match.get("line_item_value"))
                # print(list(main_page_best_match.get("label")))
            # print(f"main_page_best_match:= {main_page_best_match}")
            filtered_standardised_tables_dict,filtered_transformed_standardised_tables_dict,raw_note_list,note_number_list,subnote_number_list,tableid_list,notes_found_main_page_particular,notes_notfound_main_page_particular,note_account_mapping_dict = get_notes_tables_from_meta_dict_and_standardized_notes_dict(main_page_best_match=main_page_best_match,notes_reference_dict=self.notes_ref_dict,notes_region_meta_data=self.notes_region_meta_data,standardised_cropped_dict=self.standardised_cropped_dict,trasnformed_standardised_cropped_dict=self.transformed_standardised_cropped_dict,section=section,subsection=subsection,statement_type="cpl")
            # print(f"1.raw_note_list: {raw_note_list},note_number_list: {note_number_list},sbnoue: {subnote_number_list},tableid:{tableid_list}")
            # print(f"len of std dict {len(filtered_standardised_tables_dict)} and len of trasnformed std dict: {len(filtered_transformed_standardised_tables_dict)}")
            # noted_dict_respnse_after_filtering_keywrods = get_notes_dfDict_after_filtering_keywords(note_number_list=note_number_list,subnote_number_list=subnote_number_list,tableid_list=tableid_list,filtered_transformed_standardised_tables_dict=filtered_transformed_standardised_tables_dict,obj_techfuzzy=self.obj_techfuzzy,conf_score=self.conf_score_thresh,match_type='partial',notes_include_keywords=note_page_include_keywords,notes_exclude_keywords=notes_page_exclude_keywords)
            # temp_df = prepare_df_for_dumping(raw_note_list,note_number_list,subnote_number_list,tableid_list,filtered_transformed_standardised_tables_dict)
            # print("new meta dict")
            # print(noted_dict_respnse_after_filtering_keywrods)
            main_page_raw_note_list = list(set(raw_note_list))
            main_page_note_list = list(set(note_number_list))
            main_note_account_mapping_dict = note_account_mapping_dict
            main_page_notes_found_main_page_particular = list(set(notes_found_main_page_particular))
            main_page_notes_notfound_main_page_particular = list(set(notes_notfound_main_page_particular))
            # print("upper mainpage: ",main_page_notes_found_main_page_particular)
            noted_dict_respnse_after_filtering_keywrods,remaining_response_notes_dict = get_notes_dfDict_after_filtering_keywords(note_number_list=note_number_list,subnote_number_list=subnote_number_list,tableid_list=tableid_list,filtered_transformed_standardised_tables_dict=filtered_transformed_standardised_tables_dict,obj_techfuzzy=self.obj_techfuzzy,conf_score=self.conf_score_thresh,match_type='partial',notes_include_keywords=note_page_include_keywords,notes_exclude_keywords=notes_page_exclude_keywords)
            # not_visited_notes_line_items_df_var = not_visited_notes_line_items_df
            temp_df,temp_horizontal_df = prepare_df_for_dumping2(raw_note_list,note_number_list,subnote_number_list,tableid_list,noted_dict_respnse_after_filtering_keywrods)
            # notes_table_df = pd.concat([notes_table_df,temp_df],ignore_index=True)
            remaining_temp_df,remaning_temp_horizontal_df = prepare_df_for_dumping2(raw_note_list,note_number_list,subnote_number_list,tableid_list,remaining_response_notes_dict)
            matched_main_page_df = get_matched_main_page_df(main_page_data_indices=main_page_data_indices,df=self.df_datasheet)

            temp_horizontal_df = include_main_page_value_if_no_notes_found(main_page_notes_notfound_main_page_particular,matched_main_page_df,temp_horizontal_df)
            
            temp_horizontal_df = postprocessing_note_df(std_hrzntl_nte_df=temp_horizontal_df)
            remaning_temp_horizontal_df = postprocessing_note_df(remaning_temp_horizontal_df)
            # temp_hrznt_df_with_meta_data = postprocessing_note_df(std_hrzntl_nte_df=temp_df)
            # remaining_temp_hrznt_df_with_meta_data = postprocessing_note_df(remaining_temp_df)
            # get_notes_pages_line_items()
        except Exception as e:
            from ..logging_module.logging_wrapper import Logger
            Logger.logr.debug("module: Keyword Mapping , File:ProfitLossDataBucketing.py,  function: get_cdm_item_data_buckets")
            Logger.logr.error(f"error occured: {e}")
            print(e)
        temp_dict ={}
        temp_dict["main_page_row_indices"] = main_page_data_indices
        temp_dict["main_page_year_total"] =main_page_year_total_lst
        temp_dict["main_page_year_list"] = self.years_list
        temp_dict["main_page_raw_note"] =main_page_raw_note_list
        temp_dict["main_page_note_number_list"] = main_page_note_list
        temp_dict["main_page_particular_text_list"] = main_page_particular_text_list
        temp_dict["main_page_value_list"] = main_page_value_list
        temp_dict["main_page_cropped_df"] = matched_main_page_df
        temp_dict["notes_table_df"] = notes_table_df
        temp_dict["notes_horizontal_table_df"] = temp_horizontal_df
        temp_dict["remaining_notes_horizontal_table_df"] = remaning_temp_horizontal_df
        # print("lower ",main_page_notes_found_main_page_particular)
        temp_dict["main_page_notes_found_main_page_particular"] = main_page_notes_found_main_page_particular
        temp_dict["main_page_notes_notfound_main_page_particular"] = main_page_notes_notfound_main_page_particular
        temp_dict["main_note_account_mapping_dict"] = main_note_account_mapping_dict
        temp_dict["temp_hrznt_df_with_meta_data"] = temp_hrznt_df_with_meta_data
        temp_dict["remaining_temp_hrznt_df_with_meta_data"] = remaining_temp_hrznt_df_with_meta_data
        return temp_dict
  


    def get_REVENUES(self):
        meta_keywrods = "smr_sales"
        print(meta_keywrods)
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)
        self.pl_bucketing_dict[meta_keywrods] = temp_dict

    def get_COST_OF_SALES(self):
        meta_keywrods = "cost_of_sales"
        print(meta_keywrods)
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)
        
        #Sanjay code
        main_pg_df = self.df_datasheet
        main_pg_cropped_df = temp_dict["main_page_cropped_df"]        
        temp_dict['main_page_cropped_df'] = cost_of_sales_additional_keyword_filter(main_pg_cropped_df, main_pg_df)
        kwds = ['finance cost']
        temp_dict = remove_specific_keywords_notes_not_found_line_items_from_hrzntl_df(temp_dict=temp_dict,keywords=kwds,obj_techfuzzy=self.obj_techfuzzy)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict

    def get_SGNA_EXPENSE(self):
        meta_keywrods = "sga_total_sga_expenses"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)
        
        self.pl_bucketing_dict[meta_keywrods] = temp_dict
    
    def get_RENT(self):
        meta_keywrods = "smr_rent"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)
        kwds = ['admin expense','administration expense','administration expense','other expense']
        temp_dict = remove_specific_keywords_notes_not_found_line_items_from_hrzntl_df(temp_dict=temp_dict,keywords=kwds,obj_techfuzzy=self.obj_techfuzzy)
        self.pl_bucketing_dict[meta_keywrods] = temp_dict

    def get_OTHER_OPR_INCOME(self):
        meta_keywrods = "smr_others_opr_income"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict

    def get_INTEREST_INCOME(self):
        meta_keywrods = "smr_interest_income"
        print(meta_keywrods)
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        # temp_dict = interest_income_filter(temp_dict=temp_dict)
        temp_dict = interest_income_expense_filter_advance(temp_dict=temp_dict,datapoint_flag="smr_interest_income")
        temp_dict = make_all_positive(temp_dict=temp_dict)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict
    
    def get_INTEREST_EXPENSE(self):
        meta_keywrods = "smr_interest_expense"
        print(meta_keywrods)
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master = self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        # temp_dict = interest_expense_filter(temp_dict=temp_dict)
        temp_dict = interest_income_expense_filter_advance(temp_dict=temp_dict,datapoint_flag="smr_interest_expense")
        temp_dict = make_all_positive(temp_dict=temp_dict)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict

    def get_NON_OPR_INCOME_EXPENSE(self):
        meta_keywrods = "noie_oi_or_exp"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict
    
    def get_OTHER_INCOME_EXPENSE(self):
        meta_keywrods = "oie_oi"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict
    
    def get_TAXES(self):
        meta_keywrods = "smr_taxes"
        # print(meta_keywrods)
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)
        # print(temp_dict["notes_horizontal_table_df"])
        temp_dict = SMR_TAXES_filter(temp_dict=temp_dict)
        self.pl_bucketing_dict[meta_keywrods] = temp_dict
    
    def get_MINORITY_INTEREST(self):
        meta_keywrods = "smr_minority_interest"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict

    def get_EXTRAORDINARY_GAIN_LOSS(self):
        meta_keywrods = "smr_extraordinary_gain_loss"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        # temp_dict = make_all_positive(temp_dict=temp_dict)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict

    def get_OTHERS(self):
        meta_keywrods = "smr_other"
        main_page_targat_keywords = get_main_page_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_notes_keywords = get_notes_pages_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        main_page_exclude_keywords = get_main_page_exclude_keywords(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        note_page_exclude_keywords = get_notes_pages_exclude_keyowrds(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        section,subsection,match_type = get_section_subsection_matchType(df_nlp_bucket_master=self.df_nlp_bucket_master,df_meta_keyword=meta_keywrods)
        temp_dict = self.get_cdm_item_data_buckets(main_page_targat_keywords,main_page_exclude_keywords,match_type=match_type,note_page_include_keywords=note_page_notes_keywords,notes_page_exclude_keywords=note_page_exclude_keywords)
        temp_dict = make_all_positive(temp_dict=temp_dict)

        self.pl_bucketing_dict[meta_keywrods] = temp_dict


  