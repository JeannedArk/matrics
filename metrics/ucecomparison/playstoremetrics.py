# -*- coding: utf-8 -*-
from functools import lru_cache
from typing import Callable, List

from aggregationlevel import AggregationLevel
from metrics.metric import *

from bs4 import BeautifulSoup
import urllib.request
import ssl

from metrics.ucecomparison.multinumberucecomparison import MultiNumberUCEComparison
from model.baseexplorationmodel import BaseExplorationModel

# https://www.apptrace.com/
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
context = ssl._create_unverified_context()
ssl._create_default_https_context = ssl._create_unverified_context
headers = {'User-Agent': user_agent}
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', user_agent)]
urllib.request.install_opener(opener)
GOOGLE_PLAY_STORE_BASE_URL = "https://play.google.com/store/apps/details?id="

# Some apps are not available anymore in the app store
# I saved the stats and hardcoded it here.


@lru_cache(maxsize=64)
def get_html_from_url(url):
    request = urllib.request.Request(url, None, headers)
    try:
        fp = urllib.request.urlopen(request, context=context)
        mybytes = fp.read()
        page = mybytes.decode("utf8")
        fp.close()
        return page
    except urllib.error.HTTPError as e:
        raise AssertionError(f"HTTP error with url={url} : {e}")


rating_map = {
    "com.reddit.frontpage": 4.5,
    "me.tutti.tutti": 4.0,
    "com.tumblr": 4.3,
    "com.twitter.android.lite": 3.9,
    "com.ninegag.android.app": 4.6,

    "com.lovelyAI.CocktailsBarLiquorRecipes": 3.2,
    "tixonic.recipe.cocktailreceipeeng": 3.8,
    "tixonic.recipe.cookbookeng": 2.4,
    "com.hurrythefoodup.app": 4.6,
    "com.ajnsnewmedia.kitchenstories": 4.7,
    "cookbook.tasty.recipes": 4.6,
    "fr.cookbook": 4.7,
    "com.buzzfeed.tasty": 4.7,

    "com.datemyage": 3.6,
    "com.thedatinglab.tdlconnect": 3.1,
    "com.spark.com.silversingles.app": 3.5,
    "de.mobiletrend.lovidoo": 4.4,
    "cdff.mobileapp": 4.1,

    "com.trivago": 4.5,
    "com.tripadvisor.tripadvisor": 4.4,
    "com.kuwaitairways.mapps": 4.3,
    "com.wego.android": 4.5,
    "com.hostelworld.app": 4.6,
}

reviews_map = {
    "com.reddit.frontpage": 1604709,
    "me.tutti.tutti": 30,
    "com.tumblr": 3461841,
    "com.twitter.android.lite": 99068,
    "com.ninegag.android.app": 1647038,

    "com.lovelyAI.CocktailsBarLiquorRecipes": 9,
    "tixonic.recipe.cocktailreceipeeng": 8,
    "tixonic.recipe.cookbookeng": 8,
    "com.hurrythefoodup.app": 666,
    "com.ajnsnewmedia.kitchenstories": 29220,
    "cookbook.tasty.recipes": 778,
    "fr.cookbook": 32536,
    "com.buzzfeed.tasty": 113544,

    "com.datemyage": 6865,
    "com.thedatinglab.tdlconnect": 199,
    "com.spark.com.silversingles.app": 789,
    "de.mobiletrend.lovidoo": 36662,
    "cdff.mobileapp": 20005,

    "com.trivago": 287401,
    "com.tripadvisor.tripadvisor": 1355218,
    "com.kuwaitairways.mapps": 2014,
    "com.wego.android": 124783,
    "com.hostelworld.app": 26469,
}

installations_map = {
    "com.reddit.frontpage": 10000000,
    "com.ninegag.android.app": 10000000,
    "com.twitter.android.lite": 10000000,
    "me.tutti.tutti": 1000,
    "com.tumblr": 100000000,

    "com.lovelyAI.CocktailsBarLiquorRecipes": 5000,
    "tixonic.recipe.cocktailreceipeeng": 1000,
    "tixonic.recipe.cookbookeng": 1000,
    "com.hurrythefoodup.app": 100000,
    "com.ajnsnewmedia.kitchenstories": 1000000,
    "cookbook.tasty.recipes": 10000,
    "fr.cookbook": 1000000,
    "com.buzzfeed.tasty": 5000000,

    "com.datemyage": 1000000,
    "com.thedatinglab.tdlconnect": 10000,
    "com.spark.com.silversingles.app": 100000,
    "de.mobiletrend.lovidoo": 500000,
    "cdff.mobileapp": 1000000,

    "com.trivago": 50000000,
    "com.tripadvisor.tripadvisor": 100000000,
    "com.kuwaitairways.mapps": 100000,
    "com.wego.android": 10000000,
    "com.hostelworld.app": 1000000,
}


