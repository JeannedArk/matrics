# -*- coding: utf-8 -*-


# class CombinedStatic1(MetricAggregator):
#     description = "Combined static 1"
#     aggregation_lvls = [AggregationLevel.STATE, AggregationLevel.APP]
#
#     def __init__(self,
#                  model,
#                  filtering_widgets=lambda widgets: filter_buttons(widgets),
#                  description=description,
#                  outlier_method=ZScore1StdDevOutlierDetector):
#         super().__init__(model=model,
#                          filtering_op=filtering_widgets,
#                          data_op=data_frame_mean,
#                          data_select_op=selector_number_of_widgets,
#                          aggregation_lvls=ButtonAvgButtonsNumber.aggregation_lvls,
#                          description=description,
#                          outlier_method=outlier_method)
#
#
#
# class ModelKNNClustering(BaseMetric, outlierdetection.OutlierDetector):
#     """
#     Unsupervised Outlier Detection using Local Outlier Factor (LOF)
#     https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.LocalOutlierFactor.html
#     """
#     description = 'Unsupervised k-Nearest neighbors clustering using LOF (k_edge_connectivity, k_vertex_connectivity, ' \
#                   'density, num nodes, num edges)'
#
#     def __init__(self, model, outlier_method=None):
#         # TODO figure out k
#         apps = model.apps
#         k = len(apps)
#         print(f"apps: {apps}  k: {k}")
#         clf = LocalOutlierFactor(n_neighbors=k, contamination=0.1)
#         self.X = np.array([[app.exploration_model.k_edge_connectivity(),
#                             app.exploration_model.k_vertex_connectivity(),
#                             app.exploration_model.density(),
#                             app.exploration_model.num_nodes(),
#                             app.exploration_model.num_edges(),
#                             ] for app in apps])
#
#         try:
#             self.y_pred = clf.fit_predict(self.X)
#             self.X_scores = clf.negative_outlier_factor_
#         except ValueError:
#             # This happens if we our sample size is too small, but we will just ignore it
#             pass
#         super().__init__(model,
#                          ModelKNNClustering.description,
#                          AggregationLevel.APP.iter_instance(model),
#                          self)
#
#     def plotly(self):
#         # Create color maps
#         cmap_light = [[0, '#FFAAAA'], [0.5, '#AAFFAA'], [1, '#AAAAFF']]
#         cmap_bold = [[0, '#FF0000'], [0.5, '#00FF00'], [1, '#0000FF']]
#
#         data = [go.Scatter(x=self.X[:, 1],
#                            y=self.X[:, 2],
#                            text=self.app_names,
#                            mode='markers',
#                            marker=dict(color=self.X[:, 0],
#                                        colorscale=cmap_bold,
#                                        line=dict(color='black', width=1))
#         )]
#
#         layout = go.Layout(
#             title="k-Nearest neighbors clustering",
#             height=700,
#             hovermode='closest',
#             showlegend=False
#         )
#
#         return dcc.Graph(id=ModelKNNClustering.ui_id,
#                          config=dict(displayModeBar=False),
#                          figure=dict(data=data, layout=layout))
