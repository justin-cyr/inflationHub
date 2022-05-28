
from .fittingmethod import FittingMethod

class Spline(FittingMethod):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.pairs = None
        self.x_min = None
        self.x_max = None

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
        # binary search
        left = 0
        right = len(self.pairs)

        while left + 1 < right:
            mid = (left + right) // 2
            x, _ = self.pairs[mid]
            
            if target < x:
                right = mid
            else:
                left = mid

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


class PiecewiseConstantRightCts(Spline):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)

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


class PiecewiseLinear(Spline):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)
        self.slopes = None

    def __repr__(self):
        return f'PiecewiseLinear({self.domain_pair})'


    @FittingMethod.set_is_fit
    def fit(self, xs, ys):
        super().fit(xs, ys)
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
            
        
