import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import TrustedItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class TrustedSpider(scrapy.Spider):
	name = 'trusted'
	start_urls = ['https://trustednovusbank.gi/news']

	def parse(self, response):
		articles = response.xpath('//tr[contains(@class,"cat-list-row")]')
		for article in articles:
			date = article.xpath('.//td[@headers="categorylist_header_date"]/text()').get()
			post_links = article.xpath('.//td/a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):

		title = response.xpath('//h1//text()[last()] | //h2//text()').get()
		content = response.xpath('//div[@class="uk-panel uk-margin"]//text() | //div[@class="uk-margin-medium-top"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=TrustedItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
