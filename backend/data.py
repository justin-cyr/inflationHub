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
            self.data_parser = ErisIntradayCurveCsvParser()
        elif data_parser == 'ErisEodCurveCsvParser':
            self.data_parser = ErisEodCurveCsvParser()
        elif data_parser == 'TwHtmlUSTYieldParser':
            self.data_parser = TwHtmlUSTYieldParser()
        elif data_parser == 'ErisSwapRateCsvParser':
            self.data_parser = ErisSwapRateCsvParser()
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
        'U.S. 3 Month Treasury': 'US 3M',
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
        'U.S. 30 Year TIPS': 'TIPS 30Y'
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

    def chop_pct(self, s):
        s = s[:-1] if s and isinstance(s, str) and s[-1] == '%' else s
        return s
    
    @staticmethod
    def standard_name(name):
        """Return the standard name of this quote used in this app."""
        return Parser.standard_name_map.get(name, '')


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

                timestamp = datetime.datetime.now().strftime(
                    '%Y-%m-%dT%H:%M:%S')

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
                dates.append(date)          # already in yyyy-mm-dd format

            except Exception as e:
                app.logger.error(
                    f'{__class__.__name__}: failed to parse {decoded_line}\n\t\tReason: {e}')
        
        timestamp = DateTime(time[:-4]).datetime.strftime('%Y-%m-%dT%H:%M:%S')

        return {
            'Date': dates,
            'DiscountFactor': dfs,
            'curveName': curve,
            'evaluationDate': evaluation_date,
            'timestamp': timestamp
        }


class ErisEodCurveCsvParser(Parser):
    def parse(self, response):
        self.validate_response(response)

        dates = []
        fwd_start_dates = []
        fwd_end_dates = []
        dfs = []
        zero_rates = []
        fwd_rates = []
        line_generator = response.iter_lines()
        for line in line_generator:
            decoded_line = line.decode('UTF-8').split(',')
            if (not decoded_line) or (decoded_line[0] == 'Date') or len(decoded_line) < 6:
                continue

            try:
                date = decoded_line[0]
                df = self.to_float(decoded_line[1])
                if df <= 0.0:
                    # skip nonsense values
                    break

                zero_rate = self.to_float(decoded_line[2])

                dates.append(date)
                dfs.append(df)
                zero_rates.append(zero_rate)

                fwd_rate = self.to_float(decoded_line[3])
                if fwd_rate != '-':
                    fwd_start = decoded_line[4]
                    fwd_end = decoded_line[5]

                    fwd_rates.append(fwd_rate)
                    fwd_start_dates.append(fwd_start)
                    fwd_end_dates.append(fwd_end)

            except Exception as e:
                app.logger.error(
                    f'{__class__.__name__}: failed to parse {decoded_line}\n\t\tReason: {e}')

        return {
            'Date': dates,
            'DiscountFactor': dfs,
            'ZeroRates_Act360_Cts': zero_rates,
            'evaluationDate': dates[0],
            'FwdRates': fwd_rates,
            'FwdStartDates': fwd_start_dates,
            'FwdEndDates': fwd_end_dates
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
