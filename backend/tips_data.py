import datetime

from backend.data import DataGetter

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

    

