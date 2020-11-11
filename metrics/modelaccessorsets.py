# -*- coding: utf-8 -*-
from analysis import correlations, distribution, usecaseanalysis, playstorecorrelations
from metrics.appcomparison import uimetrics
from metrics.ucecomparison import staticmetrics, playstoremetrics
from metrics import ucecomparison


MODEL_ACCESSORS_ALL = [
    # UI
    uimetrics.UIInteractableVisibleWidgetsNumber,
    # Analysis
    usecaseanalysis.UseCaseOverview,
    usecaseanalysis.AppsUseCaseExecutionsOverview,
    usecaseanalysis.UseCaseExecutionsAppsOverview,
    correlations.CorrelationsMetricAppAL,
    correlations.UseCaseCorrelations,
    playstorecorrelations.PlayStoreCorrelationsMetricAppAL,
    distribution.Distribution,

    # Static
    staticmetrics.StaticPermissionsNumber,
    staticmetrics.StaticPermissionsDistributionAmongApps,
    staticmetrics.StaticAppPermissionsDistributionAmongPermissions,
    # staticmetrics.StaticReceiversNumber,
    # staticmetrics.StaticVersionNumber,
    staticmetrics.StaticAdTrackingLibraryNumber,
    # staticmetrics.StaticPackageSize,
    # metrics
    ucecomparison.modelmetrics.ModelGraphs,
    ucecomparison.modelmetrics.ModelNodesNumber,
    ucecomparison.modelmetrics.ModelEdgesNumber,
    # ucecomparison.modelmetrics.ModelIndegree,
    # ucecomparison.modelmetrics.ModelOutdegree,
    ucecomparison.modelmetrics.ModelNodeConnectivity,
    ucecomparison.modelmetrics.ModelEdgeConnectivity,
    ucecomparison.modelmetrics.ModelAvgGraphDepth,
    # ucecomparison.modelmetrics.ModelMaxGraphDepth,
    # ucecomparison.modelmetrics.ModelAvgShortestPathLength,
    ucecomparison.modelmetrics.ModelDensity,
    ucecomparison.networkmetrics.NetworkRequestsNumberUCE,
    ucecomparison.networkmetrics.NetworkRequestsNumberApp,
    ucecomparison.networkmetrics.NetworkLatencyUCE,
    ucecomparison.networkmetrics.NetworkLatencyApp,
    ucecomparison.networkmetrics.NetworkNumberErrors,
    ucecomparison.networkmetrics.NetworkPayloadSizeRequestUCE,
    ucecomparison.networkmetrics.NetworkPayloadSizeRequestApp,
    ucecomparison.networkmetrics.NetworkPayloadSizeResponseUCE,
    ucecomparison.networkmetrics.NetworkPayloadSizeResponseApp,
    ucecomparison.buttonmetrics.ButtonButtonsNumberUCE,
    ucecomparison.buttonmetrics.ButtonButtonsNumberApp,
    ucecomparison.buttonmetrics.ButtonAreaUCE,
    ucecomparison.buttonmetrics.ButtonAreaApp,
    ucecomparison.featuremetrics.FeatureNumber,
    ucecomparison.uimetrics.UIInteractableVisibleWidgetsNumber,
    ucecomparison.usecasemetrics.UseCaseLengthUseCaseExecutions,
    ucecomparison.usecasemetrics.UseCaseComputedUseCaseExecutionsNumber,
    ucecomparison.usecasemetrics.UseCaseVerifiedUseCaseExecutionsNumber,
    ucecomparison.usecasemetrics.UseCaseRatioVerifiedComputedUseCaseExecutionsNumber,
    ucecomparison.undesiredbehaviormetrics.UndesiredBehaviorCrashNumber,
    # Play store
    playstoremetrics.PlayStoreRating,
    playstoremetrics.PlayStoreReviewNumber,
    playstoremetrics.PlayStoreInstallationNumber,
]

METRICS_STATIC = [
    # Static
    staticmetrics.StaticPermissionsNumber,
    # staticmetrics.StaticReceiversNumber,
    staticmetrics.StaticPermissionsDistributionAmongApps,
    staticmetrics.StaticAppPermissionsDistributionAmongPermissions,
    staticmetrics.StaticAdTrackingLibraryNumber,
    staticmetrics.StaticPackageSize,
]

METRICS_BASIC = METRICS_STATIC + [
    ucecomparison.modelmetrics.ModelGraphs,
]
