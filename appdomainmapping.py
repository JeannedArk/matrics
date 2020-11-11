# -*- coding: utf-8 -*-
from enum import Enum
from functools import total_ordering


@total_ordering
class Domain(Enum):
    SOCIAL = "social"
    RECIPE = "recipe"
    DATING = "dating"
    TRAVEL = "travel"
    FLASHLIGHT = "flashlight"
    UNKNOWN = "unknown"

    def __lt__(self, other):
        return self.value < other.value


APP_DOMAIN_MAP = {
    "com.twitter.android.lite": Domain.SOCIAL,
    "com.pinterest": Domain.SOCIAL,
    "com.reddit.frontpage": Domain.SOCIAL,
    "com.tumblr": Domain.SOCIAL,
    "me.tutti.tutti": Domain.SOCIAL,
    "com.deezus.chanoran": Domain.SOCIAL,
    "com.ninegag.android.app": Domain.SOCIAL,

    "com.lovelyAI.CocktailsBarLiquorRecipes": Domain.RECIPE,
    "tixonic.recipe.cocktailreceipeeng": Domain.RECIPE,
    "tixonic.recipe.cookbookeng": Domain.RECIPE,
    "com.hurrythefoodup.app": Domain.RECIPE,
    "com.ajnsnewmedia.kitchenstories": Domain.RECIPE,
    "cookbook.tasty.recipes": Domain.RECIPE,
    "fr.cookbook": Domain.RECIPE,
    "com.buzzfeed.tasty": Domain.RECIPE,

    "com.dating.android": Domain.DATING,
    "com.datemyage": Domain.DATING,
    "com.thedatinglab.tdlconnect": Domain.DATING,
    "com.spark.com.silversingles.app": Domain.DATING,
    "de.mobiletrend.lovidoo": Domain.DATING,
    "cdff.mobileapp": Domain.DATING,

    "com.hostelworld.app": Domain.TRAVEL,
    "com.wego.android": Domain.TRAVEL,
    "com.kuwaitairways.mapps": Domain.TRAVEL,
    "com.tripadvisor.tripadvisor": Domain.TRAVEL,
    "com.trivago": Domain.TRAVEL,

    "com.flashlightsuper.tung.flashlight": Domain.FLASHLIGHT,
    "com.socialnmobile.hd.flashlight": Domain.FLASHLIGHT,
    "com.super.led.flashlight.morse": Domain.FLASHLIGHT,
    "com.happyhollow.flash.torchlight": Domain.FLASHLIGHT,
    "ru.ishalyapin.flashlight": Domain.FLASHLIGHT,
    "com.sfrees.flashlight": Domain.FLASHLIGHT,
    "net.com.flash2018": Domain.FLASHLIGHT,
}


def get_domain(package_name: str):
    return Domain.UNKNOWN if package_name not in APP_DOMAIN_MAP else APP_DOMAIN_MAP[package_name]
