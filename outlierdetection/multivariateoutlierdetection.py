# -*- coding: utf-8 -*-
import numpy as np
from sklearn.neighbors import LocalOutlierFactor

from outlierdetection.outlierdetection import OutlierDetector

# TODO this could be interesting
# https://medium.com/learningdatascience/anomaly-detection-techniques-in-python-50f650c75aaf


class KNNOutlierDetector(OutlierDetector):
    """
    Unsupervised Outlier Detection using Local Outlier Factor (LOF)
    https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html
    "The anomaly score of each sample is called Local Outlier Factor. It measures the local deviation of density of a
    given sample with respect to its neighbors. It is local in that the anomaly score depends on how isolated the object
    is with respect to the surrounding neighborhood. More precisely, locality is given by k-nearest neighbors, whose
    distance is used to estimate the local density. By comparing the local density of a sample to the local densities
    of its neighbors, one can identify samples that have a substantially lower density than their neighbors. These are
    considered outliers."
    """

    name = "K-Nearest-Neighbour"

    def __init__(self, multi_arr_data, k=4):
        """
        TODO play around with k
        """
        super().__init__(KNNOutlierDetector.name)
        self.multi_arr_data = multi_arr_data
        self.X = np.transpose(np.array(self.multi_arr_data))
        # self.X = np.array(multi_arr_data_transposed)
        self.k = k
        self.clf = LocalOutlierFactor(n_neighbors=self.k, contamination=0.1)
        self.y_pred = self.clf.fit_predict(self.X)
        self.X_scores = self.clf.negative_outlier_factor_
