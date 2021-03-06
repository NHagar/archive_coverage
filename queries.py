# %%
import os
import re
from datetime import datetime, timedelta

import pandas as pd

from goose3 import Goose
from lxml.etree import ParserError
from tqdm import tqdm

from provider_ingestions import query_downloads

from dotenv import load_dotenv

load_dotenv()

# %%
start_date = datetime.strptime("2020-04-01", "%Y-%m-%d")
end_date = datetime.strptime("2020-04-30", "%Y-%m-%d")
domain = "vox.com"
news_key = os.environ["API_KEY_NEWS"]
mc_key = os.environ["API_KEY_MC"]

# %%
def get_responses(domain, start_date, end_date, news_api_key, mc_key):
    wayback = query_downloads.archive_query(domain, start_date, end_date)
    gdelt = query_downloads.gdelt_query(domain, start_date, end_date)
    newsapi = query_downloads.newsapi_query(domain, start_date, end_date, os.environ["API_KEY_NEWS"])
    mediacloud = query_downloads.mediacloud_query(domain, start_date, end_date, os.environ["API_KEY_MC"])

    results = {
        "wayback": wayback,
        "gdelt": gdelt,
        "newsapi": newsapi,
        "mediacloud": mediacloud
    }

    return results

# %%
def response_stats(r):
    for k,v in r.items():
        print("Platform: {0}, all records: {1}, unique records: {2}".format(k,
                                                                            len(v),
                                                                            len(set(v['url']))))
    all_links = [v['url'].tolist() for k,v in r.items()]
    all_links = [i for l in all_links for i in l]
    all_links = [i.split("?")[0] for i in all_links]
    unique_links = list(set(all_links))
    print("Total unique URLs across platforms: {}".format(len(unique_links)))

    return unique_links

# %%
def extract_articles(urls):
    g = Goose()
    processed_urls = []
    for i in tqdm(urls):
        try:
            processed = g.extract(i)
            processed_urls.append(processed)
        except ParserError as e:
            pass
    articles = [{"title": i.title,
                 "body": i.cleaned_text,
                 "byline": i.authors,
                 "pub_date": i.publish_date} for i in processed_urls]
    adf = pd.DataFrame(articles)
    adf.loc[:, "url"] = urls

    return adf

# %%
r = get_responses(domain, start_date, end_date, news_key, mc_key)


# %%
links = response_stats(r)


# %%
data = extract_articles(links[0:50])


# %%
