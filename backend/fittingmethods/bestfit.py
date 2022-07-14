
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

    def dydx(self, x):
        return 0.0


class BestFitLinear(FittingMethod):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.linear_regression = None

    def __repr__(self):
        return f'BestFitLinear({self.domain_pair})'


    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        "Use OLS linear regression for best-fit line."
        import numpy as np
        from sklearn.linear_model import LinearRegression
        xs = np.array(xs).reshape(-1, 1)
        ys = np.array(ys)
        self.linear_regression = LinearRegression().fit(xs, ys)


    @FittingMethod.check_is_fit
    def predict(self, x):
        import numpy as np
        arr = np.array([x]).reshape(-1, 1)
        return self.linear_regression.predict(arr)[0]


    def dydx(self, x):
        return self.linear_regression.coef_[0]
