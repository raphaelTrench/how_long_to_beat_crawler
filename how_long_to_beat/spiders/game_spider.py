import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import GameItem
from os import path
# scrapy crawl netshoes -t csv -o -> netshoes.csv
class GameSpider(CrawlSpider):
    name = 'game_spider'
    allowed_domains = ['https://howlongtobeat.com']
    start_urls = ['https://howlongtobeat.com/#search1']
    base_url = 'https://howlongtobeat.com/'
    rules = [Rule(
        LinkExtractor(allow=['https:\/\/howlongtobeat.com\/game\?id=(\d)+',
                            '*#search*']),
                      callback='parse_game', follow=True)]

    def remove_empty_end_space(self, string):
        string = string.replace('\n','')
        return string if string[-1] != " " else string[:-1]

    def parse_info_section(self,response,child_number):
        extracted = response.css(f".profile_info:nth-child({child_number})").extract_first()
        cleaned = extracted.split('</strong>')[-1].replace('</div>','').replace('\n','')
        return cleaned if cleaned[-1] != " " else cleaned[:-1]

    def parse_playing_number(self,response):
        playing = response.css(
            ".profile_details li:nth-child(1)::text").extract_first()
        if('K' in playing):
            playing_number = int(playing.split('K')[0].split('.')[0]) * 1000 
        else:
            playing_number = int(playing.split(' ')[0])
        return playing_number

    def parse_game(self, response):
        is_game_page = response.css("#profile_summary_rest").extract_first()
        if(is_game_page):
            game = GameItem()

            game.description = self.remove_empty_end_space(
                response.css("p::text").extract_first())

            game.playing = self.parse_playing_number(response)

            name = self.remove_empty_end_space(
                response.css(".shadow_text::text").extract_first())

            info_section = response.css("p+ div div").extract()
            # get ids from list above to pass onto functions below
            developer = self.parse_info_section(response,1)
            publisher = self.parse_info_section(response,2)
            platforms = self.parse_info_section(response,3)
            genres    = self.parse_info_section(response,4)
            launch_dates = self.parse_launch_dates(response) 
            
            rating
            retirement
            submissions_per_platform
            beat
            game_type
            main_story_duration_average
            main_story_duration_median
            main_story_duration_rushed
            main_story_duration_leisure
            main_story_duration_submissions
            main_story_plus_extras_duration_average
            main_story_plus_extras_duration_median
            main_story_plus_extras_duration_rushed
            main_story_plus_extras_duration_leisure
            main_story_plus_extras_duration_submissions
            completionist_duration_average
            completionist_duration_median
            completionist_duration_rushed
            completionist_duration_leisure
            completionist_duration_submissions
            all_styles_duration_average
            all_styles_duration_median
            all_styles_duration_rushed
            all_styles_duration_leisure
            all_styles_duration_submissions
            any_percent_spdeedrun_duration_average
            any_percent_spdeedrun_duration_median
            any_percent_spdeedrun_duration_fastest
            any_percent_spdeedrun_duration_slowest
            any_percent_spdeedrun_duration_polled
            one_hundred_percent_spdeedrun_duration_average
            one_hundred_percent_spdeedrun_duration_median
            one_hundred_percent_spdeedrun_duration_fastest
            one_hundred_percent_spdeedrun_duration_slowest
            one_hundred_percent_spdeedrun_duration_polled

            
