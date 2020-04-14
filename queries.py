# %%
import os
from datetime import datetime

import pandas as pd

from provider_ingestions import query_downloads

from dotenv import load_dotenv

load_dotenv()

# %%
start_date = datetime.strptime("2020-03-01", "%Y-%m-%d")
end_date = datetime.strptime("2020-03-31", "%Y-%m-%d")


# %%
r = query_downloads.archive_query("nytimes.com", start_date, end_date)


# %%
r = query_downloads.gdelt_query("nytimes.com", start_date, end_date)


# %%
r = query_downloads.newsapi_query("nytimes.com", datetime.strftime(start_date, "%Y-%m-%d"), datetime.strftime(end_date, "%Y-%m-%d"), os.environ["API_KEY_NEWS"])

# %%
mc_sources = pd.read_csv("./data/mediacloud_sources.csv")

# %%
mc_sources[mc_sources['url']=='http://nytimes.com']['media_id'].values[0]

# %%
r = query_downloads.mediacloud_query("media_id:1", start_date, end_date, os.environ["API_KEY_MC"])


# %%
