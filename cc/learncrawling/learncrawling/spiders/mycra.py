import scrapy

class ShanghaiWeatherSpider(scrapy.Spider):
    name = "shanghai_weather"
    allowed_domains = ["weather.com.cn"]  # 替换为实际网站域名
    start_urls = [
        'http://www.weather.com.cn/weather1d/101020200.shtml',  # 替换为实际URL
    ]

    def parse(self, response):
        # 提取天气信息，这里假设页面结构如下
        # <div class="today-weather">
        #     <p class="temperature">25°C</p>
        #     <p class="condition">Sunny</p>
        # </div>
        
        weather_info = {}
        #sk mySkyNull tem
        temperature = response.css('div.tem span::text').get()
        # condition = response.css('div.today-weather p.condition::text').get()
        print("查询到的参数数据为：",temperature)
        weather_info['temperature'] = temperature
        # weather_info['condition'] = condition
        
        yield weather_info
