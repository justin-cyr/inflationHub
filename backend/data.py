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
        self.cache = data_config.get('Cache', True)
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
            k = data_config[header_col].split(':')[0]
            v = data_config[header_col][len(k) + 1:]
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
        elif data_parser == 'CnbcJsonQuoteParser':
            self.data_parser = CnbcJsonQuoteParser()           
        elif data_parser == 'IntradayUSTQuoteWsjParser':
            self.data_parser = IntradayUSTQuoteWsjParser()
        elif data_parser == 'MarketWatchBondQuoteParser':
            self.data_parser = MarketWatchBondQuoteParser()
        elif data_parser == 'CmeTsyQuoteJsonParser':
            self.data_parser = CmeTsyQuoteJsonParser()
        elif data_parser == 'CmeFuturesQuoteJsonParser':
            self.data_parser = CmeFuturesQuoteJsonParser(self.name)
        elif data_parser == 'ErisFuturesCsvParser':
            self.data_parser = ErisFuturesCsvParser()
        elif data_parser == 'TimeSeriesCsvParser':
            self.data_parser = TimeSeriesCsvParser(self.name)
        elif data_parser == 'TimeSeriesCnbcJsonParser':
            self.data_parser = TimeSeriesCnbcJsonParser(self.name)
        elif data_parser == 'TimeSeriesCnbcIntradayCloseParser':
            self.data_parser = TimeSeriesCnbcIntradayCloseParser(self.name)
        elif data_parser == 'TimeSeriesSPIndexJsonParser':
            self.data_parser = TimeSeriesSPIndexJsonParser(self.name)
        elif data_parser == 'ErisIntradayCurveCsvParser':
            self.data_parser = ErisIntradayCurveCsvParser(self.name)
        elif data_parser == 'ErisEodCurveCsvParser':
            self.data_parser = ErisEodCurveCsvParser(self.query_params[0], self.name)
        elif data_parser == 'TwHtmlUSTYieldParser':
            self.data_parser = TwHtmlUSTYieldParser()
        elif data_parser == 'ErisSwapRateCsvParser':
            self.data_parser = ErisSwapRateCsvParser()
        elif data_parser == 'QuikStrikeCtdOtrParser':
            self.data_parser = QuikStrikeCtdOtrParser()
        elif data_parser == 'QuikStrikeFedWatchParser':
            self.data_parser = QuikStrikeFedWatchParser()
        elif data_parser == 'YahooQuoteJsonParser':
            self.data_parser = YahooQuoteJsonParser()
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

    standard_name_map = {
    # US Treasuries
        ####
        # CNBC
        'U.S. 1 Month Treasury': 'US 1M',
        'U.S. 2 Month Treasury': 'US 2M',
        'U.S. 3 Month Treasury': 'US 3M',
        'U.S. 4 Month Treasury': 'US 4M',
        'U.S. 6 Month Treasury': 'US 6M',
        'U.S. 1 Year Treasury':  'US 1Y',
        'U.S. 2 Year Treasury':  'US 2Y',
        'U.S. 3 Year Treasury':  'US 3Y',
        'U.S. 5 Year Treasury':  'US 5Y',
        'U.S. 7 Year Treasury':  'US 7Y',
        'U.S. 10 Year Treasury': 'US 10Y',
        'U.S. 20 Year Treasury': 'US 20Y',
        'U.S. 30 Year Treasury': 'US 30Y',
        ####
        # WSJ
        '1-Month Bill': 'US 1M',
        '3-Month Bill': 'US 3M',
        '6-Month Bill': 'US 6M',
        '1-Year Bill':  'US 1Y',
        '2-Year Note':  'US 2Y',
        '3-Year Note':  'US 3Y',
        '5-Year Note':  'US 5Y',
        '7-Year Note':  'US 7Y',
        '10-Year Note': 'US 10Y',
        '20-Year Bond': 'US 20Y',
        '30-Year Bond': 'US 30Y',
        ####
        # MarketWatch
        'U.S. 1 Month Treasury Bill': 'US 1M',
        'U.S. 3 Month Treasury Bill': 'US 3M',
        'U.S. 6 Month Treasury Bill': 'US 6M',
        'U.S. 1 Year Treasury Bill':  'US 1Y',
        'U.S. 2 Year Treasury Note':  'US 2Y',
        'U.S. 3 Year Treasury Note':  'US 3Y',
        'U.S. 5 Year Treasury Note':  'US 5Y',
        'U.S. 7 Year Treasury Note':  'US 7Y',
        'U.S. 10 Year Treasury Note': 'US 10Y',
        'U.S. 20 Year Treasury Bond': 'US 20Y',
        'U.S. 30 Year Treasury Bond': 'US 30Y',
        ####
        # CME BrokerTec
        'UB02': 'US 2Y',
        'UB03': 'US 3Y',
        'UB05': 'US 5Y',
        'UB07': 'US 7Y',
        'UB10': 'US 10Y',
        'UB20': 'US 20Y',
        'UB30': 'US 30Y',
    # TIPS
        # CNBC
        'UST 5-Yr. TIPS':    'TIPS 5Y',
        'U.S. 5 Year TIPS':  'TIPS 5Y',
        'U.S. 10 Year TIPS': 'TIPS 10Y',
        'U.S. 30 Year TIPS': 'TIPS 30Y',
    # Bond futures
        # CME code to BBG code
        'ZT': 'TU',
        'Z3N': '3Y',
        'ZF': 'FV',
        'ZN': 'TY',
        'TN': 'UXY',
        'TWE': 'TWE',
        'ZB': 'US',
        'UB': 'WN',
        'UL': 'WN',
    # IR Futures
        'SR3': 'SFR',
        'SR1': 'SER',
        'ZQ': 'FF'
    }

    cme_month_map = {
        'F': 'JAN',
        'G': 'FEB',
        'H': 'MAR',
        'J': 'APR',
        'K': 'MAY',
        'M': 'JUN',
        'N': 'JUL',
        'Q': 'AUG',
        'U': 'SEP',
        'V': 'OCT',
        'X': 'NOV',
        'Z': 'DEC'
    }

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

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

    def current_time_as_str(self):
        """Return the yyyy-mm-dd HH:MM:SS format of the current timestamp."""
        return self.standard_datetime_str(datetime.datetime.now())

    def chop_quotes(self, s):
        """Return s without quotes if it has any leading or trailing quotes."""
        quote_chars = ['"', "'"]
        if s and s[0] in quote_chars:
            s = s[1:]
        if s and s[-1] in quote_chars:
            s = s[:-1]
        return s
    
    def to_float(self, num, err_str='-'):
        """Return float(num) if num represents a number, else return err_str."""
        if num.replace('.', '0').isnumeric():
            return float(num)
        else:
            return err_str

    def mixed_number_to_float(self, num, err_str='-'):
        """Return float(num) if num represents a mixed number, else return err_str."""
        try:
            space_split = num.split(' ')
            int_part = float(space_split[0])
            dec_part = 0.0
            if len(space_split) > 1:
                div_split = space_split[1].split('/')
                if len(div_split) != 2:
                    return err_str
                dec_part = float(div_split[0]) / float(div_split[1])
            return int_part + dec_part
        except:
            return err_str

    def chop_pct(self, s):
        s = s[:-1] if s and isinstance(s, str) and s[-1] == '%' else s
        return s
    
    def cme_ticker_to_bbg_ticker(self, ticker):
        """Return the BBG ticker for this CME ticker."""
        month_code = ticker[-2:]
        product_code = ticker[:-2]
        bbg_ticker = Parser.standard_name_map.get(
            product_code, product_code) + month_code
        return bbg_ticker

    @staticmethod
    def standard_name(name):
        """Return the standard name of this quote used in this app."""
        return Parser.standard_name_map.get(name, '')
    
    @staticmethod
    def futures_code_to_expiration_month(ticker):
        """Return the MMM YYYY expiration month for a CME futures ticker."""
        code = ticker[-2:].upper()
        month = Parser.cme_month_map.get(code[0], '')
        year = str(2020 + int(code[-1]))
        return f'{month} {year}'


