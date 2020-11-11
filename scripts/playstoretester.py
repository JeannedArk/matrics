# -*- coding: utf-8 -*-
from urllib.error import HTTPError

from metrics.ucecomparison.playstoremetrics import get_play_store_rating, get_play_store_number_of_installations, \
    get_play_store_number_of_reviews


def get_stats(package_name):
    rating = get_play_store_rating(package_name)
    num_reviews = get_play_store_number_of_reviews(package_name)
    num_installations = get_play_store_number_of_installations(package_name)
    return rating, num_reviews, num_installations


if __name__ == '__main__':
    packages = [
        "tixonic.recipe.cocktailreceipeeng",
        "com.hostelworld.app",
        "com.reddit.frontpage",
        "com.ninegag.android.app",
        "com.spark.com.silversingles.app",
        "com.hurrythefoodup.app",
        "com.ajnsnewmedia.kitchenstories",
        "com.twitter.android.lite",
        "me.tutti.tutti",
        "com.buzzfeed.tasty",
        "tixonic.recipe.cookbookeng",
        "com.lovelyAI.CocktailsBarLiquorRecipes",
        "cookbook.tasty.recipes",
        "com.trivago",
        "com.kuwaitairways.mapps",
        "com.wego.android",
        "com.tumblr",
        "fr.cookbook",
        "de.mobiletrend.lovidoo",
        "com.datemyage",
        "cdff.mobileapp",
        "com.thedatinglab.tdlconnect",
        "com.tripadvisor.tripadvisor",
    ]

    for package in packages:
        try:
            rating, num_reviews, num_installations = get_stats(package)
            print(f"{package}: {rating} {num_reviews} {num_installations}")
        except HTTPError as e:
            print(f"Error for {package}: {e}")
