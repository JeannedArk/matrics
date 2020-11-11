# -*- coding: utf-8 -*-
import json
import os
from functools import lru_cache
from typing import Dict, List, Tuple, Set

from aggregationlevel import AggregationLevel
from jsonencoder import DataCompoundEncoder, DataCompoundDumpEncoder
from jsonexportable import JsonExportable
from util import statisticsutil


class DataCompound(JsonExportable):
    def __init__(self,
                 metric,
                 chart_base_title: str,
                 data: Dict,
                 aggregation_lvl,
                 outlier_method,
                 use_case_name=None):
        self.chart_base_title = chart_base_title
        self.data = data
        self.aggregation_lvl = aggregation_lvl
        self.outlier_method = outlier_method
        self.use_case_name = use_case_name
        # Metric attributes
        self.id = metric.get_id()
        self.short_id = metric.get_short_id()
        self.name = metric.name
        self.description = metric.description

    def __repr__(self) -> str:
        return f"DataCompound({self.get_aggregation_level_str()}, metric={self.name})"

    def get_id(self):
        return self.id

    def get_id_2(self) -> str:
        aggr = self.get_aggregation_level_str().replace(" ", "-").replace("(", "").replace(")", "")
        return f"{self.id}-{aggr}"

    def get_short_id(self):
        return self.short_id

    def get_name(self) -> str:
        return self.name

    def get_title(self) -> str:
        return f"{self.description}, Aggr. level: TODO"

    def get_aggregation_level(self):
        return self.aggregation_lvl

    def get_aggregation_level_str(self) -> str:
        if self.aggregation_lvl == AggregationLevel.APP:
            return "App"
        elif self.aggregation_lvl == AggregationLevel.USE_CASE:
            return f"Use Case ({self.use_case_name})"
        elif self.aggregation_lvl == AggregationLevel.STATE:
            return "State"
        else:
            raise NotImplementedError("")

    @lru_cache(maxsize=1)
    def get_data(self) -> List:
        vals = []
        items = self.data.items()
        for app_package_name, data in items:
            if type(data) == list:
                for d in data:
                    vals.append(d)
        return vals

    @staticmethod
    def get_info_header(prefix, vals, app_package_names_w_valid_data):
        return f"{prefix} [{len(app_package_names_w_valid_data)}]"
        # shapiro_p_value: str = ""
        # anderson_exp = ""
        # try:
        #      shapiro_p_value = statisticsutil.get_shapiro_p_value(vals)
        # except:
        #     shapiro_p_value = "NaN"
        # try:
        #     anderson_exp = statisticsutil.is_exponential_distributed(vals)
        # except:
        #     anderson_exp = "Inv"
        # return f"{prefix} [{shapiro_p_value}, {anderson_exp}] [{len(app_package_names_w_valid_data)}]"

    def get_data_w_labels(self) -> Tuple[List, List]:
        indices = []
        vals = []
        items = self.data.items()
        app_package_names_w_valid_data = set()
        for app_package_name, data in items:
            if type(data) == list:
                app_package_names_w_valid_data.add(app_package_name)
                for d in data:
                    indices.append(app_package_name)
                    vals.append(d)
        assert len(indices) == len(vals), f"Indices: {len(indices)} Vals: {len(vals)}"

        return indices, vals

    def get_vals_and_packages(self) -> Tuple[List, Set]:
        vals = []
        items = self.data.items()
        app_package_names_w_valid_data = set()
        for app_package_name, data in items:
            if type(data) == list:
                app_package_names_w_valid_data.add(app_package_name)
                for d in data:
                    vals.append(d)

        return vals, app_package_names_w_valid_data

    def get_chart_title(self) -> str:
        prefix = ""
        if self.aggregation_lvl == AggregationLevel.APP:
            prefix = self.chart_base_title
        elif self.aggregation_lvl == AggregationLevel.USE_CASE:
            prefix = f"Use Case ({self.chart_base_title})"
        else:
            raise NotImplementedError("Not implemented yet")

        vals, app_package_names_w_valid_data = self.get_vals_and_packages()
        return DataCompound.get_info_header(prefix, vals, app_package_names_w_valid_data)

    def to_json(self) -> str:
        dc_dump = DataCompoundDump.construct(self)
        return json.dumps(dc_dump, cls=DataCompoundEncoder, indent=4, sort_keys=True)


class DataCompoundDump(JsonExportable):
    def __init__(self,
                 chart_base_title: str,
                 data: Dict,
                 aggregation_lvl: str,
                 use_case_name,
                 _id,
                 short_id,
                 name,
                 description,
                 chart_title):
        self.chart_base_title = chart_base_title
        self.data = data
        self.aggregation_lvl: str = aggregation_lvl
        self.use_case_name = use_case_name
        self.id = _id
        self.short_id = short_id
        self.name = name
        self.description = description
        self.chart_title = chart_title

    def __repr__(self) -> str:
        return self.to_json()

    def to_json(self) -> str:
        return json.dumps(self, cls=DataCompoundDumpEncoder, indent=4, sort_keys=True)

    @staticmethod
    def construct(data_comp: DataCompound):
        return DataCompoundDump(chart_base_title=data_comp.chart_base_title,
                                data=data_comp.data,
                                aggregation_lvl=data_comp.get_aggregation_level_str(),
                                use_case_name=data_comp.use_case_name,
                                _id=data_comp.get_id_2(),
                                short_id=data_comp.short_id,
                                name=data_comp.name,
                                description=data_comp.description,
                                chart_title=data_comp.get_chart_title())

    @staticmethod
    def construct_from_json(json_dict):
        return DataCompoundDump(chart_base_title=json_dict['chart_base_title'],
                                data=json_dict['data'],
                                aggregation_lvl=json_dict['aggregation_lvl'],
                                use_case_name=json_dict['use_case_name'],
                                _id=json_dict['id'],
                                short_id=json_dict['short_id'],
                                name=json_dict['name'],
                                description=json_dict['description'],
                                chart_title=json_dict['chart_title'])

    @staticmethod
    def dump_as_json_from_data_compound(data_comp: DataCompound, target_dir):
        dcd = DataCompoundDump.construct(data_comp)
        dcd.dump_as_json(target_dir)

    def dump_as_json(self, target_dir):
        f_name = f"{self.id}.json"
        path = os.path.join(target_dir, f_name)
        with open(path, 'w') as outfile:
            json.dump(self, outfile, cls=DataCompoundDumpEncoder, indent=4, sort_keys=True)

    def get_chart_title(self) -> str:
        return self.chart_title

    def get_aggregation_level_str(self) -> str:
        return self.aggregation_lvl

    def get_id_2(self) -> str:
        return self.id