class TimeSeriesCsvParser(Parser):
    def __init__(self, value_col_name='Value', date_col_name='Date'):
        self.value_col_name = value_col_name
        self.date_col_name = date_col_name

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
            try:
                name = record.get('name')
                last = float(self.chop_pct(record.get('last')))
                change_pct = record.get('change_pct')
                last_time = record.get('last_time', '')[:19]

                quote_type = record.get('type')
                if quote_type == 'BOND':
                    yield_num = last
                    coupon = float(self.chop_pct(record.get('coupon')))
                    standard_name = Parser.standard_name(name)

                    res.append(
                        {
                            'standardName': standard_name,
                            'name': name,
                            'coupon': coupon,
                            'price': record.get('bond_last_price'),
                            'priceChange': record.get('bond_change_price'),
                            'yield': yield_num,
                            'yieldChange': change_pct,
                            'timestamp': last_time,
                            'maturityDate': record.get('maturity_date')
                        }
                    )

                elif quote_type == 'STOCK':
                    symbol = record.get('symbol')

                    res.append(
                        {
                            'standardName': symbol,
                            'name': name,
                            'price': last,
                            'priceChange': change_pct,
                            'volume': record.get('volume_alt'),
                            'timestamp': last_time
                        }
                    )

                else:
                    raise NotImplementedError(f'Unsupported quote type {quote_type}')

            except Exception as e:
                app.logger.error(f'{__class__.__name__}: failed to parse {record}\n\t\tReason: {e}')
        return res


