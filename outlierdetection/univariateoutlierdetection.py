# -*- coding: utf-8 -*-
from abc import abstractmethod
from typing import List

import matplotlib.pyplot as pyplot
import numpy as np
import scipy.stats
from functools import lru_cache

from outlierdetection.outlierdetection import OutlierDetector


SIGNIFICANCE_LEVELS = [0.15, 0.1, 0.05, 0.025, 0.001]


class UnivariateOutlierDetector(OutlierDetector):
    def __init__(self, name):
        super().__init__(name)
        self.data: np.ndarray = None

    def init(self, data: np.ndarray):
        self.data = data

    @abstractmethod
    def marker_value(self):
        pass

    def is_outlier(self, val):
        return val >= self.upper_bound() or val <= self.lower_bound()

    @abstractmethod
    def lower_bound(self):
        pass

    @abstractmethod
    def upper_bound(self):
        pass

    def has_lower_bound(self):
        return self.lower_bound() >= 0

    def outliers(self) -> List:
        return list(filter(lambda d: d > self.upper_bound() or d < self.lower_bound(), self.data))

    def check_gaussian_distribution(self, arr, plot_hist=False):
        """
        TODO move
        Null hypothesis: x comes from a normal distribution

        Reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.normaltest.html#r7bf2e556f491-2
        scipy.stats.normaltest tests the null hypothesis that a sample comes from a normal distribution.
        Returns (statistic, pvalue)
        statistic: s^2 + k^2, where s is the z-score returned by skewtest and k is the z-score returned by kurtosistest.
        pvalue: A 2-sided chi squared probability for the hypothesis test.
        If the p-val is very small, it means it is unlikely that the data came from a normal distribution.

        TODO https://stats.stackexchange.com/questions/55691/regarding-p-values-why-1-and-5-why-not-6-or-10/55693#55693


        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.anderson.html
        """
        normaltest = scipy.stats.normaltest(arr)
        # Anderson test
        andersontest = scipy.stats.anderson(arr, dist='norm')

        if plot_hist:
            pyplot.hist(arr) # , bins='auto, density=True
            pyplot.title(f"{self.name} histogram")
            pyplot.show()

        return normaltest, andersontest


class BaseZScoreOutlierDetector(UnivariateOutlierDetector):
    def __init__(self, name, significance_lvl):
        super().__init__(name)
        self.significance_lvl = significance_lvl
        self.name = f"Z-Score ({significance_lvl} std dev)"

    @lru_cache(maxsize=1)
    def marker_value(self):
        """
        The marker value for Z-Score is defined as the mean.
        """
        m = np.mean(self.data, axis=0)
        assert not np.isnan(m), f"Mean should not be NaN, but was for {self.data}"
        return m

    @lru_cache(maxsize=1)
    def upper_bound(self):
        mean_val = self.marker_value()
        cut_off = self.standard_deviation() * self.significance_lvl
        return mean_val + cut_off

    @lru_cache(maxsize=1)
    def lower_bound(self):
        """
        TODO check for values lower 0, probably introduce a flag
        """
        mean_val = self.marker_value()
        cut_off = self.standard_deviation() * self.significance_lvl
        return mean_val - cut_off

    @lru_cache(maxsize=1)
    def standard_deviation(self):
        """
        TODO check ddof
        https://stackoverflow.com/questions/15389768/standard-deviation-of-a-list
        """
        return np.std(self.data, axis=0)

    def is_gaussian_distributed(self):
        knormaltest, andersontest = self.check_gaussian_distribution(self.nparr, plot_hist=True)
        reject_sign_lvl_kt = [(knormaltest.pvalue < sl, sl) for sl in SIGNIFICANCE_LEVELS]

        reject_sign_lvl_at = [(andersontest.statistic > cv, andersontest.significance_level[i]) for i, cv in
                           enumerate(andersontest.critical_values)]

        assert len(reject_sign_lvl_at) == len(reject_sign_lvl_kt)
        # This does not hold true in general, but I want to know, when it does not
        assert all(reject_sign_lvl_at[i] == reject_sign_lvl_kt[i] for i in range(len(reject_sign_lvl_at))),\
            "Anderson test and knormal test differ."

        return any(rs[0] for rs in reject_sign_lvl_at)


class ZScore1StdDevOutlierDetector(BaseZScoreOutlierDetector):
    SIGNIFICANCE_LEVEL = 1
    name = f"Z-Score ({SIGNIFICANCE_LEVEL} std dev)"

    def __init__(self):
        super().__init__(ZScore1StdDevOutlierDetector.name,
                         ZScore1StdDevOutlierDetector.SIGNIFICANCE_LEVEL)


class ZScore2StdDevOutlierDetector(BaseZScoreOutlierDetector):
    SIGNIFICANCE_LEVEL = 2
    name = f"Z-Score ({SIGNIFICANCE_LEVEL} std dev)"

    def __init__(self):
        super().__init__(ZScore2StdDevOutlierDetector.name,
                         ZScore2StdDevOutlierDetector.SIGNIFICANCE_LEVEL)


