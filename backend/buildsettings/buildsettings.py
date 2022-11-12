
from .. import config as cfg
from ..curveconstruction import domains
from ..fittingmethods import fittingmethod as fm

def get_usage_by_model(model_str):
    """Return the usage of the build settings for this model string."""
    model_usage = {
        cfg.BONDCURVE: BuildSettingsBondCurve.get_usage,
        cfg.CPI: BuildSettingsCPICurve.get_usage,
        cfg.SEASONALITY: BuildSettingsSeasonality.get_usage
    }
    if model_str not in model_usage:
        raise ValueError(f'get_usage_by_model: unsupported model type {model_str}.')
    
    return model_usage[model_str]()


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
        """Return usage options for these BuildSettings. First choice is default."""
        return dict(
            domainX=[domains.UNASSIGNED],
            domainY=[domains.UNASSIGNED],
            fitting_method_str=['']
        )


class BuildSettingsCPICurve(BuildSettings):
    def __init__(self, domainX, domainY, fitting_method_str, t0_date=None):
        super().__init__(domainX, domainY, fitting_method_str)

        self.validate()

        if self.domainY in [domains.TIME_WEIGHTED_ZERO_RATE, domains.ZERO_RATE]:
            # t0_date is required
            if not t0_date:
                raise ValueError(f'BuildSettingsCPICurve: t0_date is required when domainY={self.domainY}.')
            
        self.t0_date = t0_date

    @classmethod
    def get_usage(cls):
        return dict(
            domainX=[
                domains.TIME_ACT_365,
                domains.TIME_30_360
                ],
            domainY=[
                domains.TIME_WEIGHTED_ZERO_RATE,
                domains.CPI_LEVEL,
                domains.ZERO_RATE
                ],
            fitting_method_str=[
                fm.PiecewiseLinear,
                fm.BestFitLinear,
                fm.BestFitConstant,
                fm.PiecewiseConstantLeftCts,
                fm.PiecewiseConstantRightCts
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


class BuildSettingsBondCurve(BuildSettings):
    def __init__(self, domainX, domainY, fitting_method_str, t0_date=None, opt_method=cfg.BFGS):
        super().__init__(domainX, domainY, fitting_method_str)
        self.validate()

        if self.domainY in [domains.TIME_WEIGHTED_ZERO_RATE, domains.ZERO_RATE]:
            # t0_date is required
            if not t0_date:
                raise ValueError(f'BuildSettingsBondCurve: t0_date is required when domainY={self.domainY}.')
            
        self.t0_date = t0_date
        self.opt_method = opt_method
    
    @classmethod
    def get_usage(cls):
        return dict(
            domainX=[
                domains.TIME_ACT_365,
                domains.TIME_30_360
                ],
            domainY=[
                domains.TIME_WEIGHTED_ZERO_RATE,
                domains.ZERO_RATE
                ],
            fitting_method_str=[
                fm.CubicSpline,
                fm.PiecewiseLinear,
                fm.BestFitLinear,
                fm.BestFitConstant,
                fm.PiecewiseConstantLeftCts,
                fm.PiecewiseConstantRightCts
                ],
            opt_method=[
                cfg.CG,
                cfg.BFGS,
                cfg.TRUST_CONSTR
            ]
            )