class TimeSeriesSPIndexJsonParser(Parser):
    """Parser for index time series data from S&P Global."""
    def __init__(self, value_col_name='Value', date_col_name='Date'):
        self.value_col_name = value_col_name
        self.date_col_name = date_col_name

    def parse(self, response):
        """Hande response as JSON data and return data as {date_col_name:[...], value_col_name:[...]}
            dates: yyyy-mm-dd format
            values: float
        """
        self.validate_response(response)
        response_data = response.json()
        time_series = response_data['indexLevelsHolder']['indexLevels']
        dates = []
        values = []
        for record in time_series:
            d = record['formattedEffectiveDate']
            v = record['indexValue']
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
    def parse(self, response):
        """Handle response as JSON data and return data as a list quotes."""
        self.validate_response(response, fmt='json')
        response_data = response.json()
        res = []
        if 'data' in response_data and 'instruments' in response_data['data']:
            for inst in response_data['data']['instruments']:
                try:
                    if 'bond' in inst:
                        name = inst.get('formattedName')
                        standard_name = Parser.standard_name(name)
                        res.append(
                            {
                                'standardName': standard_name,
                                'name': name,
                                'coupon': inst['bond'].get('couponRate'),
                                'price': inst['bond'].get('tradePrice'),
                                'priceChange': inst['bond'].get('formattedTradePriceChange'),
                                'yield': inst['bond'].get('yield'),
                                'yieldChange': inst['bond'].get('yieldChange'),
                                'timestamp': inst.get('timestamp')[:19]
                            }
                        )
                except Exception as e:
                    app.logger.error(f'{__class__.__name__}: failed to parse {inst}\n\t\tReason: {e}')
        return res


class CmeTsyQuoteJsonParser(Parser):
    """Parser for intraday CME BrokerTec US Treasury note and bond quotes."""
    def parse(self, response):
        self.validate_response(response)
        response_data = response.json()
        res = []

        for q in response_data:
            try:
                name =  q.get('asset')
                standard_name = Parser.standard_name(name)
                if 'volume' in q:
                    volume = int(''.join(q['volume'].split(',')))
                else:
                    volume = None
                
                res.append({
                    'standardName': standard_name,
                    'name': name,
                    'price': q.get('lastprice'),
                    'displayPrice': q.get('lastdisplayprice'),
                    'timestamp': q.get('transacttime'),
                    'volume': volume
                })
            except Exception as e:
                app.logger.error(f'{__class__.__name__}: failed to parse {q}\n\t\tReason: {e}')
        return res


