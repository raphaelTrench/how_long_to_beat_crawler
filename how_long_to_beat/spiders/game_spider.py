import scrapy
from scrapy.spiders import Spider
from ..items import GameItem
from os import path
import requests as re
# scrapy crawl game_spider -t csv -o -> games.csv
class GameSpider(Spider): #since the search page is generated dynamically, CrawlSpider wont work
    name = 'game_spider'
    start_urls = ['https://howlongtobeat.com/']

    def parse(self, response):
        game_url = 'https://howlongtobeat.com/game?id={}'
        for game_id in range(1,20000):
            url = game_url.format(game_id)
            yield scrapy.Request(
                url=url,
                callback=self.parse_game,
                meta={'id':game_id},
            )

    def remove_empty_end_space(self, string):
        return string.replace('\n','').rstrip() if string else string

    def extract_info(self, profile_info, field, complete=False):
        info = None
        for section in profile_info:                
            if(field in section.lower()):
                if(complete):
                    temp = section[-2].split('strong')
                    country = temp[1][1:3]
                    launch = temp[2].replace('> ','').replace('</div>','')
                    info = f"{country}:{launch}"
                else:                
                    info = section.split('</strong>')[-1].replace('</div>','')
                info = self.remove_empty_end_space(info)
        return info

    def parse_info_section(self,response):
        profile_info = response.css("p+ div div").extract()

        fields = ['developer', 'publisher', 'playable', 'genre', 'type',
            'updated']
        info = {f: self.extract_info(profile_info, f) for f in fields}

        dates = []
        for country in ['JP','NA','EU']:
            date = self.extract_info(profile_info, country, True)
            if date:
                dates.append(date)

        info['launch_dates'] = ",".join(dates)
        
        return info

    def extract_number(self,profile_detail,field):
        number = ''
        for info in profile_detail:
            if(field in info.lower()):
                number = info.split(' ')[0]
                break

        if(not number):
            return 0

        if('%' in number):
            number = int(number.replace('%',''))
        else:
            number = self.convert_numbers(number)
        return number
    
    def parse_profile_detail_numbers(self,response):
        profile_detail = response.css(".profile_details li::text").extract()
        fields = ['playing', 'beat', 'retired', 'rating', 'replay', 'backlog']
        return {f: self.extract_number(profile_detail, f) for f in fields}

    def convert_numbers(self,number):
        if('K' in number):
                numbers = number.split('K')[0].split('.')
                if(len(numbers) > 1):
                    number1, number2 = numbers
                    number = (int(number1) + (int(number2) * 0.1))
                else:
                    number = int(numbers[0])                    
                number = number * 1000 
        else:
            number = number.split(' ')[0]

        return int(number)

    def parse_platform_submissions(self,response):
        platform_submissions = []

        tables = response.css(".game_main_table")
        platform_table = None
        for table in tables:
            if('Platform' in table.extract()):
                enough_data = not "Not enough data" in table.css('tr').extract()[1]
                if(enough_data):
                    platform_table = table.css('tr')[1:]
                else:
                    return platform_submissions
        
        if(platform_table):
            for row in platform_table:
                extracted_row = row.css('td::text').extract()
                platform  = self.remove_empty_end_space(extracted_row[0])
                number = extracted_row[1]
                number = self.convert_numbers(number)
                submission = f"{platform}:{number}" 

                platform_submissions.append(submission)
            platform_submissions = ",".join(platform_submissions)

        return platform_submissions

    def get_time_table_by_kind(self,response,key):
        tables = response.css('.back_primary')       
        for table in tables:
            extracted_table = table.css('tr')
            if(len(extracted_table)):
                if(key in extracted_table[0].extract()):
                    return extracted_table[1:]
        return None

    def parse_playing_time(self,response):
        results_dict = {}
        tables_to_compute = []
        results_dict['playing'] = {}
        results_dict['speedrun'] = {}

        single_player_table = self.get_time_table_by_kind(response, 'Single-Player')
        results_dict['playing']['categories'] = ['main story', 'extras', 'completionist', 'all']
        results_dict['playing']['dict'] = {category : {} for category in results_dict['playing']['categories']}
        if(single_player_table):
            tables_to_compute.append('playing')
            results_dict['playing']['time_table'] = single_player_table
            results_dict['playing']['columns']= ['polled' , 'average', 'median', 'rushed', 'leisure']

        speedrun_table = self.get_time_table_by_kind(response, 'Speedrun')
        results_dict['speedrun']['categories'] = ['any', '100%']
        results_dict['speedrun']['dict'] = {category : {} for category in results_dict['speedrun']['categories']}
        if(speedrun_table):
            tables_to_compute.append('speedrun')
            results_dict['speedrun']['columns'] = ['polled', 'average', 'median', 'fastest', 'slowest']
            results_dict['speedrun']['time_table'] = speedrun_table        
                

        for _type in tables_to_compute:
            for idx, row in enumerate(results_dict[_type]['time_table']):
                category = results_dict[_type]['categories'][idx]                
                results_dict[_type]['dict'][category] = {}
                extracted_row = row.css('td ::text').extract()[1:]
                for column_idx, column in enumerate(extracted_row):
                    if(column_idx == 0):
                        value = self.convert_numbers(column)
                    else:
                        value = self.remove_empty_end_space(column)
                    results_dict[_type]['dict'][category][results_dict[_type]['columns'][column_idx]] = value

        return results_dict['playing']['dict'], results_dict['speedrun']['dict']

    def validate_url(self,response):
        valid = True
        html = response.css('.back_white').extract_first()
        if(html):
            valid = not 'The page you are looking for does not exist.' in html
        return valid

    def parse_game(self, response):
        # make dict gets able to return none
        is_game_page = self.validate_url(response)
        if(is_game_page ):
            game = GameItem()

            game['website_id'] = response.meta.get('id')

            game['description'] = self.remove_empty_end_space(
                response.css("p::text").extract_first())

            game['name'] = self.remove_empty_end_space(
                response.css(".shadow_text::text").extract_first())

            info_section = self.parse_info_section(response)
            game['developer'] = info_section['developer']
            game['publisher'] = info_section['publisher']
            game['platforms'] = info_section['playable']
            game['genres']    = info_section['genre']
            game['launch_dates'] = info_section['launch_dates']
            game['game_type'] = info_section['type'] or "game"
            game['last_updated'] = info_section['updated']
            
            info_detail = self.parse_profile_detail_numbers(response)
            game['playing'] = info_detail['playing']
            game['rating'] = info_detail['rating']
            game['retired'] = info_detail['retired']
            game['beat'] = info_detail['beat']
            game['replays'] = info_detail['replay']

            game['submissions_per_platform'] = self.parse_platform_submissions(response)

            playing_time_dict, speedrun_dict = self.parse_playing_time(response)

            game['main_story_duration_average'] =     playing_time_dict['main story'].get('average')
            game['main_story_duration_median'] =      playing_time_dict['main story'].get('median')
            game['main_story_duration_rushed'] =      playing_time_dict['main story'].get('rushed')
            game['main_story_duration_leisure'] =     playing_time_dict['main story'].get('leisure')
            game['main_story_duration_submissions'] = playing_time_dict['main story'].get('polled')

            game['main_story_plus_extras_duration_average'] = playing_time_dict['extras'].get('average')
            game['main_story_plus_extras_duration_median'] = playing_time_dict['extras'].get('median')
            game['main_story_plus_extras_duration_rushed'] = playing_time_dict['extras'].get('rushed')
            game['main_story_plus_extras_duration_leisure'] = playing_time_dict['extras'].get('leisure')
            game['main_story_plus_extras_duration_submissions'] = playing_time_dict['extras'].get('polled')

            game['completionist_duration_average'] = playing_time_dict['completionist'].get('average')
            game['completionist_duration_median'] = playing_time_dict['completionist'].get('median')
            game['completionist_duration_rushed'] = playing_time_dict['completionist'].get('rushed')
            game['completionist_duration_leisure'] = playing_time_dict['completionist'].get('leisure')
            game['completionist_duration_submissions'] = playing_time_dict['completionist'].get('polled')

            game['all_styles_duration_average'] = playing_time_dict['all'].get('average')
            game['all_styles_duration_median'] = playing_time_dict['all'].get('median')
            game['all_styles_duration_rushed'] = playing_time_dict['all'].get('rushed')
            game['all_styles_duration_leisure'] = playing_time_dict['all'].get('leisure')
            game['all_styles_duration_submissions'] = playing_time_dict['all'].get('polled')

            game['any_percent_spdeedrun_duration_median'] = speedrun_dict['any'].get('average')
            game['any_percent_spdeedrun_duration_average'] = speedrun_dict['any'].get('median')
            game['any_percent_spdeedrun_duration_fastest'] = speedrun_dict['any'].get('fastest')
            game['any_percent_spdeedrun_duration_slowest'] = speedrun_dict['any'].get('slowest')
            game['any_percent_spdeedrun_duration_polled'] = speedrun_dict['any'].get('polled')

            game['one_hundred_percent_spdeedrun_duration_average'] = speedrun_dict['100%'].get('average')
            game['one_hundred_percent_spdeedrun_duration_median'] = speedrun_dict['100%'].get('median')
            game['one_hundred_percent_spdeedrun_duration_fastest'] = speedrun_dict['100%'].get('fastest')
            game['one_hundred_percent_spdeedrun_duration_slowest'] = speedrun_dict['100%'].get('slowest')
            game['one_hundred_percent_spdeedrun_duration_polled'] = speedrun_dict['100%'].get('polled')

            yield game

            
