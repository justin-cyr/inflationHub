
import numpy as np

from .fittingmethod import FittingMethod

class BestFitConstant(FittingMethod):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.constant = None
        self.training_len = None
        self.gradient = None
        self.hessian = None

    def __repr__(self):
        return f'BestFitConstant({self.domain_pair.domainY})'


    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        # take the average
        if not ys:
            raise ValueError('BestFitConstant.fit: ys must be list of at least 1 point.')

        self.training_len = len(ys)
        self.constant = sum(ys) / self.training_len


    @FittingMethod.check_is_fit
    def predict(self, x=0):
        return self.constant

    def dydx(self, x):
        return 0.0

    def grad(self, x):
        if self.gradient is not None:
            return self.gradient
        
        self.gradient = np.array([1.0 / self.training_len for _ in range(self.training_len)])
        return self.gradient

    def hess(self, x):
        if self.hessian is not None:
            return self.hessian

        dim = self.training_len
        self.hessian = [[0.0 for _ in range(dim)] for _ in range(dim)]
        return self.hessian


class BestFitLinear(FittingMethod):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.linear_regression = None
        self.training_len = None
        self.xs = None
        self.pinv = None
        self.hessian = None

    def __repr__(self):
        return f'BestFitLinear({self.domain_pair})'


    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        "Use OLS linear regression for best-fit line."
        import numpy as np
        from sklearn.linear_model import LinearRegression
        self.xs = xs
        self.training_len = len(self.xs)
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

    def grad(self, x):
        if self.pinv is not None:
            return x * self.pinv[0] + self.pinv[1]
        
        # gradient is found using the Moore-Penrose pseudoinverse of the predictor variables
        from scipy.linalg import pinv
        predict_vars = [[pt, 1.0] for pt in self.xs]
        self.pinv = pinv(predict_vars)
        return x * self.pinv[0] + self.pinv[1]
    
    def hess(self, x):
        if self.hessian is not None:
            return self.hessian

        dim = self.training_len
        self.hessian = [[0.0 for _ in range(dim)] for _ in range(dim)]
        return self.hessian
