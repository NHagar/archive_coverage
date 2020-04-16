# %%
import os
from datetime import datetime, timedelta

import pandas as pd

from provider_ingestions import query_downloads

from dotenv import load_dotenv

load_dotenv()

# %%
start_date = datetime.strptime("2020-03-01", "%Y-%m-%d")
end_date = datetime.strptime("2020-03-31", "%Y-%m-%d")
domain = "foxnews.com"
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
r = get_responses(domain, start_date, end_date, news_key, mc_key)


# %%
