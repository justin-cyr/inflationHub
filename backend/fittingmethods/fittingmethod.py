
from ..curveconstruction.domains import DomainPair

# String constants for fitting method names
BestFitConstant = 'BestFitConstant'
BestFitLinear = 'BestFitLinear'
PiecewiseLinear = 'PiecewiseLinear'
PiecewiseConstantLeftCts = 'PiecewiseConstantLeftCts'
PiecewiseConstantRightCts = 'PiecewiseConstantRightCts'


class FittingMethod(object):
    def __init__(self, domainX, domainY):
        self.domain_pair = DomainPair(domainX, domainY)
        self.is_fit = False


    def throw_if_not_fit(self):
        if not self.is_fit:
            raise RuntimeError('FittingMethod: has not been fit')
    

    def validate(self, xs, ys):
        try:
            xs = list(xs)
            ys = list(ys)
            
            if len(xs) != len(ys):
                raise ValueError('FittingMethod.fit: xs and ys must have the same length')

        except:
            raise TypeError('FittingMethod.fit: xs and ys must be list-like.')


    # decorator
    def set_is_fit(fit):
        def inner(self, xs, ys):
            fit(self, xs, ys)
            self.is_fit = True
        return inner
    
    # decorator
    def check_is_fit(predict):
        def inner(self, x):
            self.throw_if_not_fit()
            return predict(self, x)
        return inner


    @set_is_fit
    def fit(self, xs, ys):
        """Train the fitting method with data from the domain pair."""
        raise NotImplementedError('FittingMethod.fit: not implemented in base class.')

    
    @check_is_fit
    def predict(self, x):
        """Predict a y value given an x value."""
        raise NotImplementedError('FittingMethod.predict: not implemented in base class.')

    
    def difference_quotient(self, x, delta_x=1E-4):
        """Return the difference quotient (y(x + delta_x) - y(x) / (delta_x)."""
        if delta_x == 0:
            raise ValueError('FittingMethod.difference_quotient: delta_x cannot be 0.')

        # Derive class implements predict
        x0, x1 = x, x + delta_x
        y0, y1 = self.predict(x0), self.predict(x1)

        return (y1 - y0) / (x1 - x0)


    def dydx(self, x):
        """Return the derivative dy/dx at point x."""
        # Default implementation is a difference quotient with small step size
        return self.difference_quotient(x, delta_x=1E-8)

    def grad(self, x):
        """Return the gradient vector (df(x)/dy_1,...,df(x)/dy_n)"""
        raise NotImplementedError(f'{self.__class__.__name__}.{__name__}: not implemented in base class.')

    def hess(self, x):
        """Return the Hessian matrix [d^2f(x)/dy_idy_j]"""
        raise NotImplementedError(f'{self.__class__.__name__}.{__name__}: not implemented in base class.')
