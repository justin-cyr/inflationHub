import datetime
import os
from io import BytesIO
import requests
import pandas as pd
from xml.etree import ElementTree

# get logger from current_app instance
from flask import current_app as app

from .utils import Date, DateTime

# Read DataConfig.csv
DATA_CONFIG = pd.read_csv(
                os.path.join(os.getcwd(), 'backend/DataConfig.csv'),
                index_col='Name',
                keep_default_na=False
            ).to_dict(orient='index')

# Flag icon folcer
FLAG_FOLDER = os.path.join(os.getcwd(), 'backend/flag_icons')

class DataAPI(object):
    def __init__(self, name=None, data_config=None):

        if not (name or data_config):
            raise Exception('DataAPI - requires name or data_config dict.')

        # look up data_config if name is present
        if not data_config:
            if name not in DATA_CONFIG:
                raise Exception('DataAPI - Unrecognized data name ' + name)
            else:
                data_config = DATA_CONFIG[name]

        if not name:
            if 'Name' not in data_config:
                raise Exception('DataAPI - construction from data_config must include Name key.')
            else:
                name = data_config['Name']

        self.name = name
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
        
        headers = {}
        i = 1
        header_str = 'Header'
        header_col = header_str + str(i)
        while (header_col in data_config and data_config[header_col]):
            k, v = data_config[header_col].split(':')
            headers[k] = v
            i += 1
            header_col = header_str + str(i)

        self.headers = headers

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
        elif data_parser == 'TimeSeriesCnbcIntradayCloseParser':
            self.data_parser = TimeSeriesCnbcIntradayCloseParser(self.name)
        elif data_parser == 'CnbcJsonQuoteParser':
            self.data_parser = CnbcJsonQuoteParser()           
        elif data_parser == 'IntradayUSTQuoteWsjParser':
            self.data_parser = IntradayUSTQuoteWsjParser()
        elif data_parser == 'GasPricesExcelParser':
            self.data_parser = GasPricesExcelParser()
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
            response = self.data_getter.get(self.url_query(), headers=self.headers)
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

    def get(self, url, headers={}):
        """Default implementation: make GET request to url and return response as text."""
        app.logger.info('DataAPI(\'' + self.name + '\') making request GET ' + url)
        response = requests.get(url, headers=headers)
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

    def standard_datetime_str(self, datetime_str):
        """Return the yyyy-mm-dd HH:MM:SS format of this datetime string if it can be inferred."""
        try:
            return str(DateTime(datetime_str))
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

    def chop_pct(self, s):
        s = s[:-1] if s and isinstance(s, str) and s[-1] == '%' else s
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
            try:
                values.append(float(v))
                dates.append(date_str)
            except:
                # continue if value cannot be parsed as a float
                pass

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

class TimeSeriesCnbcIntradayCloseParser(Parser):
    """Parser for CNBC quotes intraday close JSON data."""
    def __init__(self, value_col_name='Value', date_col_name='Date'):
        self.value_col_name = value_col_name
        self.date_col_name = date_col_name

    def __repr__(self):
        return 'TimeSeriesCnbcIntradayCloseParser(' + str(self.__dict__) + ')'

    def parse(self, response):
        """Hande response as JSON data and return data as {date_col_name:[...], value_col_name:[...]}
            dates: yyyy-mm-dd HH:MM:SS format
            values: float
        """
        self.validate_response(response, fmt='json')
        response_data = response.json()
        time_series = response_data['barData']['priceBars']
        dates = []
        values = []
        for record in time_series:
            d = record['tradeTime']
            v = record['close']
            date_str = self.standard_datetime_str(d)
            if not date_str:
                continue
            dates.append(date_str)
            values.append(float(v))

        return {self.date_col_name: dates,
                self.value_col_name: values}


