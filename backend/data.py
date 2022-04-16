import os
import requests
import pandas as pd

# Read DataConfig.csv
DATA_CONFIG = pd.read_csv(
                os.path.join(os.getcwd(), 'backend/DataConfig.csv'),
                index_col='Name',
                keep_default_na=False
            ).to_dict(orient='index')
print(DATA_CONFIG)

class DataAPI(object):
    def __init__(self, name):

        if name not in DATA_CONFIG:
            raise Exception('DataAPI - Unrecognized data name ' + name)

        self.name = name
        # look up parameters from DataConfig
        data_config = DATA_CONFIG[name]
        self.label = data_config.get('Label')
        self.type = data_config.get('Type')
        self.url = data_config.get('URL')
        self.description = data_config.get('Description')
        self.icon = data_config.get('Icon')
        self.source = data_config.get('Source')
        
        query_params = []
        i = 1
        query_param_str = 'QueryParam'
        query_param_col = query_param_str + str(i)
        while (query_param_col in data_config) and data_config[query_param_col]:
            query_params.append(data_config[query_param_col])
            i += 1
            query_param_col = query_param_str + str(i)

        self.query_params = query_params
        
        # set DataGetter and Parser
        data_getter = data_config.get('Getter')
        if not data_getter:
            self.data_getter = DataGetter()

        data_parser = data_config.get('Parser')
        if not data_parser:
            self.data_parser = Parser()


    def __repr__(self):
        return str(self.__dict__)


    def url_query(self):
        return self.url + '?' + '&'.join(self.query_params)

    
    def get_and_parse_data(self):
        try:
            response = self.data_getter.get(self.url_query())
        except Exception as e:
            return dict(errors=str(e))

        try:
            parsed_data = self.data_parser.parse(response)
        except Exception as e:
            return dict(errors=str(e))

        return dict(data=parsed_data)
        

class DataGetter(object):
    def get(self, url):
        """Default implementation: make GET request to url and return response as text."""
        response = requests.get(url)
        return response


class Parser(object):
    def parse(self, data):
        """Default implementation: do nothing."""
        if isinstance(data, requests.Response):
            return data.text
        else:
            return str(data)
