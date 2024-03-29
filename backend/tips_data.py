from concurrent import futures
import datetime
import os
import requests

from backend.data import HttpGetter, get_fred_data, MarketWatchBondQuoteParser
from backend import config as cfg

# get logger from current_app instance
from flask import current_app as app

def calc_tenor(maturity_date, start_date=datetime.date.today()):
    """Return tenor in years from start_date to maturity_date.
        maturity_date can be a datetime.date or a yyyy-mm-dd string.
    """
    if isinstance(maturity_date, str):
        end_date = datetime.datetime.strptime(maturity_date, '%Y-%m-%d').date()
    else:
        end_date = maturity_date

    dcf = (end_date - start_date).days / 365.0
    return dcf


def get_tips_cusips():
    """Return list of TIPS cusips"""
    tips_cusips_url = 'https://www.treasurydirect.gov/TA_WS/secindex/current/CPI?format=json'
    getter = HttpGetter('TIPS CUSIPs', tips_cusips_url)

    response = getter.get()
    return [record['cusip'] for record in response.json()]


def get_all_tsy_reference_data():
    """Return reference data for all outstanding Treasuries, from Auction Query page on TreasuryDirect."""
    first_page_url = f'https://www.treasurydirect.gov/TA_WS/securities/jqsearch?format=json&pagesize=1&pagenum=0'
    app.logger.info(f'get_all_tsy_reference_data: making request GET {first_page_url}')
    num_records = requests.get(first_page_url).json()['totalResultsCount']

    page_size = 100
    max_workers = 32
    pages = (num_records // page_size) + 1
    urls = [f'https://www.treasurydirect.gov/TA_WS/securities/jqsearch?format=json&pagesize={page_size}&pagenum={p}'
                for p in range(pages)
            ]

    def get_page(url):
        res = requests.get(url).json()
        return res['securityList']

    today = datetime.date.today()
    def str_to_date(s):
        s = s[:10]
        return datetime.date(int(s[:4]), int(s[5:7]), int(s[8:]))

    # request pages in multiple threads
    results = []
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = { executor.submit(get_page, url): url for url in urls }
        
        for future in futures.as_completed(future_to_url):
            try:
                results += future.result()
            except Exception as e:
                app.logger.error(e)

    # filter out matured bonds and reopenings
    outstanding = [r for r in results if (str_to_date(r['maturityDate']) > today) and (r['reopening'] == 'No')]
    return outstanding


def get_treasury_reference_data(cusip):
    """Get reference data for each cusip in CUSIPs from TreasuryDirect."""
    url = 'https://www.treasurydirect.gov/TA_WS/securities/search?format=json&cusip=' + cusip
    
    getter = HttpGetter(cusip, url)
    response = getter.get()
    record = response.json()[0]
    
    # strip timestamp out of date fields
    date_fields = [
        'issueDate',
        'maturityDate',
        'announcementDate',
        'auctionDate',
        'datedDate',
        'backDatedDate',
        'firstInterestPaymentDate',
        'maturingDate'
    ]
    for key in date_fields:
        record[key] = record[key][:10]

    # calculate tenor
    record['tenor'] = calc_tenor(record['maturityDate'])

    return record


def get_tips_fred_key(term, maturity_date):
    """Return FRED time series key for TIPS yield data."""
    maturity_datetime = datetime.datetime.strptime(maturity_date, '%Y-%m-%d')
    maturity_month = maturity_datetime.strftime("%b")
    maturity_month_letter = 'L' if maturity_month == 'Jul' else maturity_month[0]
    maturity_year = str(maturity_datetime.date().year)

    return 'DTP' + term + maturity_month_letter + maturity_year[-2:]


def get_tips_yield_data(term, maturity_date, name=None):
    """Get daily yield-to-maturity time series from St. Louis Fed."""
    key = get_tips_fred_key(term, maturity_date)
    return get_fred_data(key, name)


def get_term_from_tsy_record(record):
    """Return original term of bond from TreasuryDirect reference data record."""
    term = ''
    if 'term' in record:
        term_str = str(record['term'])
        term = term_str.split('-')[0]
    return term
        

def get_maturity_date_from_tsy_record(record):
    """Return maturityDate of bond from TreasuryDirect reference data record."""
    return str(record.get('maturityDate'))


def get_tips_yield_data_by_cusip(cusip):
    """Return yield to maturity daily time series for a given TIPS cusip."""
    record = get_treasury_reference_data(cusip)
    term = get_term_from_tsy_record(record)
    maturity_date = get_maturity_date_from_tsy_record(record)
    return get_tips_yield_data(term, maturity_date, name='Real Yield')


def get_tips_prices_wsj():
    """Return TIPS bid/ask prices and yields from WSJ markets page.
    Data returned as
    [
        {
            'MATURITY': '2022-07-15',
            'COUPON': 0.125,
            'BID': 101.28,
            'ASK': 101.30,
            'CHANGE': -4.0,
            'YIELD': -8.408,
            'ACCRUED PRINCIPAL': 1231.0
        }
    ]
    """
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service

    # configure web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    if cfg.IS_PROD in os.environ:
        options.binary_location = os.environ[cfg.GOOGLE_CHROME_BIN]

    service = Service(executable_path=os.environ[cfg.CHROMEDRIVER_PATH])
    driver = webdriver.Chrome(service=service,
                            options=options)

    # get page
    url = 'https://www.wsj.com/market-data/bonds/tips'
    app.logger.info(f'get_tips_prices_wsj() making request GET {url}')
    driver.get(url)

    # find table data elements
    tables = driver.find_elements(By.TAG_NAME, 'table')
    if not tables:
        raise RuntimeError(f'get_tips_prices_wsj: No <table> found on page {url}')
    table_element = tables[0]
    table_doc = table_element.get_attribute('innerHTML')

    # close page
    driver.quit()
    table_data = [d.split('>')[-1] for d in table_doc.split('</td>')][:-1]

    # parse into row data (takes around 20-25 seconds)
    columns = [
        'MATURITY',
        'COUPON',
        'BID',
        'ASK',
        'CHANGE',
        'YIELD',
        'ACCRUED PRINCIPAL'
    ]
    # use number of columns to determine row endings based on counter
    num_cols = len(columns)

    row_data = []
    column_count = 0
    row = {}
    for td in table_data:
        row[columns[column_count]] = td
    
        column_count += 1
        column_count %= num_cols
        if column_count % num_cols == 0:
            row_data.append(row)
            row = {}

    # post processing
    for row in row_data:
        row['MATURITY'] = str(datetime.datetime.strptime(row['MATURITY'], '%Y %b %d').date())
        row['TENOR'] = calc_tenor(row['MATURITY'])
        row['CHANGE'] = 0.0 if row['CHANGE'] in ['unch.', '...'] else float(row['CHANGE'])
        
        for col in ['COUPON', 'BID', 'ASK', 'YIELD', 'ACCRUED PRINCIPAL']:
            try:
                row[col] = float(row[col])
            except ValueError as e:
                pass

        # Mid price and spread
        if 'ASK'in row and 'BID' in row:
            row['MID'] = (row['ASK'] + row['BID']) / 2.0

            # spread in 32nds of a point
            ask_int_part, bid_int_part = int(row['ASK']), int(row['BID'])
            ask_frac_part, bid_frac_part = row['ASK'] - ask_int_part, row['BID'] - bid_int_part
            row['BID_ASK_SPREAD'] = 32 * (ask_int_part - bid_int_part) + 100 * (ask_frac_part - bid_frac_part)

    return row_data


def cusip_to_us_isin(cusip):
    """Given the CUSIP of a US Govt security, return the ISIN number.
        This is just the CUSIP with the 'check digit' appended at the end.
        The check digit is calculated using Luhn's algorithm.
    """
    # country code US
    cusip_num = 3028
    for c in cusip:
        if c.isnumeric():
            cusip_num = cusip_num * 10 + int(c)
        else:
            cusip_num = cusip_num * 100 + (ord(c) - 55)

    twice_sum = 0
    i = 0
    while cusip_num > 0:
        d = (cusip_num % 10) * (2 - (i % 2))
        if d >= 10:
            twice_sum += d % 10
            d = d // 10
        twice_sum += d

        cusip_num = cusip_num // 10
        i += 1

    check_digit = (- twice_sum) % 10
    return cusip + str(check_digit)


def get_tips_quotes_from_marketwatch(cusips):
    """Query Market-Watch for last price and yield of these TIPS CUSIPs."""
    endpoint = 'https://api.wsj.net/api/dylan/quotes/v2/comp/quoteByDialect'
    static_query_params = {
        'dialect': 'official',
        'MaxInstrumentMatches': '1',
        'needed': 'CompositeTrading',
        'accept': 'application/json',
        'EntitlementToken': 'cecc4267a0194af89ca343805a3e57af',
        'ckey': 'cecc4267a0'
    }
    mapped_cusip_names = ['BOND-US-' + cusip_to_us_isin(c) for c in cusips]

    url = endpoint + '?' + '&'.join([k + '=' + v for k, v in static_query_params.items()]) + '&id=' + ','.join(mapped_cusip_names)
    getter = HttpGetter(f'Market-Watch TIPS Quotes {cusips}', url)
    response = getter.get()
    parser = MarketWatchBondQuoteParser()
    return parser.parse(response)
