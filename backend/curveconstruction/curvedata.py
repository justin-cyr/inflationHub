
import json
import math

from .. import config as cfg
from ..utils import Date, Tenor, Month
from . import convertutils as cu
from . import domains
from ..products.bonds import Bond

def supported_curve_data_point_types(curve_type):
    """Return the names of curve data point sub-classes that can be used by the front end."""
    data_point_map = {
        cfg.BONDCURVE: [
            BondPriceDataPoint.__name__,
            BondYieldDataPoint.__name__
        ],
        cfg.CPI: [
            CpiLevelDataPoint.__name__,
            YoYDataPoint.__name__
        ],
        cfg.SEASONALITY: [
            CpiLevelDataPoint.__name__,
            AdditiveSeasonalityDataPoint.__name__
        ]
    }
    
    return data_point_map[curve_type]


class CurveDataPoint(object):

    __supported_X_domains__ = []
    __supported_Y_domains__ = []

    def __init__(self, value, label):
        try:
            float_value = float(value)
        except:
            raise TypeError('CurveDataPoint: value must be float.')
        self.value = float_value

        self.label = str(label)


    def serialize(self):
        d = self.__dict__
        d['type'] = self.__class__.__name__
        return d

    
    def __repr__(self):
        return str(self.serialize())


    @classmethod
    def deserialize(cls, d):
        for key in ['value', 'label']:
            if key not in d:
                raise KeyError(f'CurveDataPoint.deserialize: dict must contain key {key}.')

        return CurveDataPoint(d['value'], d['label'])


    # decorator
    def check_domains(convert):
        def inner(self, domainX, domainY, *args, **kwargs):

            if domainX not in self.__class__.__supported_X_domains__:
                raise ValueError(f'{self.__class__.__name__}: unsupported X domain {domainX}')

            if domainY not in self.__class__.__supported_Y_domains__:
                raise ValueError(f'{self.__class__.__name__}: unsupported Y domain {domainY}')

            return convert(self, domainX, domainY, *args, **kwargs)
        return inner


class CurveDataPointFactory(object):
    
    @classmethod
    def deserialize(cls, d):
        """Determine the type and delegate."""
        if not isinstance(d, dict):
            raise TypeError('CurveDataPointFactory.deserialize: argument must be a dict.')

        if 'type' not in d:
            raise KeyError('CurveDataPointFactory.deserialize: dict must contain key type.')

        t = d['type']
        # Call constructor based on type
        deserializer_map = { cls.__name__: cls.deserialize for cls in [
                                    CurveDataPoint,
                                    CpiLevelDataPoint,
                                    YoYDataPoint,
                                    BondPriceDataPoint,
                                    BondYieldDataPoint,
                                    AdditiveSeasonalityDataPoint
                                ]
                            }
        if t not in deserializer_map:
            raise NotImplementedError(f'CurveDataPointFactory.deserialize: type {t} is not supported.')
        
        return deserializer_map[t](d)


class CpiLevelDataPoint(CurveDataPoint):

    __supported_X_domains__ = [
        domains.TIME_ACT_365
        ]
    __supported_Y_domains__ = [
        domains.CPI_LEVEL,
        domains.TIME_WEIGHTED_ZERO_RATE,
        domains.ZERO_RATE
    ]

    def __init__(self, value, date, label=None):
        if not label:
            label = '_'.join([self.__class__.__name__, str(date)])
        super().__init__(value, label)
        if self.value <= 0.0:
            raise ValueError(f'CpiLevelDataPoint: level must be positive but got {value}.')
        self.date = Date(date)

    def serialize(self):
        d = self.__dict__
        d['type'] = self.__class__.__name__
        return d
    
    @classmethod
    def deserialize(cls, d):
        for key in ['value', 'date']:
            if key not in d:
                raise KeyError(f'CpiLevelDataPoint.deserialize: dict must contain key {key}.')

        return CpiLevelDataPoint(d['value'], d['date'], d.get('label'))

    
    @CurveDataPoint.check_domains
    def convert(self, domainX, domainY, base_date=None, base_cpi=None):
        t, y = None, None

        if base_date:
            t = cu.time_difference(base_date, self.date, domainX)

        if domainY == domains.CPI_LEVEL:
            y = self.value
        
        else:
            # base_cpi is required
            if base_cpi:
                time_weighted_zero_rate = math.log(self.value / base_cpi)

                if domainY == domains.TIME_WEIGHTED_ZERO_RATE:
                    y = time_weighted_zero_rate
                
                elif domainY == domains.ZERO_RATE:
                    # base_date is required
                    if t:
                        y = time_weighted_zero_rate / t
                    elif t == 0.0:
                        y = 0.0

        return (t, y)


