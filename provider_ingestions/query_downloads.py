import requests
import pandas as pd
import mediacloud.api
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
from newsapi import NewsApiClient

def archive_query(domain, start_date, end_date):
    url = 'https://web.archive.org/cdx/search/cdx'
    params = {"url": domain,
            "matchType": "domain",
            "from": start_date,
            "to": end_date,
            "output": "json"}
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    response = requests.get(url, params=params, headers=headers).json()
    return response


def gdelt_query(domain, start_date, end_date):
    url = 'http://data.gdeltproject.org/events/'
    # TODO: generate date range
    date_range = []
    date_range_encoded = [10000*dt_time.year + 100*dt_time.month + dt_time.day for dt_time in date_range]
    uris = ['{}.export.CSV.zip'.format(i) for i in date_range_encoded]
    urls = ['{0}{1}'.format(url, i) for i in uris]

    df_all = []

    for i in urls:
        page = urlopen(i)
        zipfile = ZipFile(BytesIO(page.read()))
        filename = zipfile.namelist()[0]
        df = pd.read_csv(zipfile.open(filename), sep='\t', header=None)
        nyt_links = df[df[57].str.contains('www.nytimes')][57]
        df_filtered = pd.DataFrame({'urls': nyt_links, 'date': filename})
        df_all.append(df_filtered)
    
    df_all = pd.concat(df_all).drop_duplicates()
    return df_all


def newsapi_query(domain, start_date, end_date, api_key):
    newsapi = NewsApiClient(api_key=api_key)
    all_articles = newsapi.get_everything(domains=domain,
                                          from_param=start_date,
                                          to=end_date)
    
    return all_articles


def mediacloud_query(domain, start_date, end_date, api_key):
    mc = mediacloud.api.MediaCloud(api_key)
    # TODO: query domain ID
    stories = mc.storyCount(domain, 
                            solr_filter=mc.publish_date_query(start_date, end_date)
                            )

    return stories


def cc_query(domain, start_date, end_date):
    ""