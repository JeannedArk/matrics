# -*- coding: utf-8 -*-

from numpy import array
from matplotlib import pyplot
from statsmodels.stats.power import TTestIndPower


def plot_power_curve():
    """
    https://www.statsmodels.org/stable/generated/statsmodels.stats.power.TTestIndPower.plot_power.html
    https://github.com/statsmodels/statsmodels/blob/master/statsmodels/stats/power.py
    """
    significance_value = 0.05
    effect_size = 0.8
    statistical_power = 0.8

    # calculate power curves for varying sample and effect size

    # parameters for power analysis
    # effect_sizes = array([0.2, 0.5, 0.8])
    effect_sizes = array([effect_size])
    sample_sizes = array(range(7, 100))
    # calculate power curves from multiple power analyses
    analysis = TTestIndPower()
    analysis.plot_power(dep_var='nobs',
                        alpha=significance_value,
                        nobs=sample_sizes,
                        effect_size=effect_sizes,
                        title="")
    # fig = pyplot.gcf()
    pyplot.ylabel('Statistical power')
    pyplot.show()


if __name__ == '__main__':
    plot_power_curve()