class YoYDataPoint(CurveDataPoint):

    # supported domains are same as CpiLevelDataPoint

    def __init__(self, value, start_date, tenor, label=None):
        if not label:
            label = '_'.join([self.__class__.__name__, str(start_date), str(tenor)])
        super().__init__(value, label)

        self.start_date = Date(start_date)
        self.tenor = Tenor(tenor)

        if self.tenor.unit != 'Y':
            raise ValueError('YoYDataPoint: tenor must be in years but got {tenor}.')

        self.end_date = self.start_date.addTenor(self.tenor)


    def serialize(self):
        d = self.__dict__
        d['type'] = self.__class__.__name__
        return d
    
    @classmethod
    def deserialize(cls, d):
        for key in ['value', 'start_date', 'tenor']:
            if key not in d:
                raise KeyError(f'YoYDataPoint.deserialize: dict must contain key {key}.')

        return YoYDataPoint(d['value'], d['start_date'], d['tenor'], d.get('label'))


    def to_CpiLevelDataPoint(self, start_date_cpi):
        """Return the equivalent CpiLevelDataPoint."""
        years = self.tenor.size
        end_date_cpi = start_date_cpi * (1.0 + self.value)**(years)
        return CpiLevelDataPoint(end_date_cpi, self.end_date, label=self.label)


    def convert(self, domainX, domainY, start_date_cpi, base_date=None, base_cpi=None):
        cpiLevelDataPoint = self.to_CpiLevelDataPoint(start_date_cpi)
        return cpiLevelDataPoint.convert(domainX, domainY, base_date, base_cpi)


class BondDataPoint(CurveDataPoint):
    def __init__(self, value, bond, base_date=Date.today(), label=None):
        # bond argument is eiter type Bond or deserializable as a Bond
        if isinstance(bond, Bond):
            self.bond = bond
        elif isinstance(bond, dict):
            self.bond = Bond.create_bond(**bond)
        elif isinstance(bond, str):
            self.bond = Bond.create_bond(**json.loads(bond))
        else:
            raise ValueError(f'{self.__class__.__name__}: bond argument must Bond type or deserializable using Bond.create_bond.')
        
        if not label:
            label = '_'.join([self.__class__.__name__, str(self.bond.maturity_date)])
        
        super().__init__(value, label)
        self.base_date = Date(base_date)

    def to_BondPriceAndYieldDataPoint(self):
        raise NotImplementedError(f'{self.__class__.__name__}.{__name__}: not implemented in base class')


class BondPriceDataPoint(BondDataPoint):
    def __init__(self, clean_price, bond, base_date=Date.today(), label=None):
        super().__init__(clean_price, bond, base_date=base_date, label=label)
        self.price = clean_price
    
    @classmethod
    def deserialize(cls, d):
        for key in ['clean_price', 'bond']:
            if key not in d:
                raise KeyError(f'{cls.__name__}.deserialize: dict must contain key {key}.')

        return BondPriceDataPoint(d['clean_price'], d['bond'], base_date=d.get('base_date'), label=d.get('label'))

    def to_BondYieldDatapoint(self):
        """Return the equivalent BondYieldDataPoint"""
        ytm = self.bond.clean_price_to_yield(self.price, self.base_date)
        return BondYieldDataPoint(ytm, self.bond, base_date=self.base_date, label=f'Converted_{self.label}')

    def to_BondPriceAndYieldDataPoint(self):
        return BondPriceAndYieldDataPoint(self.bond, clean_price=self.price, base_date=self.base_date, label=f'Consistent_{self.label}')


class BondYieldDataPoint(BondDataPoint):
    def __init__(self, ytm, bond, base_date=Date.today(), label=None):
        super().__init__(ytm, bond, base_date=base_date, label=label)
        self.ytm = ytm
    
    @classmethod
    def deserialize(cls, d):
        for key in ['ytm', 'bond']:
            if key not in d:
                raise KeyError(f'{cls.__name__}.deserialize: dict must contain key {key}.')

        return BondYieldDataPoint(d['ytm'], d['bond'], base_date=d.get('base_date'), label=d.get('label'))

    def to_BondPriceDataPoint(self):
        """Return the equivalent BondPriceDataPoint"""
        clean_price = self.bond.yield_to_clean_price(self.ytm, self.base_date)
        return BondPriceDataPoint(clean_price, self.bond, base_date=self.base_date, label=f'Converted_{self.label}')

    def to_BondPriceAndYieldDataPoint(self):
        return BondPriceAndYieldDataPoint(self.bond, ytm=self.ytm, base_date=self.base_date, label=f'Consistent_{self.label}')


class BondPriceAndYieldDataPoint(BondDataPoint):
    """A bond with consistent price and yield values."""
    def __init__(self, bond, ytm=None, clean_price=None, base_date=Date.today(), label=None):
        super().__init__(0.0, bond, base_date=base_date, label=label)
        
        # requires ytm or clean_price
        if ytm:
            self.ytm = ytm
            # override price with consistent price from yield
            self.price = self.bond.yield_to_clean_price(self.ytm, self.base_date)

        elif clean_price:
            self.price = clean_price
            self.ytm = self.bond.clean_price_to_yield(self.price, self.base_date)
        
        else:
            raise ValueError(f'{self.__class__.__name__}: requires either ytm or clean_price.')
    
    def to_BondPriceAndYieldDataPoint(self):
        return self

    def ctsly_compounded_yield(self):
        return self.bond.annual_yield_to_ctsly_compounded(self.ytm, self.base_date)
        
class AdditiveSeasonalityDataPoint(CurveDataPoint):
    def __init__(self, value, month_str, label=None):
        # validate month_str
        month_obj = Month.from_str_slice(month_str)
        self.month_str = month_obj.__repr__()
        if not label:
            label = '_'.join([self.__class__.__name__, self.month_str])
        super().__init__(value, label)

    def get_month(self):
        """Return the Month enum for this data point."""
        return Month.from_str(self.month_str)

    @classmethod
    def deserialize(cls, d):
        for key in ['value', 'month_str']:
            if key not in d:
                raise KeyError(f'{cls}.{__name__}: dict must contain key {key}.')

        return AdditiveSeasonalityDataPoint(d['value'], d['month_str'], d.get('label'))