class CmeFuturesQuoteJsonParser(Parser):
    """Parser for intraday CME futures quotes."""
    def __init__(self, name):
        self.name = name

    def parse(self, response):
        self.validate_response(response)
        response_data = response.json()
        res = []
        if 'quotes' in response_data:
            for q in response_data['quotes']:
                try:
                    if q['updated'] == '-':
                        # there is a record but no useful data
                        continue

                    last = q['last']
                    price = '-'
                    if last != '-':
                        last_split = last.split('\'')
                        try:
                            int_part = float(last_split[0])
                            frac_part = 0.0
                            if len(last_split) > 1:
                                frac_str = last_split[1]
                                if len(frac_str) >= 3:
                                    frac_part = float(frac_str) / (320.0)
                                else:
                                    frac_part = float(frac_str) / (32.0)
                            price = int_part + frac_part
                        except:
                            pass
                    
                    # Convert 'updated' time to an Eastern time timestamp
                    updated_date = q['updated'].split('> ')[-1]
                    updated_time = q['updated'].split(' CT')[0]
                    updated_datetime_central = DateTime(updated_time + ' ' + updated_date).datetime
                    updated_datetime_eastern = updated_datetime_central + datetime.timedelta(hours=1)
                    timestamp = updated_datetime_eastern.strftime('%Y-%m-%dT%H:%M:%S')

                    res.append(
                        {
                            'standardName': self.cme_ticker_to_bbg_ticker(q['quoteCode']),
                            'ticker':       q['quoteCode'],
                            'productName':  q['productName'],
                            'expirationDate': q['expirationDate'],
                            'month':        q['expirationMonth'],
                            'last':         last,
                            'price':        price,
                            'change':       q['percentageChange'],
                            'open':         q['open'],
                            'high':         q['high'],
                            'low':          q['low'],
                            'priorSettle':  q['priorSettle'],
                            'volume':       q['volume'],
                            'timestamp':    timestamp,
                            'dataName':     self.name
                        }
                    )
                except Exception as e:
                    app.logger.error(f'{__class__.__name__}: failed to parse {q}\n\t\tReason: {e}')
        return res


class YahooQuoteJsonParser(Parser):
    """Parser for intraday quotes from Yahoo Finance."""
    def parse(self, response):
        self.validate_response(response)
        response_data = response.json()
        res = []
        if 'quoteResponse' in response_data and 'result' in response_data['quoteResponse']:
            for q in response_data['quoteResponse']['result']:
                try:
                    name = q['longName'] if 'longName' in q else q['shortName']
                    res.append(
                        {
                            'name': name,
                            'quote': q['regularMarketPrice'],
                            'change': q['regularMarketChange'],
                            'changePct': q['regularMarketChangePercent'],
                            'unixTimestamp': q['regularMarketTime']
                        }
                    )
                except Exception as e:
                    app.logger.error(f'{__class__.__name__}: failed to parse {q}\n\t\tReason: {e}')
        return res


class MarketWatchBondQuoteParser(Parser):
    """Parse MarketWatch bond quotes for last price and yield."""
    def parse(self, response):
        self.validate_response(response, fmt='json')
        response_data = response.json()
        res = []
        if 'InstrumentResponses' in response_data:
            for record in response_data['InstrumentResponses']:
                try:
                    if 'Matches' in record and record['Matches']:
                        match = record['Matches'][0]
                        res_record = {}

                        # Name
                        if 'Instrument' in match:
                            res_record['name'] = match['Instrument'].get('CommonName')
                            res_record['standardName'] = Parser.standard_name(res_record['name'])

                        # Price
                        if 'BondSpecific' in match:
                            bond_specific = match['BondSpecific']
                            res_record['coupon'] = bond_specific.get('CouponRate')
                            res_record['price'] = bond_specific['TradePrice']['Value'] if 'TradePrice' in bond_specific and 'Value' in bond_specific['TradePrice'] else None
                            res_record['priceChange'] = bond_specific.get('TradeChangePercent')
                            res_record['yieldChange'] = bond_specific.get('YieldChangePercent')
                            res_record['maturityDate'] = bond_specific.get('MaturityDate')[:10]

                        # Yield
                        if 'CompositeTrading' in match:
                            composite_trading = match['CompositeTrading']
                            if 'Last' in composite_trading:
                                last = composite_trading['Last']
                                res_record['timestamp'] = last.get('Time')
                                if 'Price' in last:
                                    res_record['yield'] = last['Price'].get('Value')

                        res.append(res_record)
                except Exception as e:
                    app.logger.error(f'{__class__.__name__}: failed to parse {record}\n\t\tReason: {e}')
        return res


