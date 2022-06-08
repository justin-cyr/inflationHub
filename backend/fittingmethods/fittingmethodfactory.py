from .bestfit import *
from .spline import *

class FittingMethodFactory(object):

    @classmethod
    def create(cls, fitting_method_type, domainX, domainY):
        t = str(fitting_method_type)


        if t == 'PiecewiseLinear':
            return PiecewiseLinear(domainX, domainY)

        elif t == 'PiecewiseConstantLeftCts':
            return PiecewiseConstantLeftCts(domainX, domainY)

        elif t == 'PiecewiseConstantRightCts':
            return PiecewiseConstantRightCts(domainX, domainY)

        elif t == 'BestFitConstant':
            return BestFitConstant(domainX, domainY)

        else:
            raise ValueError(f'FittingMethodFactory: unrecognized fitting method type {t}.')
