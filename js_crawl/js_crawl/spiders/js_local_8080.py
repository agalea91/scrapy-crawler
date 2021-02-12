import json
import scrapy
from scrapy_selenium import SeleniumRequest

class Sitemap:
    def __init__(self):
        self._xml_records = []
        self._urls_added = []

    @property
    def xml(self):
        return """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{}
</urlset>
""".format("\n".join(self._xml_records))

    def get_url(self, data):
        url = data["url"]
        url = url.split("localhost:8080")[-1]
        url = f"https://ravenslightphoto.com{url}"
        return url

    def update(self, data):
        url = self.get_url(data)
        self._urls_added.append(url)
        self._xml_records.append(
f"""  <url>
    <loc>{url}</loc>
  </url>""")


    def write(self):
        with open("crawl-data/sitemap.xml", "w") as f:
            f.write(self.xml)

    def write_urls_added(self):
        with open("crawl-data/website_urls.json", "w") as f:
            f.write(json.dumps(self._urls_added))



class Spider(scrapy.Spider):
    name = "js_local_8080"

    def init_spider(self):
        self.xml_sitemap = Sitemap()

    def start_requests(self):
        self.init_spider()
        urls = [
            'http://localhost:8080/'
        ]
        for url in urls:
            yield SeleniumRequest(url=url, callback=self.parse)


    def parse(self, response):
        self.xml_sitemap.update({"url": response.url})
        self.xml_sitemap.write()
        self.xml_sitemap.write_urls_added()
        self.dump_html(response)
        yield self.dump_page_data(response)
        for link in self.get_follow_inlinks(response):
            url = response.urljoin(link)
            yield SeleniumRequest(url=url, callback=self.parse)

    def dump_html(self, response):
        page = response.url.replace("/", "_").replace(":", "")
        with open(f"crawl-data/html/{page}.html", 'wb') as f:
            f.write(response.body)


    def dump_page_data(self, response):
        title = response.request.meta['driver'].title
        return dict(url=response.url, title=title)


    def get_follow_inlinks(self, response):
        links = response.css('a::attr(href)').getall()
        # Filter on localhost and relative paths
        links = [link for link in links if any((
            link.startswith("/"),
            "localhost" in link,
        ))]
        return links