class CnbcJsonQuoteParser(Parser):
    """Parser for CNBC quotes JSON data."""
    def __repr__(self):
        return f'{self.__class__.__name__}(' + str(self.__dict__) + ')'

    def parse(self, response):
        """Hande response as JSON data and return data as {date_col_name:[...], value_col_name:[...]}
            dates: yyyy-mm-dd format
            values: float
        """
        self.validate_response(response, fmt='json')
        response_data = response.json()
        quote_list = response_data['FormattedQuoteResult']['FormattedQuote']
        res = []

        for record in quote_list:
            yield_num = float(self.chop_pct(record.get('last')))
            coupon = float(self.chop_pct(record.get('last')))

            res.append(
                {
                    'name': record.get('name'),
                    'coupon': coupon,
                    'price': record.get('bond_last_price'),
                    'priceChange': record.get('bond_change_price'),
                    'yield': yield_num,
                    'yieldChange': record.get('change_pct'),
                    'timestamp': record.get('last_time')[:19],
                    'maturityDate': record.get('maturity_date')
                }
            )
        return res

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


class IntradayUSTQuoteWsjParser(Parser):
    """Parser for intraday quotes from Wall Street Journal bonds page."""
    def __repr__(self):
        return 'IntradayUSTQuoteWsjParser(' + str(self.__dict__) + ')'

    def parse(self, response):
        """Handle response as JSON data and return data as a list quotes."""
        self.validate_response(response, fmt='json')
        response_data = response.json()
        res = []
        if 'data' in response_data and 'instruments' in response_data['data']:
            for inst in response_data['data']['instruments']:
                if 'bond' in inst:
                    res.append(
                        {
                            'name': inst.get('formattedName'),
                            'coupon': inst['bond'].get('couponRate'),
                            'price': inst['bond'].get('tradePrice'),
                            'priceChange': inst['bond'].get('formattedTradePriceChange'),
                            'yield': inst['bond'].get('yield'),
                            'yieldChange': inst['bond'].get('yieldChange'),
                            'timestamp': inst.get('timestamp')[:19]
                        }
                    )
        return res


class ExcelParser(Parser):
    """Parser for Excel data (xlsx, xls, and any format supported by pandas.read_excel)."""
    def __init__(self, dropna=True, sheet_name=0, header=0, usecols=None):
        self.dropna = dropna
        self.sheet_name = sheet_name
        self.header = header
        self.usecols=usecols

    def __repr__(self):
        return 'ExcelParser(' + str(self.__dict__) + ')'

    def parse(self, response):
        """Save *.xls response as a temporary file, parse and return data series."""
        # response content is binary data
        io = BytesIO()
        io.write(response.content)
        df = pd.read_excel(
                io,
                sheet_name=self.sheet_name,
                header=self.header,
                usecols=self.usecols
            )
        io.close()
        if self.dropna:
            df = df.dropna()
        res = df.to_dict(orient='list')

        return res


class GasPricesExcelParser(ExcelParser):
    """Parse weekly gas prices from US Energy Information Administration."""
    def __init__(self):
        super().__init__(
            sheet_name='Data 3',
            header=2,
            usecols='A:B'
        )

    def __repr__(self):
        return 'GasPricesExcelParser(' + str(self.__dict__) + ')'

    def parse(self, response):
        res = super().parse(response)
        dates = res.get('Date')
        res['Date'] = [str(Date(str(d)[:10])) for d in dates]

        # replace key with series name
        old_key = [k for k in res.keys() if k != 'Date'][0]
        res['US Gas Prices'] = res[old_key]
        del res[old_key] 

        return res


def get_fred_data(key, name=None):
    """Get time series from St. Louis FRED data based on time series key."""
    if not name:
        name = 'FRED data ' + key
    data_config = dict(
        Name=name,
        Label=key,
        Type='Time series',
        URL='https://fred.stlouisfed.org/graph/fredgraph.csv',
        Description='FRED time series ' + key,
        Parser='TimeSeriesCsvParser',
        Source='https://fred.stlouisfed.org/series/' + key,
        QueryParam1='id=' + key
    )
    data_api = DataAPI(data_config=data_config)
    return data_api.get_and_parse_data()
