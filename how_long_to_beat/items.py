# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GameItem(scrapy.Item):
    website_id = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()

    developer = scrapy.Field()
    publisher = scrapy.Field()
    platforms = scrapy.Field()
    genres = scrapy.Field()
    launch_dates = scrapy.Field()
    game_type = scrapy.Field()
    last_updated = scrapy.Field()

    rating = scrapy.Field()
    retired = scrapy.Field()
    playing = scrapy.Field()
    beat = scrapy.Field()
    replays = scrapy.Field()
    backlogs = scrapy.Field()    

    submissions_per_platform = scrapy.Field()

    main_story_duration_average = scrapy.Field()
    main_story_duration_median = scrapy.Field()
    main_story_duration_rushed = scrapy.Field()
    main_story_duration_leisure = scrapy.Field()
    main_story_duration_submissions = scrapy.Field()

    main_story_plus_extras_duration_average = scrapy.Field()
    main_story_plus_extras_duration_median = scrapy.Field()
    main_story_plus_extras_duration_rushed = scrapy.Field()
    main_story_plus_extras_duration_leisure = scrapy.Field()
    main_story_plus_extras_duration_submissions = scrapy.Field()

    completionist_duration_average = scrapy.Field()
    completionist_duration_median = scrapy.Field()
    completionist_duration_rushed = scrapy.Field()
    completionist_duration_leisure = scrapy.Field()
    completionist_duration_submissions = scrapy.Field()

    all_styles_duration_average = scrapy.Field()
    all_styles_duration_median = scrapy.Field()
    all_styles_duration_rushed = scrapy.Field()
    all_styles_duration_leisure = scrapy.Field()
    all_styles_duration_submissions = scrapy.Field()

    any_percent_spdeedrun_duration_average = scrapy.Field()
    any_percent_spdeedrun_duration_median = scrapy.Field()
    any_percent_spdeedrun_duration_fastest = scrapy.Field()
    any_percent_spdeedrun_duration_slowest = scrapy.Field()
    any_percent_spdeedrun_duration_polled = scrapy.Field()

    one_hundred_percent_spdeedrun_duration_average = scrapy.Field()
    one_hundred_percent_spdeedrun_duration_median = scrapy.Field()
    one_hundred_percent_spdeedrun_duration_fastest = scrapy.Field()
    one_hundred_percent_spdeedrun_duration_slowest = scrapy.Field()
    one_hundred_percent_spdeedrun_duration_polled = scrapy.Field()



