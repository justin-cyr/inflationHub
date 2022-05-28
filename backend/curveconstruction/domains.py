
class DomainPair(object):
    def __init__(self, domainX, domainY):
        self.domainX = str(domainX)
        self.domainY = str(domainY)

    def __repr__(self):
        return f'DomainPair({self.domainX}, {self.domainY})'


# Domains
ADDITIVE_SEASONALITY = 'ADDITIVE_SEASONALITY'
CPI_LEVEL = 'CPI_LEVEL'
INSTANTANEOUS_RATE = 'INSTANTANEOUS_RATE'
MONTH = 'MONTH'
TIME_30_360 = 'TIME_30_360'
TIME_ACT_365 = 'TIME_ACT_365'
TIME_WEIGHTED_ZERO_RATE = 'TIME_WEIGHTED_ZERO_RATE'
ZERO_RATE = 'ZERO_RATE'
