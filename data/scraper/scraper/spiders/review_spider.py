import scrapy


class ReviewSpider(scrapy.Spider):
    name = 'review'

    start_urls = ['https://steepster.com/teas']

    def parse(self, response):
        # follow links to tea pages
        for href in response.css('a.tea-name::attr(href)'):
            yield response.follow(href, self.parse_tea)

        # follow pagination links
        pagination_links = response.css('nav.pagination ul li a::attr(href)').extract()
        if pagination_links:
            yield response.follow(pagination_links[-1], self.parse)

    def parse_tea(self, response):
        
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        reviews = response.css('div.review')
        for review in reviews:

            author = review.css('span[itemprop=author] meta[itemprop=name]::attr(content)').extract_first()
            ratingValue = review.css('div[itemprop=reviewRating] span[itemprop=ratingValue]::text').extract_first()
            description = review.css('span[itemprop=description]').extract_first()
            likes = review.css('a.likes-count::text').extract_first()

            yield {
                'id': response.url.split('/')[5].split("-")[0],
                'review_id': review.css('div.review::attr(id)').extract_first().strip().replace("review_", ""),
                'note_id': review.css('div.note::attr(id)').extract_first().strip().replace("note_", ""),
                'author': author.strip() if author else "Not available",
                'author_url': review.css('span[itemprop=author] a[itemprop=url]::attr(href)').extract_first().strip()[1:] if author else "Not available",
                'ratingValue': ratingValue.strip() if ratingValue else "Not available",
                'description': description.strip().replace("\n", " ") if description else "Not available",
                'likes': likes.strip().replace(" likes", "") if likes else "Not available",
            }

        # follow link to tasting notes
        pagination_links = response.css('nav.pagination ul li a::attr(href)').extract()
        if pagination_links:
            yield response.follow(pagination_links[-1], self.parse_tea)



        

