
from ..curveconstruction.domains import DomainPair

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
