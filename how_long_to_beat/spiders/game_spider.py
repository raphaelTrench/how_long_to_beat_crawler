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
                if(not "Not enough data" in table.css('tr').extract()[1]):
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

    def parse_playing_time(self, response):
        results_dict = {
            'playing': {},
            'speedrun': {},
        }
        tables_to_compute = []
        playing = results_dict['playing']
        speedrun = results_dict['speedrun']

        single_player_table = self.get_time_table_by_kind(
            response,
            'Single-Player',
        )
        playing['categories'] = ['main story', 'extras', 'completionist',
            'all']
        playing['dict'] = {cat: {} for cat in playing['categories']}
        if(single_player_table):
            tables_to_compute.append('playing')
            playing['time_table'] = single_player_table
            playing['columns'] = ['polled' , 'average', 'median', 'rushed',
                'leisure']

        speedrun_table = self.get_time_table_by_kind(response, 'Speedrun')
        speedrun['categories'] = ['any', '100%']
        speedrun['dict'] = {cat: {} for cat in speedrun['categories']}
        if(speedrun_table):
            tables_to_compute.append('speedrun')
            speedrun['columns'] = ['polled', 'average', 'median', 'fastest',
                'slowest']
            speedrun['time_table'] = speedrun_table        
                
        tables = lambda l: (results_dict[i] for i in l)
        for _type in tables(tables_to_compute):
            for idx, row in enumerate(_type['time_table']):
                category = _type['categories'][idx]   
                _type['dict'][category] = {}
                extracted_row = row.css('td ::text').extract()[1:]
                for idy, column in enumerate(extracted_row):
                    if(not idy):
                        value = self.convert_numbers(column)
                    else:
                        value = self.remove_empty_end_space(column)
                    _type['dict'][category][_type['columns'][idy]] = value

        return playing['dict'], speedrun['dict']

    def validate_url(self, response):
        html = response.css('.back_white').extract_first()
        not_exist_msg = 'The page you are looking for does not exist.'
        return (not_exist_msg not in html) if html else True

    def parse_game(self, response):
        # make dict gets able to return none
        if not self.validate_url(response):
            return

        info_detail = self.parse_profile_detail_numbers(response)
        info_section = self.parse_info_section(response)
        game = GameItem(
            website_id=response.meta.get('id'),
            developer=info_section['developer'],
            publisher=info_section['publisher'],
            platforms=info_section['playable'],
            genres=info_section['genre'],
            launch_dates=info_section['launch_dates'],
            game_type=(info_section['type'] or "game"),
            last_updated=info_section['updated'],
            playing=info_detail['playing'],
            rating=info_detail['rating'],
            retired=info_detail['retired'],
            beat=info_detail['beat'],
            replays=info_detail['replay'],
            description=self.remove_empty_end_space(
                response.css("p::text").extract_first()),
            name=self.remove_empty_end_space(
                response.css(".shadow_text::text").extract_first()),
            submissions_per_platform=self.parse_platform_submissions(
                response),
        )

        playing_time, speedrun = self.parse_playing_time(response)

        fields = {
            'main_story_duration': 'main story',
            'main_story_plus_extras_duration': 'extras',
            'completionist_duration': 'completionist',
            'all_styles_duration': 'all',
        }
        for field, key in fields.items():
            data = playing_time[key]
            game[f'{field}_average'] = data.get('average')
            game[f'{field}_median'] = data.get('median')
            game[f'{field}_rushed'] = data.get('rushed')
            game[f'{field}_leisure'] = data.get('leisure')
            game[f'{field}_submissions'] = data.get('polled')

        fields = {
            'any_percent_speedrun_duration': 'any',
            'one_hundred_percent_speedrun_duration': '100%',
        }
        for field, key in fields.items():
            data = speedrun[key]
            game[f'{field}_median'] = data.get('average')
            game[f'{field}_average'] = data.get('median')
            game[f'{field}_fastest'] = data.get('fastest')
            game[f'{field}_slowest'] = data.get('slowest')
            game[f'{field}_polled'] = data.get('polled')

        return game