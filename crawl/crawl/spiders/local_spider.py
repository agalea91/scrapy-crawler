import scrapy


class QuotesSpider(scrapy.Spider):
    name = "local_8080"

    def start_requests(self):
        urls = [
            'http://localhost:8080/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        self.dump_html(response)
        yield self.dump_page_data(response)
        yield self.follow_inlinks(response)

    def dump_html(self, response):
        page = response.url.replace("/", "_").replace(":", "_")
        filename = f'local_8080_{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')


    def dump_page_data(self, response):
        title = response.request.meta['driver'].title
        return dict(title=title)

    def follow_inlinks(self, response):
        links = response.css('a::attr(href)').getall()
        # Filter on localhost and relative paths
        links = [link for link in links if any((
            link.startswith("/"),
            "localhost" in link,
        ))]
        return from response.follow_all(anchors, callback=self.parse)

