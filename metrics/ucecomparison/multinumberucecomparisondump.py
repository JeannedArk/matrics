# -*- coding: utf-8 -*-
from typing import List

from metrics.datacompound import DataCompound, DataCompoundDump
from plotconfiguration import PlotConfiguration, PlotConfigurationDump


class MultiNumberUCEComparisonDump(object):
    def __init__(self,
                 aggregation_lvls: List[str],
                 data_compounds: List[DataCompound],
                 description,
                 metric_id,
                 plot_config: PlotConfiguration,
                 use_case_whitelist):
        self.aggregation_lvls: List[str] = aggregation_lvls
        self.data_compounds: List[DataCompoundDump] = [DataCompoundDump.construct(dc) for dc in data_compounds]
        self.description = description
        self.metric_id = metric_id
        self.plot_config: PlotConfigurationDump = PlotConfigurationDump.construct(plot_config)
        self.use_case_whitelist = use_case_whitelist

    @staticmethod
    def construct(multinumber):
        return MultiNumberUCEComparisonDump(aggregation_lvls=[str(aggr_lvl.name) for aggr_lvl in multinumber.aggregation_lvls],
                                            data_compounds=multinumber.data_compounds,
                                            description=multinumber.description,
                                            metric_id=multinumber.get_id(),
                                            plot_config=multinumber.plot_config,
                                            use_case_whitelist=multinumber.use_case_whitelist)

    @staticmethod
    def construct_from_json(json_dict):
        data_comps = [DataCompoundDump.construct_from_json(j) for j in json_dict['data_compounds']]
        plot_config = PlotConfigurationDump.construct_from_json(json_dict['plot_config'])
        return MultiNumberUCEComparisonDump(aggregation_lvls=json_dict['aggregation_lvls'],
                                            data_compounds=data_comps,
                                            description=json_dict['description'],
                                            metric_id=json_dict['metric_id'],
                                            plot_config=plot_config,
                                            use_case_whitelist=json_dict['use_case_whitelist'])
