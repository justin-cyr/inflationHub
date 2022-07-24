import math
from multiprocessing.managers import ValueProxy

from .. import config as cfg
from ..utils import Date, Tenor
from . import convertutils as cu
from . import domains

def supported_curve_data_point_types(curve_type):
    """Return the names of curve data point sub-classes that can be used by the front end."""
    data_point_map = {
        cfg.CPI: [
            CpiLevelDataPoint.__name__,
            YoYDataPoint.__name__
        ],
        cfg.SEASONALITY: [
            CurveDataPoint.__name__
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
        if t == 'CurveDataPoint':
            return CurveDataPoint.deserialize(d)
        elif t == 'CpiLevelDataPoint':
            return CpiLevelDataPoint.deserialize(d)
        elif t == 'YoYDataPoint':
            return YoYDataPoint.deserialize(d)
        else:
            raise NotImplementedError(f'CurveDataPointFactory.deserialize: type {t} is not supported.')


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
