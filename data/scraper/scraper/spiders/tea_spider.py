import scrapy


class TeaSpider(scrapy.Spider):
    name = 'tea'

    start_urls = ['https://steepster.com/teas']

    def parse(self, response):
        # follow links to tea pages
        for href in response.css('a.tea-name::attr(href)'):
            yield response.follow(href, self.parse_tea)

        # follow pagination links
        pagination_links = response.css('nav.pagination ul li a::attr(href)').extract()
        yield response.follow(pagination_links[-1], self.parse)

    def parse_tea(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        tea_description = response.css('dl.tea-description dd::text')
        tea_array = []
        for row in tea_description:
            tea_array.append(row.extract().strip())

        yield {
            'id': response.url.split('/')[5].split("-")[0],
            'name': extract_with_css('h1[itemprop=name]::text'),
            'brand': extract_with_css('span[itemprop=brand] span[itemprop=name]::text'),
            'reviewCount': extract_with_css('meta[itemprop=reviewCount]::attr(content)'),
            'ratingValue': extract_with_css('div[itemprop=ratingValue]::text'),
            'teaType': extract_with_css('dl.tea-description dd a::text'),
            'ingredients': tea_array[0],
            'flavors': tea_array[1],
            'soldIn': tea_array[2],
            'caffeine': tea_array[3],
            'certification': tea_array[4],
            'wantIt': extract_with_css('section[id=want-user-images] h3::text').replace(" Want it", ""),
            'ownIt': extract_with_css('section[id=have-user-images] h3::text').replace(" Own it", ""),
            'imageUrl': extract_with_css('div.tea-image img[itemprop=image]::attr(src)'),
            'url': response.url
        }