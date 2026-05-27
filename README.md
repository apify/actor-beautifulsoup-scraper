# Beautifulsoup Scraper

Beautifulsoup Scraper crawls websites using plain HTTP requests (no browser) and lets you extract data from each page with your own Python code, powered by the [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) library. It's the Python alternative to [Cheerio Scraper](https://apify.com/apify/cheerio-scraper) and is ideal for sites that don't rely on client-side JavaScript.

## How it works

You give the scraper two things: where to start and how to extract data.

1. It adds your [**Start URLs**](https://apify.com/apify/beautifulsoup-scraper/input-schema) to the crawling queue.
2. It fetches each URL and builds a `BeautifulSoup` DOM from the HTML.
3. It runs your **Page function** on the page and stores the returned data.
4. Optionally, it follows links matching your **Link selector** / **Link patterns** and enqueues them for recursive crawling.

## Page function

Python code run for every page. It receives a [`BeautifulSoupCrawlingContext`](https://crawlee.dev/python/api/class/BeautifulSoupCrawlingContext) and returns the data to store:

```python
from typing import Any
from crawlee.crawlers import BeautifulSoupCrawlingContext

def page_function(context: BeautifulSoupCrawlingContext) -> Any:
    return {
        'url': context.request.url,
        'title': context.soup.title.string if context.soup.title else None,
    }
```

The code runs on Python 3.14 and may only import modules already installed in the Actor.

## Proxy configuration

A proxy is **required**. Set `proxyConfiguration` to use [Apify Proxy](https://apify.com/proxy) (automatic or selected groups) or your own custom proxy URLs:

```jsonc
{
  "useApifyProxy": true,           // use Apify Proxy
  "apifyProxyGroups": [],          // optional: specific groups
  "proxyUrls": []                  // or custom "scheme://user:pass@host:port" URLs
}
```

## Output

Results returned by your page function land in the run's default dataset. Download them as JSON, CSV, XML, or Excel from Apify Console, or via the API:

```
https://api.apify.com/v2/datasets/[DATASET_ID]/items?format=json&clean=true
```

## Limitations

The Actor uses raw HTTP requests, so it can't render JavaScript. For dynamic sites use [Web Scraper](https://apify.com/apify/web-scraper) instead. To add Python modules not bundled here, open an issue or PR at [github.com/apify/actor-beautifulsoup-scraper](https://github.com/apify/actor-beautifulsoup-scraper).
