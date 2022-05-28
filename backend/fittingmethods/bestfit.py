
from .fittingmethod import FittingMethod

class BestFitConstant(FittingMethod):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.constant = None


    def __repr__(self):
        return f'BestFitConstant({self.domain_pair.domainY})'


    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        # take the average
        if not ys:
            raise ValueError('BestFitConstant.fit: ys must be list of at least 1 point.')

        self.constant = sum(ys) / len(ys)


    @FittingMethod.check_is_fit
    def predict(self, x=0):
        return self.constant