class ExcelParser(Parser):
    """Parser for Excel data (xlsx, xls, and any format supported by pandas.read_excel)."""
    def __init__(self, dropna=True, sheet_name=0, header=0, usecols=None):
        self.dropna = dropna
        self.sheet_name = sheet_name
        self.header = header
        self.usecols=usecols

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

    def parse(self, response):
        res = super().parse(response)
        dates = res.get('Date')
        res['Date'] = [str(Date(str(d)[:10])) for d in dates]

        # replace key with series name
        old_key = [k for k in res.keys() if k != 'Date'][0]
        res['US Gas Prices'] = res[old_key]
        del res[old_key] 

        return res


class TwHtmlUSTYieldParser(Parser):    
    def parse(self, response):
        self.validate_response(response)

        # resposne is an HTML document
        root = ElementTree.fromstring(response.text)
        script_text = root[1][0][9].text
        data_str = script_text.split('data:')[1].split('legendIndex')[0].strip()[1:-2]
        raw_data_pts = [r.split('[')[1].split(',') for r in data_str.split(']')[:-1]]
        data_pts = [{'month': int(d[0]), 'yield': float(d[1].strip())} for d in raw_data_pts]

        return data_pts


class ErisSwapRateCsvParser(Parser):
    def parse(self, response):
        self.validate_response(response)

        symbols = []
        tenors = []
        rates = []
        line_generator = response.iter_lines()
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if len(decoded_line) < 15:
                continue
            try:
                symbol = decoded_line[0]
                rate = decoded_line[11]

                tenor_idx = min([i for i, c in enumerate(symbol) if c.isnumeric()])
                tenor = symbol[tenor_idx:]

                symbols.append(symbol)
                tenors.append(tenor)
                rates.append(float(rate))
            except:
                # continue if value cannot be parsed as a float
                pass

        evaluation_date = decoded_line[1]
        index = decoded_line[14]

        return {
                'symbol': symbols,
                'tenor': tenors,
                'rate': rates,
                'index': index,
                'evaluationDate': evaluation_date
                }


class ErisFuturesCsvParser(Parser):

    def __init__(self):
        self.eris_futures_map = {
            'index': {
                'YI': 'SOFR',
                'KX': 'BSBY3M'
            },
            'tenor': {
                'A': '1Y',
                'T': '2Y',
                'C': '3Y',
                'D': '4Y',
                'W': '5Y',
                'B': '7Y',
                'Y': '10Y',
                'I': '12Y',
                'L': '15Y',
                'O': '20Y',
                'E': '30Y'
            }
        }

    def product_to_name(self, product):
        product = str(product)
        if len(product) < 3:
            raise ValueError(
                f'{__class__.__name__}: expected len(product code) = 3 but got {len(product)}.')
        
        index_code = product[:2]
        tenor_code = product[-1]

        if index_code not in self.eris_futures_map['index']:
            raise KeyError(f'{__class__.__name__}: unrecognized index code {index_code}.')
        index = self.eris_futures_map['index'][index_code]

        if tenor_code not in self.eris_futures_map['tenor']:
            raise KeyError(f'{__class__.__name__}: unrecognized tenor code {tenor_code}.')
        tenor = self.eris_futures_map['tenor'][tenor_code]

        name = f'{tenor} Eris {index} Swap Future'
        return name

    def parse(self, response):
        self.validate_response(response)
        
        res = []
        line_generator = response.iter_lines()
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if (not decoded_line) or (decoded_line[0] == 'Symbol') or len(decoded_line) < 8:
                continue

            symbol = decoded_line[0]
            product = decoded_line[1]
            period = decoded_line[2]
            price = decoded_line[3]
            par_rate = decoded_line[5]
            
            try:

                price = self.to_float(price)
                par_rate = self.to_float(par_rate)

                timestamp = self.current_time_as_str()

                res.append(
                    {
                        'ticker':       symbol,
                        'productName':  product,
                        'expirationDate': period,
                        'last':         price,
                        'price':        price,
                        'parRate':      par_rate,
                        'timestamp':    timestamp,
                        'dataName':     self.product_to_name(product)
                    }
                )
            except Exception as e:
                app.logger.error(
                    f'{__class__.__name__}: failed to parse {decoded_line}\n\t\tReason: {e}')
        return res


