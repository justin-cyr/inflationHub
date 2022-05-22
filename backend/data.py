import datetime
import os
import requests
import pandas as pd
from xml.etree import ElementTree

# get logger from current_app instance
from flask import current_app as app

from .utils import Date

# Read DataConfig.csv
DATA_CONFIG = pd.read_csv(
                os.path.join(os.getcwd(), 'backend/DataConfig.csv'),
                index_col='Name',
                keep_default_na=False
            ).to_dict(orient='index')

# Flag icon folcer
FLAG_FOLDER = os.path.join(os.getcwd(), 'backend/flag_icons')

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
            self.data_getter = DataGetter(self.name)
        else:
            raise Exception('DataAPI(\'' + name + '\') - unrecognized Getter: ' + data_getter)

        data_parser = data_config.get('Parser')
        if not data_parser:
            self.data_parser = Parser()
        elif data_parser == 'TimeSeriesCsvParser':
            self.data_parser = TimeSeriesCsvParser(self.name)
        elif data_parser == 'TimeSeriesCnbcJsonParser':
            self.data_parser = TimeSeriesCnbcJsonParser(self.name)
        elif data_parser == 'TimeSeriesStatCanXmlParser':
            self.data_parser = TimeSeriesStatCanXmlParser(self.name)
        else:
            raise Exception('DataAPI(\'' + name + '\') - unrecognized Parser: ' + data_parser)


    def __repr__(self):
        return str(self.__dict__)


    def url_query(self):
        if self.query_params:
            return self.url + '?' + '&'.join(self.query_params)
        else:
            return self.url

    
    def get_and_parse_data(self):
        try:
            response = self.data_getter.get(self.url_query())
        except Exception as e:
            app.logger.error('DataAPI(\'' + self.name + '\').get_and_parse_data failed to get data: ' + str(e))
            return dict(errors=str(e))

        try:
            parsed_data = self.data_parser.parse(response)
        except Exception as e:
            app.logger.error('DataAPI(\'' + self.name + '\').get_and_parse_data failed to parse data: ' + str(e))
            return dict(errors=str(e))

        return dict(data=parsed_data)
        

class DataGetter(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'DataGetter(\'' + self.name + '\')'

    def get(self, url):
        """Default implementation: make GET request to url and return response as text."""
        app.logger.info('DataAPI(\'' + self.name + '\') making request GET ' + url)
        response = requests.get(url)
        return response


class Parser(object):

    def parse(self, data):
        """Default implementation: do nothing."""
        if isinstance(data, requests.Response):
            return data.text
        else:
            return str(data)

    
    def validate_response(self, response, fmt='*'):
        """Ensure response has correct python type, successful status code and expected format."""
        if not isinstance(response, requests.Response):
            raise Exception('Parser.validate_response - invalid response type ' + str(type(response))
                            + ' type must be requests.Response.')
        
        if response.status_code != 200:
            # Raise HTTPError for this status code
            response.raise_for_status()

        # check format
        content_type = response.headers.get('Content-Type')
        if content_type:
            s = str(content_type).split('/')
            if len(s) > 1:
                content_type_format = s[1]

                if fmt == 'json':
                    if content_type_format[:4] != fmt:
                        raise Exception('Parser.validate_response - expected Content-Type json but got ' + content_type_format)

    def standard_date_str(self, date_str):
        """Return the yyyy-mm-dd format of this state string if it can be inferred.
            Use 1st of the month if day is not provided.
        """
        try:
            return str(Date(date_str))
        except TypeError:
            return None

    def chop_quotes(self, s):
        """Return s without quotes if it has any leading or trailing quotes."""
        quote_chars = ['"', "'"]
        if s and s[0] in quote_chars:
            s = s[1:]
        if s and s[-1] in quote_chars:
            s = s[:-1]
        return s


class TimeSeriesCsvParser(Parser):
    def __init__(self, value_col_name='Value', date_col_name='Date'):
        self.value_col_name = value_col_name
        self.date_col_name = date_col_name

    def __repr__(self):
        return 'TimeSeriesCsvParser(' + str(self.__dict__) + ')'

    def parse(self, response):
        """Handle response as CSV and return data as {date_col_name:[...], value_col_name:[...]}
            dates: yyyy-mm-dd format
            values: float
        """
        self.validate_response(response)
        dates = []
        values = []
        line_generator = response.iter_lines()
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if len(decoded_line) < 2:
                continue
            d = self.chop_quotes(decoded_line[0])
            v = self.chop_quotes(decoded_line[1])
            date_str = self.standard_date_str(d)
            if not date_str:
                continue
            dates.append(date_str)
            values.append(float(v))

        return {self.date_col_name: dates,
                self.value_col_name: values}


class TimeSeriesCnbcJsonParser(Parser):
    """Parser for CNBC quotes JSON data."""
    def __init__(self, value_col_name='Value', date_col_name='Date'):
        self.value_col_name = value_col_name
        self.date_col_name = date_col_name

    def __repr__(self):
        return 'TimeSeriesCnbcJsonParser(' + str(self.__dict__) + ')'

    def parse(self, response):
        """Hande response as JSON data and return data as {date_col_name:[...], value_col_name:[...]}
            dates: yyyy-mm-dd format
            values: float
        """
        self.validate_response(response, fmt='json')
        response_data = response.json()
        time_series = response_data['barData']['priceBars']
        dates = []
        values = []
        for record in time_series:
            d = record['tradeTime'][:8]
            v = record['close']
            date_str = self.standard_date_str(d)
            if not date_str:
                continue
            dates.append(date_str)
            values.append(float(v))

        return {self.date_col_name: dates,
                self.value_col_name: values}

class TimeSeriesStatCanXmlParser(Parser):
    """Parser for time series from Statistics Canada."""
    def __init__(self, value_col_name='Value', date_col_name='Date'):
        self.value_col_name = value_col_name
        self.date_col_name = date_col_name

    def __repr__(self):
        return 'TimeSeriesStatCanXmlParser(' + str(self.__dict__) + ')'

    def parse(self, response):
        """Hande response as JSON data and return data as {date_col_name:[...], value_col_name:[...]}
            dates: yyyy-mm-dd format
            values: float
        """
        self.validate_response(response)
        root = ElementTree.fromstring(response.text)
        dates = []
        values = []
        for record in root[1][0]:
            d = record.get('TIME_PERIOD')
            v = record.get('OBS_VALUE')
            date_str = self.standard_date_str(d)
            if not date_str:
                continue
            dates.append(date_str)
            values.append(float(v))

        return {self.date_col_name: dates,
                self.value_col_name: values}
