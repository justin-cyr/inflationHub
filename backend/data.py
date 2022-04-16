import os
import pandas as pd
import numpy as np

# Read DataConfig.csv
DATA_CONFIG = pd.read_csv(os.path.join(os.getcwd(), 'backend/DataConfig.csv'), index_col='Name').to_dict(orient='index')


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
        query_param_col = key + str(i)
        while (query_param_col in data_config) and (not np.isnan(data_config[query_param_col])):
            query_params.append(data_config[query_param_col])

        self.query_params = query_params
        

    def __repr__(self):
        return str(self.__dict__)


    def url_query(self):
        return self.url + '?' + '&'.join(self.query_params)
        