class ErisIntradayCurveCsvParser(Parser):
    def __init__(self, value_col_name='DiscountFactor'):
        self.value_col_name = value_col_name

    def parse(self, response):
        self.validate_response(response)

        dates = []
        dfs = []
        line_generator = response.iter_lines()
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if (not decoded_line) or (decoded_line[0] == 'Date') or len(decoded_line) < 4:
                continue

            date = decoded_line[0]
            df = self.to_float(decoded_line[1])

            if df <= 0.0:
                # skip nonsense values
                break

            try:
                if df == 1.0:
                    # this is the first line
                    evaluation_date = decoded_line[2]
                    curve = decoded_line[3]
                    time = decoded_line[4]

                dfs.append(float(df))
                dates.append(self.standard_date_str(date))          # already in yyyy-mm-dd format

            except Exception as e:
                app.logger.error(
                    f'{__class__.__name__}: failed to parse {decoded_line}\n\t\tReason: {e}')
        
        timestamp = DateTime(time[:-4]).datetime.strftime('%Y-%m-%dT%H:%M:%S')

        return {
            'Date': dates,
            self.value_col_name: dfs,
            'curveName': curve,
            'evaluationDate': evaluation_date,
            'timestamp': timestamp
        }


class ErisEodCurveCsvParser(Parser):
    def __init__(self, field, value_col_name='DiscountFactor'):
        self.field = field
        self.value_col_name = value_col_name

    def parse_fwd_rate(self, line_generator):
        dates = []
        fwd_start_dates = []
        fwd_rates = []
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if (not decoded_line) or (decoded_line[0] == 'Date') or len(decoded_line) < 6:
                continue
            try:
                date = decoded_line[0]
                fwd_date = decoded_line[4]
                fwd_rate = decoded_line[3]

                if fwd_date != date:
                    # it's a non-business day, copy the last fwd rate
                    if fwd_rates:
                        fwd_start_dates.append(self.standard_date_str(date))
                        fwd_rates.append(fwd_rates[-1])
                else:
                    fwd_start_dates.append(self.standard_date_str(fwd_date))
                    fwd_rates.append(self.to_float(fwd_rate))

            except Exception as e:
                    app.logger.error(f'{__class__.__name__}: failed to parse {decoded_line}\n\t\tReason: {e}')
        return {
            'Date': fwd_start_dates,
            self.value_col_name: fwd_rates
        }

    def parse_df(self, line_generator):
        dates = []
        dfs = []
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if (not decoded_line) or (decoded_line[0] == 'Date') or len(decoded_line) < 6:
                continue
            try:
                date = decoded_line[0]
                df = decoded_line[1]

                dates.append(self.standard_date_str(date))
                dfs.append(self.to_float(df))

            except Exception as e:
                    app.logger.error(f'{__class__.__name__}: failed to parse {decoded_line}\n\t\tReason: {e}')
        return {
            'Date': dates,
            self.value_col_name: dfs
        }

    def parse_zero_rate(self, line_generator):
        dates = []
        zero_rates = []
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if (not decoded_line) or (decoded_line[0] == 'Date') or len(decoded_line) < 6:
                continue
            try:
                date = decoded_line[0]
                zero_rate = decoded_line[2]

                dates.append(self.standard_date_str(date))
                zero_rates.append(self.to_float(zero_rate))

            except Exception as e:
                    app.logger.error(f'{__class__.__name__}: failed to parse {decoded_line}\n\t\tReason: {e}')
        return {
            'Date': dates,
            self.value_col_name: zero_rates
        }
                        
    def parse(self, response):
        self.validate_response(response)
        line_generator = response.iter_lines()

        if self.field == 'ForwardRate':
            return self.parse_fwd_rate(line_generator)
        elif self.field == 'DiscountFactor':
            return self.parse_df(line_generator)
        elif self.field == 'ZeroRate':
            return self.parse_zero_rate(line_generator)
        else:
            raise ValueError(f'{__class__.__name__}: unsupported field {self.field}.)')


