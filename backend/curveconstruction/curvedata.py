from ..utils import Date, Tenor

def supported_curve_data_point_types():
    """Return the names of curve data point sub-classes that can be used by the front end."""
    return [
        CpiLevelDataPoint.__name__,
        YoYDataPoint.__name__
    ]


class CurveDataPoint(object):

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
    def __init__(self, value, date, label=None):
        if not label:
            label = '_'.join([self.__class__.__name__, str(date)])
        super().__init__(value, label)

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


class YoYDataPoint(CurveDataPoint):
    def __init__(self, value, start_date, tenor, label=None):
        if not label:
            label = '_'.join([self.__class__.__name__, str(start_date), str(tenor)])
        super().__init__(value, label)

        self.start_date = Date(start_date)
        self.tenor = Tenor(tenor)

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