def get_play_store_rating(package_id: str):
    if package_id in rating_map:
        return float(rating_map[package_id])
    url = f"{GOOGLE_PLAY_STORE_BASE_URL}{package_id}"
    page = get_html_from_url(url)
    soup = BeautifulSoup(page, "lxml")
    html_elements = soup.body.find_all(attrs={"class": "pf5lIe"})
    # For example, 'Rated 4.4 stars out of five stars'
    rating_str: str = html_elements[0].contents[0].attrs["aria-label"]
    rating = float(rating_str.replace("Rated ", "").replace(" stars out of five stars", ""))

    # print(f'"{package_id}": {rating},')

    return rating


def get_play_store_number_of_reviews(package_id: str):
    if package_id in reviews_map:
        return int(reviews_map[package_id])
    url = f"{GOOGLE_PLAY_STORE_BASE_URL}{package_id}"
    page = get_html_from_url(url)
    soup = BeautifulSoup(page, "lxml")
    html_elements = soup.body.find_all(attrs={"class": "AYi5wd TBRnV"})
    reviews_str: str = html_elements[0].contents[0].attrs["aria-label"]
    reviews = int(reviews_str.replace(" ratings", "").replace(",", ""))

    # print(f'"{package_id}": {reviews},')

    return reviews


def get_play_store_number_of_installations(package_id: str):
    if package_id in installations_map:
        return int(installations_map[package_id])
    url = f"{GOOGLE_PLAY_STORE_BASE_URL}{package_id}"
    page = get_html_from_url(url)
    soup = BeautifulSoup(page, "lxml")
    html_elements = soup.body.find_all(attrs={"class": "IQ1z0d"})
    # For example, '10,000,000+'
    installation_str: str = html_elements[4].contents[0].contents[0]
    installation = int(installation_str.replace("+", "").replace(",", ""))

    # print(f'"{package_id}": {installation},')

    return installation


# Force to load from cache

def selector_play_store_rating(it_unit: BaseExplorationModel,
                               filtering_entries: Callable,
                               aggregation_lvl) -> List:
    return [get_play_store_rating(it_unit.package_name)]


class PlayStoreRating(MultiNumberUCEComparison):
    description = "Google Play Store rating"
    name = "Play Store Rating"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    axis_type="log",
                                    boxpoints='outliers')

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_play_store_rating,
                         aggregation_lvls=PlayStoreRating.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=PlayStoreRating.plot_config,
                         force_reload=False)


def selector_play_store_review_number(it_unit: BaseExplorationModel,
                                      filtering_entries: Callable,
                                      aggregation_lvl) -> List[int]:
    return [get_play_store_number_of_reviews(it_unit.package_name)]


class PlayStoreReviewNumber(MultiNumberUCEComparison):
    description = "Google Play Store number of reviews"
    name = "Play Store Quantity of Reviews"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    axis_type="log",
                                    boxpoints='outliers')

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_play_store_review_number,
                         aggregation_lvls=PlayStoreReviewNumber.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=PlayStoreReviewNumber.plot_config,
                         force_reload=False)


def selector_play_store_installations_number(it_unit: BaseExplorationModel,
                                             filtering_entries: Callable,
                                             aggregation_lvl) -> List[int]:
    return [get_play_store_number_of_installations(it_unit.package_name)]


class PlayStoreInstallationNumber(MultiNumberUCEComparison):
    description = "Google Play Store number of installations"
    name = "Play Store Quantity of Installations"
    aggregation_lvls = [AggregationLevel.APP]
    plot_config = PlotConfiguration(univariate_plot_style=PlotStyle.BOX,
                                    axis_type="log",
                                    boxpoints='outliers')

    def __init__(self, model, outlier_method=ZScore1StdDevOutlierDetector):
        super().__init__(model=model,
                         filtering_op=identity,
                         data_select_op=selector_play_store_installations_number,
                         aggregation_lvls=PlayStoreInstallationNumber.aggregation_lvls,
                         outlier_method=outlier_method,
                         plot_config=PlayStoreInstallationNumber.plot_config,
                         force_reload=False)