class QuikStrikeHtmlParser(Parser):
    """Base class for parsing QuikStrike HTML documents."""
    def parse(self, response):
        self.validate_response(response)
        return response.text

class QuikStrikeCtdOtrParser(Parser):
    def parse(self, response):
        raw_text = super().parse(response)
        tr_split = raw_text.split('<tr')
        rows = [r.split('</tr>')[0] for r in tr_split[4:]]
        row_data = [[s.split('</td>')[0].split('">')[1]
                     for s in row.split('<td class=')[1:]] for row in rows]

        return [self.parse_row_data(row) for row in row_data]

    def parse_row_data(self, row):
        # each row_data looks has this form:
        # ['2 Yr',                            0   Future name
        #  '\r\n<span>TUZ3</span>\r\n\r\n',   1   Future ticker
        #  '101-28.125',                      2   Future price
        #  '3 1/2',                           3   CTD coupon
        #  '9/15/2025',                       4   CTD maturity
        #  '1/4/2024',                        5   CTD delivery date
        #  '9/15/2022',                       6   CTD issue date
        #  '4.9266%',                         7   CTD Forward yield
        #  '$33.03',                          8   Futures DV01
        #  '5',                               9   OTR coupon
        #  '8/31/2025',                       10  OTR maturity
        #  '9/5/2023',                        11  OTR settlement date
        #  '8/31/2023',                       12  OTR issue date
        #  '4.8816%',                         13  OTR yield
        #  '$37.49']                          14  OTR DV01
        futureTicker = row[1].split('<span>')[1].split('</span>')[0]
        return {
            'standardName': self.cme_ticker_to_bbg_ticker(futureTicker),
            'futureName': row[0],
            'futureTicker': futureTicker,
            'futurePrice': row[2],
            'ctdCoupon': self.mixed_number_to_float(row[3]),
            'ctdMaturity': self.standard_date_str(row[4]),
            'ctdDeliveryDate': self.standard_date_str(row[5]),
            'ctdIssueDate': self.standard_date_str(row[6]),
            'fwdYield': float(self.chop_pct(row[7])),
            'futureDV01': float(row[8][1:]),
            'otrCoupon': self.mixed_number_to_float(row[9]),
            'otrMaturity': self.standard_date_str(row[10]),
            'otrSettlementDate': self.standard_date_str(row[11]),
            'otrIssueDate': self.standard_date_str(row[12]),
            'otrYield': float(self.chop_pct(row[13])),
            'otrDV01': float(row[14][1:])
        }