class ZScore3StdDevOutlierDetector(BaseZScoreOutlierDetector):
    SIGNIFICANCE_LEVEL = 3
    name = f"Z-Score ({SIGNIFICANCE_LEVEL} std dev)"

    def __init__(self):
        super().__init__(ZScore3StdDevOutlierDetector.name,
                         ZScore3StdDevOutlierDetector.SIGNIFICANCE_LEVEL)


class BaseModifiedZScoreOutlierDetector(UnivariateOutlierDetector):
    def __init__(self, name, significance_lvl):
        super().__init__(name)
        self.significance_lvl = significance_lvl
        self.name = f"Modified Z-Score ({significance_lvl} dev)"

    @lru_cache(maxsize=1)
    def marker_value(self):
        """
        The marker value for modified Z-Score is defined as the median.
        """
        m = np.median(self.data, axis=0)
        assert not np.isnan(m), f"Mean should not be NaN, but was for {self.data}"
        return m

    def mad(self):
        """
        Median absolute deviation
        http://colingorrie.github.io/outlier-detection.html
        """
        m = self.marker_value()
        return np.median([np.abs(y - m) for y in self.data])

    @lru_cache(maxsize=1)
    def upper_bound(self):
        cut_off = self.mad() * self.significance_lvl
        return self.marker_value() + cut_off

    @lru_cache(maxsize=1)
    def lower_bound(self):
        cut_off = self.mad() * self.significance_lvl
        return self.marker_value() - cut_off


class ModifiedZScore1DevOutlierDetector(BaseModifiedZScoreOutlierDetector):
    SIGNIFICANCE_LEVEL = 1
    name = f"Modified Z-Score ({SIGNIFICANCE_LEVEL} dev)"

    def __init__(self):
        super().__init__(ModifiedZScore1DevOutlierDetector.name,
                         ModifiedZScore1DevOutlierDetector.SIGNIFICANCE_LEVEL)


class ModifiedZScore2DevOutlierDetector(BaseModifiedZScoreOutlierDetector):
    SIGNIFICANCE_LEVEL = 2
    name = f"Modified Z-Score ({SIGNIFICANCE_LEVEL} dev)"

    def __init__(self):
        super().__init__(ModifiedZScore2DevOutlierDetector.name,
                         ModifiedZScore2DevOutlierDetector.SIGNIFICANCE_LEVEL)


class ModifiedZScore3DevOutlierDetector(BaseModifiedZScoreOutlierDetector):
    SIGNIFICANCE_LEVEL = 3
    name = f"Modified Z-Score ({SIGNIFICANCE_LEVEL} dev)"

    def __init__(self):
        super().__init__(ModifiedZScore3DevOutlierDetector.name,
                         ModifiedZScore3DevOutlierDetector.SIGNIFICANCE_LEVEL)


class IQROutlierDetector(UnivariateOutlierDetector):
    """
    http://colingorrie.github.io/outlier-detection.html
    """

    name = "IQR (Interquartile Range) (75th and 25th percentiles and 1.5 factor)"
    outlier_factor = 1.5
    lower_percentile = 25
    upper_percentile = 75

    def __init__(self):
        super().__init__(IQROutlierDetector.name)

    @lru_cache(maxsize=1)
    def marker_value(self):
        quartile_1, quartile_3 = np.percentile(self.data, [IQROutlierDetector.lower_percentile, IQROutlierDetector.upper_percentile])
        iqr = quartile_3 - quartile_1
        return iqr

    @lru_cache(maxsize=1)
    def lower_bound(self):
        quartile_1, quartile_3 = np.percentile(self.data, [IQROutlierDetector.lower_percentile, IQROutlierDetector.upper_percentile])
        iqr = quartile_3 - quartile_1
        lower_bound = quartile_1 - (iqr * IQROutlierDetector.outlier_factor)
        return lower_bound

    @lru_cache(maxsize=1)
    def upper_bound(self):
        quartile_1, quartile_3 = np.percentile(self.data, [IQROutlierDetector.lower_percentile, IQROutlierDetector.upper_percentile])
        iqr = quartile_3 - quartile_1
        upper_bound = quartile_3 + (iqr * IQROutlierDetector.outlier_factor)
        return upper_bound


UNIVARIATE_OUTLIER_DETECTORS = [
    IQROutlierDetector,  # Default
    ModifiedZScore2DevOutlierDetector,
    ModifiedZScore1DevOutlierDetector,
    ModifiedZScore3DevOutlierDetector,
    ZScore1StdDevOutlierDetector,
    ZScore2StdDevOutlierDetector,
    ZScore3StdDevOutlierDetector,
]

OUTLIER_NAME_INSTANCE_MAP = {
    ZScore1StdDevOutlierDetector.name: ZScore1StdDevOutlierDetector,
    ZScore2StdDevOutlierDetector.name: ZScore2StdDevOutlierDetector,
    ZScore3StdDevOutlierDetector.name: ZScore3StdDevOutlierDetector,
    ModifiedZScore1DevOutlierDetector.name: ModifiedZScore1DevOutlierDetector,
    ModifiedZScore2DevOutlierDetector.name: ModifiedZScore2DevOutlierDetector,
    ModifiedZScore3DevOutlierDetector.name: ModifiedZScore3DevOutlierDetector,
    IQROutlierDetector.name: IQROutlierDetector,
}
