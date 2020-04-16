# %%
import os
from datetime import datetime

import pandas as pd

from provider_ingestions import query_downloads

from dotenv import load_dotenv

load_dotenv()

# %%
start_date = datetime.strptime("2020-03-16", "%Y-%m-%d")
end_date = datetime.strptime("2020-03-31", "%Y-%m-%d")
domain = "nytimes.com"

# %%
def get_responses(domain, start_date, end_date, news_api_key, mc_key):
    wayback = query_downloads.archive_query(domain, start_date, end_date)
    gdelt = query_downloads.gdelt(domain, start_date, end_date)
    newsapi = query_downloads.newsapi_query(domain, start_date, end_date, os.environ["API_KEY_NEWS"])
    mediacloud = query_downloads.mediacloud(domain, start_date, end_date, os.environ["API_KEY_MC"])

    results = {
        "wayback": wayback,
        "gdelt": gdelt,
        "newsapi": newsapi,
        "mediacloud": mediacloud
    }

    return results


# %%
mc_sources = pd.read_csv("./data/mediacloud_sources.csv")

# %%
mc_sources[mc_sources['url']=='http://nytimes.com']['media_id'].values[0]

# %%
r = query_downloads.mediacloud_query("media_id:1", start_date, end_date, os.environ["API_KEY_MC"])


# %%
r = query_downloads.cc_query("cnn.com", start_date, end_date)