class QuikStrikeFedWatchParser(QuikStrikeHtmlParser):

    def parse_fed_funds_futures(self, ff_split):
        ff_split0 = ff_split.split('<th>')
        futures_codes = [d.split('</th>')[0] for d in ff_split0[1:]]
        futures_prices = [float(d.split('</td>')[0]) for d in ff_split0[-1].split('<td>')[1:]]

        timestamp = self.current_time_as_str()

        res = [
            {
                'ticker': code,
                'productName': 'FF' + code[-2:],
                'month': Parser.futures_code_to_expiration_month(code),
                'last': price,
                'price': price,
                'timestamp': timestamp,
                'dataName': 'FF Futures (FedWatch)'
            }   for code, price in zip(futures_codes, futures_prices)
        ]
        return res

    def parse_meeting_prob_row(self, row_data):
        date = self.standard_date_str(row_data[0])
        row_data_strs = [d.split('\'>\r\n')[1].split('\r\n')[0].strip() for d in row_data[1:] if len(d.split('\'>\r\n')) > 1]
        row_data = [float(d.split('%')[0]) if d else 0.0 for d in row_data_strs]
        return date, row_data

    def parse_meeting_probabilities(self, meeting_prob_split):
        mp_split0 = meeting_prob_split.split('<th>')
        ranges = [d.split('</th>')[0] for d in mp_split0[2:]]
        rows = [self.parse_meeting_prob_row(d.split('</td>')) for d in mp_split0[-1].split('<td class="number">')[1:]]
        dates, data = zip(*rows)
        res = {
            'ranges': ranges,
            'dates': list(dates),
            'probabilities': list(data)
        }
        return res

    def parse_total_probabilities(self, total_prob_split):
        tp_split0 = total_prob_split.split('<th>')
        rows = [[x.split('</td>\r\n')[0] for x in d.split('<td class="number">')[1:]]
                for d in tp_split0[-1].split('<tr>\r\n')[1:]]

        res = []
        for row in rows:
            row_dict = {
                'Meeting Date': self.standard_date_str(row[0]),
                'Days to Meeting': row[1],
                'Ease': float(self.chop_pct(row[2])),
                'No Change': float(self.chop_pct(row[3])),
                'Hike': float(self.chop_pct(row[4]))
            }
            res.append(row_dict)

        return res

    def calc_expected_change(self, meeting_probabilities, total_probabilities):
        ease_prob = total_probabilities[0]['Ease']
        no_change_prob = total_probabilities[0]['No Change']
        next_meeting_probabilities = meeting_probabilities['probabilities'][0]

        running_ease = 0.0
        tol = 1E-6
        range_idx = 0
        for prob in next_meeting_probabilities:
            if (abs(prob - no_change_prob) < tol) and (abs(ease_prob - running_ease) < tol):
                break
            range_idx += 1
            running_ease += prob

        if range_idx >= len(next_meeting_probabilities):
            raise ValueError(f'{self.__class__}.{__name__}: failed to find {ease_prob} in next meeting probabilities {next_meeting_probabilities}.')

        if range_idx >= len(meeting_probabilities['ranges']):
            raise IndexError(f'{self.__class__}.{__name__}: unexpected meeting probability without heading in {meeting_probabilities}.')

        current_range = meeting_probabilities['ranges'][range_idx]
        app.logger.info(f'{self.__class__}.{__name__}: Current FedFunds target range {current_range}.')

        rate_changes = [25.0 * (i - range_idx) for i in range(len(next_meeting_probabilities))]
        expected_change_from_current = [ 0.01 * sum([r * p for r, p in zip(rate_changes, prob_row)]) for prob_row in meeting_probabilities['probabilities']]
        expected_incremental_change = [this - prev for this, prev in zip(
            expected_change_from_current,
            [0.0] + expected_change_from_current[:-1]
            )
        ]
        res = {
            'fromCurrent': [[d, r] for d, r in zip(meeting_probabilities['dates'], expected_change_from_current)],
            'atMeeting': [[d, r] for d, r in zip(meeting_probabilities['dates'], expected_incremental_change)]
        }

        return res

    def parse(self, response):
        raw_text = super().parse(response)

        split0 = raw_text.split('Fed Fund Futures')[1].split('Meeting Probabilities')
        split1 = split0[1].split('Total Probabilities')
        
        ff_split = split0[0]
        meeting_prob_split = split1[0]
        total_prob_split = split1[1]

        fed_funds_futures = self.parse_fed_funds_futures(ff_split)
        meeting_probabilities = self.parse_meeting_probabilities(meeting_prob_split)
        total_probabilites = self.parse_total_probabilities(total_prob_split)
        expected_changes = self.calc_expected_change(meeting_probabilities, total_probabilites)

        return {
            'fedFundsFutures': fed_funds_futures,
            'meetingProbabilities': meeting_probabilities,
            'totalProbabilities': total_probabilites,
            'expectedChangeBps': expected_changes
        }


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
