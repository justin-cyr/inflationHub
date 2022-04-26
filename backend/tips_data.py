import datetime
import os

from backend.data import DataGetter
from backend import config as cfg

# get logger from current_app instance
from flask import current_app as app


def get_tips_cusips():
    """Return list of TIPS cusips"""
    tips_cusips_url = 'https://www.treasurydirect.gov/TA_WS/secindex/current/CPI?format=json'
    getter = DataGetter('TIPS CUSIPs')

    response = getter.get(tips_cusips_url)
    return [record['cusip'] for record in response.json()]


def get_treasury_reference_data(cusip):
    """Get reference data for each cusip in CUSIPs from TreasuryDirect."""
    url = 'https://www.treasurydirect.gov/TA_WS/securities/search?format=json&cusip=' + cusip
    today = datetime.date.today()
    
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
    maturity_date_str = record['maturityDate']
    maturity_date = datetime.datetime.strptime(maturity_date_str, '%Y-%m-%d').date()
    record['tenor'] = (maturity_date - today).days / 365.0

    return record


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
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.common.by import By

    # configure web driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    if cfg.IS_PROD in os.environ:
        options.binary_location = os.environ[cfg.GOOGLE_CHROME_BIN]

    app.logger.info('Environ = ' + str(os.environ))
    driver = webdriver.Chrome(executable_path=os.environ[cfg.CHROMEDRIVER_PATH],
                            options=options)

    # get page
    driver.get('https://www.wsj.com/market-data/bonds/tips')

    # find table data elements
    table_data = driver.find_elements(By.TAG_NAME, 'td')

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
        row[columns[column_count]] = td.text
    
        column_count += 1
        column_count %= num_cols
        if column_count % num_cols == 0:
            row_data.append(row)
            row = {}

    # close page
    driver.quit()

    # post processing
    for row in row_data:
        row['MATURITY'] = str(datetime.datetime.strptime(row['MATURITY'], '%Y %b %d').date())
        row['CHANGE'] = 0.0 if row['CHANGE'] == 'unch.' else float(row['CHANGE'])
        
        for col in ['COUPON', 'BID', 'ASK', 'YIELD', 'ACCRUED PRINCIPAL']:
            row[col] = float(row[col])

    return row_data

