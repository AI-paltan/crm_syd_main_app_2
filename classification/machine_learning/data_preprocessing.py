from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import re
from ...logging_module.logging_wrapper import Logger

class dataPreprocessing:
    def __init__(self) -> None:
        # self.text:str = raw_text
        self.processed_data:str = ''

    def data_preprocessing(self,raw_text) -> str:
        Logger.logr.debug("module: Classification_service , submodule: machine_learning, File:data_preprocessing.py,  function: data_preprocessing")
        corpus = ''
        ignore_words_list = ['other', 'during', 'after', 'before']
        list_stopwords = stopwords.words('english')
        list_stopwords = [e for e in list_stopwords if e not in ignore_words_list]
        # for i in range(0, len(self.text)):
        data_input = re.sub('[^a-zA-Z]', ' ', raw_text)
        data_input = data_input.lower()
        data_input = data_input.split()
        ps = PorterStemmer()
        data_input = [ps.stem(word) for word in data_input
                    if not word in set(list_stopwords)]
        data_input = ' '.join(data_input)
        corpus = data_input
        Logger.logr.debug("data_preprocessing function completed")
        return corpus