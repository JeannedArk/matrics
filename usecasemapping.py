# -*- coding: utf-8 -*-


#  White lists of valid use cases
import appdomainmapping
from datatypes.orderedset import OrderedSet

FILTERED_USE_CASES = [
    "Birth_date",
    "Email",
    "Name",
]

SOCIAL_USE_CASES = [
    "Add_address",
    "Add_email_account",
    # "Birth_date", # Disable, because it is not a real use case
    "Browse_content",
    "Browse_news",
    "Publish_post_message",
    "Configure_account",
    "Create_comment",
    "Edit_post",
    # "Email", # Disable, because it is not a real use case
    "Follow_profile",
    "Login_with_email",
    "Login_with_google",
    "Login_with_username",
    # "Name", # Disable, because it is not a real use case
    "Restore_account",
    "Personal_data",
    "Play_video",
    "Publish_post_message",
    "Publish_post_text",
    "Search_for_bill_gates",
    "Search_for_posts",
    "Select_interests",
    "Send_friend_request",
    "Send_message",
    "Send_message_with_photo",
    "Setup_profile",
    "Show_comments",
    "Show_friends",
    "Show_messages",
    "Show_profile",
    "Show_settings"
]

RECIPE_USE_CASES = [
    "Add_email_account",
    "Add_recipe",
    "Add_to_shopping_list",
    # "Birth_date", # Disable, because it is not a real use case
    "Browse_content",
    "Browse_news",
    "Configure_account",
    "Create_comment",
    "Create_recipe_core",
    "Create_recipe_extended",
    # "Email", # Disable, because it is not a real use case
    "Find_recipe",
    "Login_with_email",
    "Login_with_google",
    "Login_with_username",
    # "Name", # Disable, because it is not a real use case
    "Search_for_avocado",
    "Search_recipe",
    "Setup_profile",
    "Show_cocktail_recipe_1",
    "Show_cocktail_recipe_2",
    "Show_comments",
    "Show_profile",
    "Show_recipe",
    "Show_recipe_avocado_extended",
    "Show_recipe_avocado_core",
    "Show_recipe_dinner",
    "Show_reviews",
    "Show_settings",
    "Show_shopping_list",
    "Tutorial",
]

DATING_USE_CASES = [
    "Add_address",
    "Add_email_account",
    "Add_photo",
    "Add_profile_photo",
    # "Birth_date",
    "Browse_content",
    "Browse_news",
    "Configure_account",
    # "Email",
    "Login_with_email",
    "Login_with_google",
    "Login_with_username",
    "Meet_profile",
    # "Name",
    "Personal_data",
    "Personality_test",
    "Play_match_game",
    "Play_match_game_core",
    "Premium_membership",
    "Search_for_profile",
    "Send_message",
    "Setup_profile",
    "Setup_profile_body_type",
    "Setup_profile_gender",
    "Show_contacts",
    "Show_gallery",
    "Show_matches",
    "Show_messages",
    "Show_profile",
    "Show_visitors",
    "Video_chat",
]

TRAVEL_USE_CASES = [
    "Add_address",
    "Add_email_account",
    "Add_payment_option",
    # "Birth_date", # Disable, because it is not a real use case
    "Bonus_program",
    "Book_flight_core",
    "Book_flight_extended",
    "Book_hotel_core",
    "Book_hotel_extended",
    "Browse_content",
    "Browse_news",
    "Check_in",
    "Check_out",
    "Configure_account",
    "Create_review",
    "Credit_card_details",
    # "Email", # Disable, because it is not a real use case
    "Interact_with_map",
    "Login_as_guest",
    "Login_with_email",
    "Login_with_google",
    "Login_with_username",
    # "Name", # Disable, because it is not a real use case
    "Online_checkin",
    "Personal_data",
    "Search_flight_core",
    "Search_flight_extended",
    "Search_hotel",
    "Search_restaurant",
    "Security_questions",
    "Select_currency",
    "Select_dates",
    "Setup_profile",
    "Show_bookings",
    "Show_flight_status",
    "Show_gift_card",
    "Show_restaurant",
    "Show_reviews",
    "Show_settings",
]

FLASHLIGHT_USE_CASES = [
    # "Login",
    # "Flashlight"
]

ALL_USE_CASES = OrderedSet(
    SOCIAL_USE_CASES + RECIPE_USE_CASES + DATING_USE_CASES + TRAVEL_USE_CASES + FLASHLIGHT_USE_CASES
)

# Used when the use case filtering is enabled
APP_USE_CASE_MAP = {
    "com.twitter.android.lite": SOCIAL_USE_CASES,
    "com.pinterest": SOCIAL_USE_CASES,
    "com.reddit.frontpage": SOCIAL_USE_CASES,
    "com.tumblr": SOCIAL_USE_CASES,
    "me.tutti.tutti": SOCIAL_USE_CASES,
    "com.deezus.chanoran": SOCIAL_USE_CASES,
    "com.ninegag.android.app": SOCIAL_USE_CASES,

    "com.lovelyAI.CocktailsBarLiquorRecipes": RECIPE_USE_CASES,
    "tixonic.recipe.cocktailreceipeeng": RECIPE_USE_CASES,
    "tixonic.recipe.cookbookeng": RECIPE_USE_CASES,
    "com.hurrythefoodup.app": RECIPE_USE_CASES,
    "com.ajnsnewmedia.kitchenstories": RECIPE_USE_CASES,
    "cookbook.tasty.recipes": RECIPE_USE_CASES,
    "fr.cookbook": RECIPE_USE_CASES,
    "com.buzzfeed.tasty": RECIPE_USE_CASES,

    "com.dating.android": DATING_USE_CASES,
    "com.datemyage": DATING_USE_CASES,
    "com.thedatinglab.tdlconnect": DATING_USE_CASES,
    "com.spark.com.silversingles.app": DATING_USE_CASES,
    "de.mobiletrend.lovidoo": DATING_USE_CASES,
    "cdff.mobileapp": DATING_USE_CASES,

    "com.hostelworld.app": TRAVEL_USE_CASES,
    "com.wego.android": TRAVEL_USE_CASES,
    "com.kuwaitairways.mapps": TRAVEL_USE_CASES,
    "com.tripadvisor.tripadvisor": TRAVEL_USE_CASES,
    "com.trivago": TRAVEL_USE_CASES,

    "com.flashlightsuper.tung.flashlight": FLASHLIGHT_USE_CASES,
    "com.socialnmobile.hd.flashlight": FLASHLIGHT_USE_CASES,
    "com.super.led.flashlight.morse": FLASHLIGHT_USE_CASES,
    "com.happyhollow.flash.torchlight": FLASHLIGHT_USE_CASES,
    "ru.ishalyapin.flashlight": FLASHLIGHT_USE_CASES,
    "com.sfrees.flashlight": FLASHLIGHT_USE_CASES,
    "net.com.flash2018": FLASHLIGHT_USE_CASES,
}

USE_CASE_DOMAIN_MAP = {
    appdomainmapping.Domain.SOCIAL: SOCIAL_USE_CASES,
    appdomainmapping.Domain.RECIPE: RECIPE_USE_CASES,
    appdomainmapping.Domain.DATING: DATING_USE_CASES,
    appdomainmapping.Domain.TRAVEL: TRAVEL_USE_CASES,
}
