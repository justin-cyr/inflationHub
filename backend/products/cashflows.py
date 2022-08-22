
from ..utils import Date

class Cashflows(object):
    def __init__(self, payment_dates, amounts):
        # default implementation is fixed amount on each payment date
        try:
            payment_dates = list(payment_dates)
            amounts = list(amounts)
        except Exception as e:
            raise ValueError(f'Cashflows: payment_dates and amounts must be list-like types, {e}')

        if len(payment_dates) != len(amounts):
            raise ValueError(f'Cashflows: len(payment_dates)={len(payment_dates)} and len(amounts)={len(amounts)} don\'t match.')
        
        try:
            payment_date_objs = [Date(d) for d in payment_dates]
        except Exception as e:
            raise ValueError(f'Cashflows: payment_dates cannot be converted to Date type, {e}')

        sorted_cashflows = sorted(zip(payment_date_objs, amounts), key=lambda pair: pair[0])
        self.payment_dates = [pair[0] for pair in sorted_cashflows]
        self.amount_map = {str(d): a for d, a in sorted_cashflows}

    def __repr__(self):
        cashflows = [(str(d), self.amount_map[str(d)]) for d in self.payment_dates]
        return f'Cashflows({cashflows})'

    def amount_calc(self, d):
        # override in inherited classes
        return self.amount_map[str(Date(d))]

    def amount(self, d):
        return self.amount_calc(d)



