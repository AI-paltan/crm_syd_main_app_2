from .analyzer import build_analyzer
import pandas as pd

analyzer = build_analyzer()



class TableExtract():
    def __init__(self) -> None:
        self.page = ''
        self.table_dict :dict = {}


    def process_page(self,file):
        df = analyzer.analyze(path=file)
        df.reset_state()
        self.page = next(iter(df))
        for tid, table in enumerate(self.page.tables):
            try:
                df_list = pd.read_html(table.html)
                dfx = df_list[0]
                self.table_dict[tid] = dfx
            except:
                pass
        return self.table_dict, self.page
