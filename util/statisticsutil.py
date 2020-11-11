# -*- coding: utf-8 -*-
import numpy as np
import scipy
from scipy.stats import stats
from scipy import stats
from scipy.stats import kendalltau, pearsonr, spearmanr
import pandas as pd

from util import util
from util.latexutil import texify


STATISTICAL_SIGNIFICANCE_VALUE_ALPHA = 0.05


def calc_hamming_score(y_true: np.ndarray, y_pred: np.ndarray):
    """
    Compute the Hamming score (a.k.a. label-based accuracy) for the multi-label case
    http://stackoverflow.com/q/32239577/395857
    """
    acc_list = []
    for i in range(y_true.shape[0]):
        set_true = set(np.where(y_true[i])[0])
        set_pred = set(np.where(y_pred[i])[0])
        # print('\nset_true: {0}'.format(set_true))
        # print('set_pred: {0}'.format(set_pred))
        if not set_true and not set_pred:
            tmp_a = 1
        else:
            tmp_a = len(set_true.intersection(set_pred)) / float(len(set_true.union(set_pred)))
        # print('tmp_a: {0}'.format(tmp_a))
        acc_list.append(tmp_a)
    return np.mean(acc_list)


def get_q_1(data):
    return np.percentile(data, 25)


def get_q_2(data):
    return np.percentile(data, 50)


def get_q_3(data):
    return np.percentile(data, 75)


def get_shapiro_p_value(data) -> str:
    stat, p = stats.shapiro(data)
    return util.shorten_fl(p)


def is_exponential_distributed(vals) -> bool:
    """
    Null hypothesis: x comes from an exponential distribution

    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.anderson.html
    If the returned statistic is larger than these critical values then for the corresponding significance level,
    the null hypothesis that the data come from the chosen distribution can be rejected.
    """
    andersontest = scipy.stats.anderson(vals, dist='expon')
    assert len(andersontest.statistic) == len(andersontest.significance_level),\
        f"Statistic: {len(andersontest.statistic)} Significance lvl: {len(andersontest.significance_level)}"
    for i, sig_lvl in enumerate(andersontest.significance_level):
        if sig_lvl == STATISTICAL_SIGNIFICANCE_VALUE_ALPHA:
            reject = andersontest.statistic <= andersontest.critical_values[i]
            return reject
    raise AssertionError("Did not find a significance value")

    # reject_sign_lvl = [(andersontest.statistic <= cv, andersontest.significance_level[i]) for i, cv in
    #                    enumerate(andersontest.critical_values)]
    # return any(rs[0] for rs in reject_sign_lvl)


def pval_kendall(x, y):
    return kendalltau(x, y)[1]


def pval_pearsonr(x, y):
    return pearsonr(x, y)[1]


def pval_spearmanr(x, y):
    return spearmanr(x, y)[1]


def get_corresponding_pval_function(method: str):
    if method == "pearson":
        return pval_pearsonr
    elif method == "spearman":
        return pval_spearmanr
    elif method == "kendall":
        return pval_kendall
    else:
        raise NotImplementedError(f"Unknown method: {method}")


def calc_correlation_matrix(df: pd.DataFrame, method: str, labels_column_white_list=None) -> pd.DataFrame:
    corr = df.corr(method=method)
    labels = df.columns.values
    method_p_val_func = get_corresponding_pval_function(method)
    p_values = df.corr(method=method_p_val_func)

    for l_row in labels:
        for l_col in labels:
            p_val = p_values[l_row][l_col]
            if p_val > STATISTICAL_SIGNIFICANCE_VALUE_ALPHA:
                corr[l_row][l_col] = np.NAN

    if labels_column_white_list is not None:
        for label in labels:
            if label not in labels_column_white_list:
                corr.drop(label, axis=0, inplace=True)

    return corr


def coeff_variance(data):
    return stats.variation(data)


def coeff_quartile_variation(data):
    return (get_q_3(data) - get_q_1(data)) / (get_q_3(data) + get_q_1(data))


def descriptive_statistics_latex_header():
    return "Sample Size & Mean & Q2 & Q1 & Q3 & CQV & Range & LF & UF"


def descriptive_statistics_latex_row(data):
    """
    Univariate analysis involves describing the distribution of a single variable,
    including its central tendency (including the mean, median, and mode)
    and dispersion (including the range and quartiles of the data-set, and measures of spread such as the variance and standard deviation)

    Variance use ddof = 1:
    However, variance is the square of the std dev, huge values -> drop it
    https://realpython.com/python-statistics/

    mean, Q_2 (median), Q_1, Q_3, 1 std deviation, range, coefficient of variance
    """
    sample_size = len(data)

    mean = np.mean(data)
    median = np.median(data)
    q_1 = get_q_1(data)
    q_2 = get_q_2(data)
    q_3 = get_q_3(data)

    # mode = stats.mode(data)
    # std_dev = np.std(data, axis=0)
    # var = np.var(data, ddof=1)
    range_ = np.ptp(data)
    # coef_var = coeff_variance(data)
    coef_qartile_var = coeff_quartile_variation(data)
    # _, sw_p_value = scipy.stats.shapiro(data)

    # Upper fence
    lf = q_1 - 1.5 * (q_3 - q_1)
    # Lower fence
    uf = q_3 + 1.5 * (q_3 - q_1)

    return f"{texify(sample_size)} & {texify(mean)} & {texify(q_2)} & {texify(q_1)} & {texify(q_3)} " \
           f"& {texify(coef_qartile_var)} & {texify(range_)} & {texify(lf)} & {texify(uf)}"
