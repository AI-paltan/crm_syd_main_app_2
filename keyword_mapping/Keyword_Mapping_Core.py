from .CBS_mapping import CBSMapping
from .CPL_mapping import CPLMapping
from .CCF_mapping import CCFMapping



class KeywordMappingCore:
    def __init__(self,cbs_dict,cpl_dict,ccf_dict,notes_ref_dict,notes_region_meta_data,standardised_cropped_dict,standard_note_meta_dict,transformed_standardised_cropped_dict,month) -> None:
        self.cbs_main_page_dict = cbs_dict
        self.cpl_main_page_dict = cpl_dict
        self.ccf_main_page_dict = ccf_dict
        self.notes_ref_dict = notes_ref_dict
        self.notes_region_meta_data = notes_region_meta_data
        self.standardised_cropped_dict = standardised_cropped_dict
        self.standard_note_meta_dict = standard_note_meta_dict
        self.transformed_standardised_cropped_dict = transformed_standardised_cropped_dict
        self.month = month
        self.ccf_df_response_dict : dict = {}
        self.cbs_bucket_response_dict : dict = {}
        self.cpl_bucket_response_dict: dict = {}

    def CBS_bucketing(self):
        if len(self.cbs_main_page_dict)>0:
            for key,val in self.cbs_main_page_dict.items():
                cbs_df = val
                if not cbs_df.empty:
                    cbs_df.columns = cbs_df.columns.map(str)
                    obj_cbsMapping = CBSMapping(cbs_df=cbs_df,notes_ref_dict=self.notes_ref_dict,notes_region_meta_data=self.notes_region_meta_data,standard_note_meta_dict=self.standard_note_meta_dict,standardised_cropped_dict=self.standardised_cropped_dict,transformed_standardised_cropped_dict=self.transformed_standardised_cropped_dict,month=self.month)
                    obj_cbsMapping.trigger_job()
                    self.cbs_bucket_response_dict[key] = obj_cbsMapping.bs_bucket_dict
    
    def CPL_bucketing(self):
        if len(self.cpl_main_page_dict)>0:
            for key,val in self.cpl_main_page_dict.items():
                cpl_df = val
                if not cpl_df.empty:
                    cpl_df.columns = cpl_df.columns.map(str)
                    obj_cbsMapping = CPLMapping(cpl_df=cpl_df,notes_ref_dict=self.notes_ref_dict,notes_region_meta_data=self.notes_region_meta_data,standard_note_meta_dict=self.standard_note_meta_dict,standardised_cropped_dict=self.standardised_cropped_dict,transformed_standardised_cropped_dict=self.transformed_standardised_cropped_dict,month=self.month)
                    obj_cbsMapping.trigger_job()
                    self.cpl_bucket_response_dict[key] = obj_cbsMapping.pl_bucket_dict

    def CCF_bucketing(self):
        if len(self.ccf_main_page_dict)>0:
            for key,value in self.ccf_main_page_dict.items():
                ccf_df = value
                if not ccf_df.empty:
                    ccf_df.columns = ccf_df.columns.map(str)
                    obj_ccfmapping = CCFMapping(ccf_df=ccf_df)
                    obj_ccfmapping.trigger_job()
                    self.ccf_df_response_dict[key] = obj_ccfmapping.df_response
