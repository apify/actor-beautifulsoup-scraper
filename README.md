# Beautifulsoup Scraper

Beautifulsoup Scraper is a ready-made solution for crawling websites using plain HTTP requests. It provides HTTP responses to your defined function, where you can use [Beautifulsoup](https://pypi.org/project/beautifulsoup4/) Python library to extract any data from them. Fast.

Beautifulsoup is a Python library used for parsing HTML and XML documents. It provides an interface for navigating and manipulating the document structure. With powerful search functions, you can search for elements based on tags, attributes, or CSS classes.

Beautifulsoup Scraper is ideal for scraping web pages that do not rely on client-side JavaScript to serve their content. Beautiful Soup itself is a parser library and does not execute JavaScript.

## Usage

To get started with Beautifulsoup Scraper, you only need two things. First, tell the scraper which web pages it should load. Second, tell it how to extract data from each page.

The scraper starts by loading the pages specified in the [**Start URLs**](#start-urls) field. You can make the scraper follow page links on the fly by setting a [**Link selector**](#link-selector), and [**Link patterns**](#link-patterns) to tell the scraper which links it should add to the crawling queue. This is useful for the recursive crawling of entire websites, e.g. to find all products in an online store.

To tell the scraper how to extract data from web pages, you need to provide a [**Page function**](#page-function). This is Python code that is executed for every web page loaded. A [Beautifulsoup](https://pypi.org/project/beautifulsoup4/) library is assumed to be used for data extraction.

In summary, Beautifulsoup Scraper works as follows:

1. Adds each [Start URL](#start-urls) to the crawling queue.
2. Fetches the first URL from the queue and constructs a DOM from the fetched HTML string.
3. Executes the [**Page function**](#page-function) on the loaded page and saves its results.
4. Optionally, finds all links from the page using the [**Link selector**](#link-selector).
   If a link matches any of the [**Link selector**](#link-selector) and has not yet been visited, add it to the queue.
5. If there are more items in the queue, repeats step 2, otherwise finish.

See our video guide for more details on how to set up this Actor:
[web scraping with beautifulsoup](https://www.youtube.com/watch?v=1KqLLuIW6MA)

<!-- TODO: Add Content types section -->

## Limitations

The Actor does not employ a full-featured web browser such as Chromium or Firefox, so it will not be sufficient for web pages that render their content dynamically using client-side JavaScript. To scrape such sites, you might prefer to use [**Web Scraper**](https://apify.com/apify/web-scraper) (`apify/web-scraper`), which loads pages in a full browser and renders dynamic content.

In the [**Page function**](#page-function) you can only use Python modules that are already installed in this Actor. If you require other modules for your scraping, you'll need to develop a completely new Actor or open a new issue or pull request in the [github.com/apify/actor-beautifulsoup-scraper](https://github.com/apify/actor-beautifulsoup-scraper).

## Input configuration

As input, the Beautifulsoup Scraper Actor accepts a number of configurations. These can be entered either manually in the user interface in [Apify Console](https://console.apify.com), or programmatically in a JSON object using the [Apify API](https://apify.com/docs/api/v2#/reference/actors/run-collection/run-actor). For a complete list of input fields and their types, please visit the [Input](https://apify.com/apify/beautifulsoup-scraper/input-schema) tab.

### Page function

The **Page function** (`pageFunction`) field contains a Python script with a single function that enables the user to extract data from the web page, access its DOM, add new URLs to the request queue, and otherwise control Beautifulsoup Scraper's operation.

Example:

```python
from typing import Any

def page_function(context: Context) -> Any:
    url = context.request["url"]
    title = context.soup.title.string if context.soup.title else None
    return {"url": url, "title": title}
```

### Context

The code runs in Python 3.12 and the `page_function` accepts a single argument `context` of type [Context](https://github.com/apify/-beautifulsoup-scraper/blob/master/src/dataclasses.py). It is a dataclass with the following fields:
- `soup` of type `BeautifulSoup` with the parsed HTTP payload,
- `request` of type `dict` with the HTTP request data,
- `request_queue` of type `apify.storages.RequestQueue` ([RequestQueue](https://docs.apify.com/sdk/python/reference/class/RequestQueue)) for the interaction with the HTTP request queue,
- `response` of type `httpx.Response` with the HTTP response data.

## Proxy configuration

The **Proxy configuration** (`proxyConfiguration`) option enables you to set proxies that will be used by the scraper in order to prevent its detection by target web pages. You can use both the [Apify Proxy](https://apify.com/proxy) and custom HTTP or SOCKS5 proxy servers.

Proxy is required to run the scraper. The following table lists the available options for the proxy configuration setting:

<table class="table table-bordered table-condensed">
    <tbody>
    <tr>
        <th><b>Apify&nbsp;Proxy&nbsp;(automatic)</b></td>
        <td>
            The scraper will load all web pages using the <a href="https://apify.com/proxy">Apify Proxy</a> in automatic mode. In this mode, the proxy uses all proxy groups that are available to the user. For each new web page, it automatically selects the proxy that hasn't been used in the longest time for the specific hostname in order to reduce the chance of detection by the web page. You can view the list of available proxy groups on the <a href="https://console.apify.com/proxy" target="_blank" rel="noopener">Proxy</a> page in Apify Console.
        </td>
    </tr>
    <tr>
        <th><b>Apify&nbsp;Proxy&nbsp;(selected&nbsp;groups)</b></td>
        <td>
            The scraper will load all web pages using the <a href="https://apify.com/proxy">Apify Proxy</a> with specific groups of target proxy servers.
        </td>
    </tr>
    <tr>
        <th><b>Custom&nbsp;proxies</b></td>
        <td>
            <p>
                The scraper will use a custom list of proxy servers. The proxies must be specified in the <code>scheme://user:password@host:port</code> format. Multiple proxies should be separated by a space or new line. The URL scheme can be either <code>http</code> or <code>socks5</code>. The user and password might be omitted, but the port must always be present.
            </p>
            <p>
                Example:
            </p>
            <pre><code class="language-none">http://bob:password@proxy1.example.com:8000<br>http://bob:password@proxy2.example.com:8000</code></pre>
        </td>
    </tr>
    </tbody>
</table>

The proxy configuration can be set programmatically when calling the Actor using the API by setting the `proxyConfiguration` field. It accepts a JSON object with the following structure:

```javascript
{
    // Indicates whether to use the Apify Proxy or not.
    "useApifyProxy": Boolean,

    // Array of Apify Proxy groups, only used if "useApifyProxy" is true.
    // If missing or null, the Apify Proxy will use automatic mode.
    "apifyProxyGroups": String[],

    // Array of custom proxy URLs, in "scheme://user:password@host:port" format.
    // If missing or null, custom proxies are not used.
    "proxyUrls": String[],
}
```

## Results

The scraping results returned by [**Page function**](#page-function) are stored in the default dataset associated with the Actor run, from where you can export them to formats such as JSON, XML, CSV, or Excel.

To download the results, call the [Get dataset items](https://docs.apify.com/api/v2#/reference/datasets/item-collection) API endpoint:

```
https://api.apify.com/v2/datasets/[DATASET_ID]/items?format=json
```

where `[DATASET_ID]` is the ID of the Actor's run dataset, in which you can find the Run object returned when starting the Actor. Alternatively, you'll find the download links for the results in Apify Console.

To skip the `#error` and `#debug` metadata fields from the results and not include empty result records, simply add the `clean=true` query parameter to the API URL, or select the **Clean items** option when downloading the dataset in Apify Console.

To get the results in other formats, set the `format` query parameter to `xml`, `xlsx`, `csv`, `html`, etc. For more information, see [Datasets](https://docs.apify.com/storage#dataset) in documentation or the [Get dataset items](https://docs.apify.com/api/v2#/reference/datasets/item-collection) endpoint in Apify API reference.
