
import numpy as np
from scipy.interpolate import CubicSpline as scipyCubicSpline

from .fittingmethod import FittingMethod

class Spline(FittingMethod):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.pairs = None
        self.x_min = None
        self.x_max = None
        self.num_nodes = None
        self.time_index_cache = {}

    def is_between_endpoints(self, x):
        return (self.x_min <= x) and (x <= self.x_max)

    def throw_if_out_of_range(self, x):
        if not self.is_between_endpoints(x):
            raise ValueError(f'x={x} is out of Spline interpolation range [{self.x_min}, {self.x_max}]')

    # decorator
    def check_if_out_of_range(predict):
        def inner(self, x):
            self.throw_if_out_of_range(x)
            return predict(self, x)
        return inner


    @check_if_out_of_range
    def find_node_index_below(self, target):
        """Return the index of the spline node with the largest x that is <= target."""
        if target in self.time_index_cache:
            return self.time_index_cache[target]
        
        # binary search
        left = 0
        right = self.num_nodes

        while left + 1 < right:
            mid = (left + right) // 2
            x, _ = self.pairs[mid]
            
            if target < x:
                right = mid
            else:
                left = mid

        self.time_index_cache[target] = left
        return left


    def find_node_index_above(self, target):
        """Return the index of the spline node with the smallest x that is >= target."""
        i = self.find_node_index_below(target)
        xi, _ = self.pairs[i]
        if target == xi:
            return i
        else:
            return i + 1


    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        self.validate(xs, ys)
        xs = [float(x) for x in xs]
        ys = [float(y) for y in ys]

        self.pairs = sorted(zip(xs, ys), key=lambda x: x[0])
        self.x_min = self.pairs[0][0]
        self.x_max = self.pairs[-1][0]
        self.num_nodes = len(self.pairs)

        # ensure strictly increasing
        x_last = self.x_min
        for x, _ in self.pairs[1:]:
            if x == x_last:
                raise ValueError(f'Spline.fit: x values must be strictly increasing. Got multiple x={x}.')
            x_last = x


    @FittingMethod.check_is_fit
    def predict(self, x):
        raise NotImplementedError('Spline.predict: not implemented in base class')


class PiecewiseConstantLeftCts(Spline):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.hessian = None

    def __repr__(self):
        return f'PiecewiseConstantLeftCts({self.domain_pair})'

    @FittingMethod.check_is_fit
    def predict(self, x):
        # natural extrapolation
        if x <= self.x_min:
            return self.pairs[0][1]
        if x > self.x_max:
            return self.pairs[-1][1]

        # binary search, take left endpoint
        i = self.find_node_index_above(x)
        _, y = self.pairs[i]
        return y

    def dydx(self, x):
        return 0.0

    def grad(self, x):
        vec = [0.0 for _ in self.pairs]
        if x <= self.x_min:
            vec[0] = 1.0
            return vec
        if x > self.x_max:
            vec[-1] = 1.0
            return vec
        
        i = self.find_node_index_above(x)
        vec[i] = 1.0
        return np.array(vec)

    def hess(self, x):
        if self.hessian is not None:
            return self.hessian

        dim = self.num_nodes
        self.hessian = np.zeros((dim, dim))
        return self.hessian

class PiecewiseConstantRightCts(Spline):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.hessian = None

    def __repr__(self):
        return f'PiecewiseConstantRightCts({self.domain_pair})'

    @FittingMethod.check_is_fit
    def predict(self, x):
        # natural extrapolation
        if x < self.x_min:
            return self.pairs[0][1]
        if x >= self.x_max:
            return self.pairs[-1][1]
        
        # binary search, take right endpoint
        i = self.find_node_index_below(x)
        _, y = self.pairs[i]
        return y

    def dydx(self, x):
        return 0.0

    def grad(self, x):
        vec = [0.0 for _ in self.pairs]
        if x <= self.x_min:
            vec[0] = 1.0
            return vec
        if x > self.x_max:
            vec[-1] = 1.0
            return np.array(vec)
        
        i = self.find_node_index_below(x)
        vec[i] = 1.0
        return vec

    def hess(self, x):
        if self.hessian is not None:
            return self.hessian

        dim = self.num_nodes
        self.hessian = np.zeros((dim, dim))
        return self.hessian

class PiecewiseLinear(Spline):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.slopes = None
        self.hessian = None

    def __repr__(self):
        return f'PiecewiseLinear({self.domain_pair})'


    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        super().fit(xs, ys)
        if len(xs) < 2:
            raise ValueError(f'PiecewiseLinear.fit: requires at least 2 points but got xs={xs}, ys={ys}.')
        self.slopes = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(len(ys) - 1)]


    @FittingMethod.check_is_fit
    def predict(self, x):
        # natural extrapolation
        if x < self.x_min:
            x0, y0 = self.pairs[0]
            return y0 + self.slopes[0] * (x - x0)

        if x >= self.x_max:
            xn, yn = self.pairs[-1]
            return yn + self.slopes[-1] * (x - xn)

        # linear interpolation
        i = self.find_node_index_below(x)
        xi, yi = self.pairs[i]
        return yi + self.slopes[i] * (x - xi)
            
    
    def dydx(self, x):
        # natural extrapolation
        if x < self.x_min:
            return self.slopes[0]

        if x >= self.x_max:
            return self.slopes[-1]

        # linear interpolation
        i = self.find_node_index_below(x)
        return self.slopes[i]

    def grad(self, x):
        if x < self.x_min:
            i = 0
        elif x >= self.x_max:
            i = self.num_nodes - 2
        else:
            i = self.find_node_index_below(x)
        
        xi, _ = self.pairs[i]
        xiplus1, _ = self.pairs[i + 1]
        run = xiplus1 - xi

        vec = [0.0 for _ in self.pairs]
        vec[i] = (xiplus1 - x) / run
        vec[i + 1] = (x - xi) / run

        return np.array(vec)

    def hess(self, x):
        if self.hessian is not None:
            return self.hessian

        dim = len(self.pairs)
        self.hessian = np.zeros((dim, dim))
        return self.hessian


class CubicSpline(Spline):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.interpolator = None
        self.interpolator_prime = None

    def __repr__(self):
        return f'{self.__class__.__name__}({self.domain_pair})'
    
    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        super().fit(xs, ys)
        xs = np.array([p[0] for p in self.pairs])
        ys = np.array([p[1] for p in self.pairs])
        self.interpolator = scipyCubicSpline(xs, ys, bc_type='not-a-knot', extrapolate=True)

    @FittingMethod.check_is_fit
    def predict(self, x):
        return self.interpolator(x)
    
    def dydx(self, x):
        if self.interpolator_prime is None:
            self.interpolator_prime = self.interpolator.derivative(1)
        return float(np.asscalar(self.interpolator_prime(x)))
