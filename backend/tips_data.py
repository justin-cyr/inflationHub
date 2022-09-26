import datetime
import os

from backend.data import DataGetter, get_fred_data
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
    getter = DataGetter('TIPS CUSIPs')

    response = getter.get(tips_cusips_url)
    return [record['cusip'] for record in response.json()]


def get_treasury_reference_data(cusip):
    """Get reference data for each cusip in CUSIPs from TreasuryDirect."""
    url = 'https://www.treasurydirect.gov/TA_WS/securities/search?format=json&cusip=' + cusip
    
    getter = DataGetter(cusip)
    response = getter.get(url)
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

    # configure web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    if cfg.IS_PROD in os.environ:
        options.binary_location = os.environ[cfg.GOOGLE_CHROME_BIN]

    driver = webdriver.Chrome(executable_path=os.environ[cfg.CHROMEDRIVER_PATH],
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
        row['CHANGE'] = 0.0 if row['CHANGE'] == 'unch.' else float(row['CHANGE'])
        
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

