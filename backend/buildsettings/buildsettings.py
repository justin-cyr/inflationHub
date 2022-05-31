
from ..curveconstruction import domains

class BuildSettings(object):
    def __init__(self, domainX, domainY, fitting_method_str=''):
        self.domainX = domainX
        self.domainY = domainY
        self.fitting_method_str = fitting_method_str

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(self.__dict__) + ')'

    def validate(self):
        d = self.get_usage()
        for k, v in self.__dict__.items():
            if k in d and v not in d[k]:
                raise ValueError(f'BuildSettings: option {k}={v} is not in supported choices {d[k]}.')
            
    @classmethod
    def get_usage(cls):
        """Return usage options for these BuildSettings."""
        return dict(
            domainX=[domains.UNASSIGNED],
            domainY=[domains.UNASSIGNED],
            fitting_method_str=['']
        )


class BuildSettingsCPICurve(BuildSettings):
    def __init__(self, domainX, domainY, fitting_method_str):
        super().__init__(domainX, domainY, fitting_method_str)

        self.validate()


    @classmethod
    def get_usage(cls):
        return dict(
            domainX=[
                domains.TIME_ACT_365,
                domains.TIME_30_360
                ],
            domainY=[
                domains.CPI_LEVEL,
                domains.TIME_WEIGHTED_ZERO_RATE,
                domains.ZERO_RATE
                ],
            fitting_method_str=[
                'BestFitConstant',
                'PiecewiseLinear',
                'PiecewiseConstantLeftCts',
                'PiecewiseConstantRightCts'
                ]
            )


class BuildSettingsSeasonality(BuildSettings):
    def __init__(self, domainX, domainY):
        super().__init__(domainX, domainY)

        self.validate()

    @classmethod
    def get_usage(cls):
        return dict(
            domainX=[
                domains.MONTH
                ],
            domainY=[
                domains.ADDITIVE_SEASONALITY
                ]
            )
