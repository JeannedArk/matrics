# -*- coding: utf-8 -*-
import dash_html_components as html


def header_metric(p_text: str):
    return html.P(p_text, style={"padding-top": "20px", "margin-bottom": "5px"})
