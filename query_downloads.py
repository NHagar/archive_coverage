from datetime import datetime, timedelta
import requests
import pandas as pd
import mediacloud.api
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
from warcio.archiveiterator import ArchiveIterator
from newsapi import newsapi_exception
from tqdm import tqdm

def archive_query(domain, start_date, end_date):
    start_date = 10000*start_date.year + 100*start_date.month + start_date.day
    end_date = 10000*end_date.year + 100*end_date.month + end_date.day
    url = 'https://web.archive.org/cdx/search/cdx'
    params = {"url": domain,
            "matchType": "domain",
            "from": start_date,
            "to": end_date,
            "output": "json"}
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    response = requests.get(url, params=params, headers=headers).json()
    results = [{"timestamp": i[1], "url": i[2]} for i in response[1:]]
    results = pd.DataFrame(results)

    return results


def gdelt_query(domain, start_date, end_date):
    url = 'http://data.gdeltproject.org/events/'
    date_range = pd.date_range(start=start_date, end=end_date)
    date_range_encoded = [10000*dt_time.year + 100*dt_time.month + dt_time.day for dt_time in date_range]
    uris = ['{}.export.CSV.zip'.format(i) for i in date_range_encoded]
    urls = ['{0}{1}'.format(url, i) for i in uris]

    df_all = []

    for i in urls:
        page = urlopen(i)
        zipfile = ZipFile(BytesIO(page.read()))
        filename = zipfile.namelist()[0]
        df = pd.read_csv(zipfile.open(filename), sep='\t', header=None)
        nyt_links = df[df[57].str.contains(domain)][57]
        df_filtered = pd.DataFrame({'url': nyt_links, 'timestamp': filename})
        df_filtered.loc[:, 'timestamp'] = df_filtered['timestamp'].map(lambda x: x.split(".")[0])
        df_all.append(df_filtered)
    
    df_all = pd.concat(df_all).drop_duplicates()
    return df_all

# TODO: Implement day-to-day pagination to get most possible results
def newsapi_query(domain, start_date, end_date, api_key):
    all_articles = run_newsapi_query(domain, start_date, end_date, api_key)
    all_articles = pd.DataFrame(all_articles)
    return all_articles

def run_newsapi_query(domain, start_date, end_date, api_key):
    newsapi = NewsApiClient(api_key=api_key)
    all_articles = []
    page = 1
    while True:
        try:
            articles = newsapi.get_everything(domains=domain,
                                          from_param=start_date,
                                          to=end_date,
                                          page=page)
            article_info = articles['articles']
            if len(article_info)==0:
                break
            all_articles.extend(article_info)
            page += 1
        except  newsapi_exception.NewsAPIException as e:
            if e.get_code()=="parameterInvalid":
                start_date = datetime.now().date() - timedelta(days=30)
                pass
            elif e.get_code()=='maximumResultsReached':
                break
    return all_articles


def mediacloud_query(domain, start_date, end_date, api_key):
    mc = mediacloud.api.MediaCloud(api_key)
    media_id = mediacloud_lookup(domain)
    if len(media_id)>0:
        all_stories = []
        last_processed_stories_id = 0
        while True:
            stories = mc.storyList(media_id, 
                                    solr_filter=mc.publish_date_query(start_date, end_date),
                                    rows=1000,
                                    last_processed_stories_id=last_processed_stories_id
                                    )
            if len(stories)==0:
                break
            all_stories.extend(stories)
            
            last_processed_stories_id = all_stories[-1]['processed_stories_id']
            print("stories processed: {0} - last id: {1}".format(len(all_stories), last_processed_stories_id))
        stories_df = pd.DataFrame(all_stories)
        stories_df = stories_df[['collect_date', 'publish_date', 'url', 'title']]
    else:
        print("No media ID found for {}".format(domain))
        stories_df = None
    return stories_df


def mediacloud_lookup(domain):
    mc_sources = pd.read_csv("./data/mediacloud_sources.csv")
    domain_variants = ["http://", "https://", "http://www.", "https://www."]
    domain_variants = [i+domain for i in domain_variants]
    media_id = ""
    for i in domain_variants:
        try:
            mid = mc_sources[mc_sources['url']==i].iloc[0]['media_id']
            media_id = "media_id:{}".format(mid)
        except IndexError:
            pass

    return media_id


def cc_query(domain, start_date, end_date):
    year = str(start_date.year)
    month = str(start_date.month)
    month = month if len(month)>1 else "0{}".format(month)
    cc_files = requests.get("https://commoncrawl.s3.amazonaws.com/?prefix=crawl-data/CC-NEWS/{0}/{1}".format(year, month))
    soup = BeautifulSoup(cc_files.text)
    urls = ["https://commoncrawl.s3.amazonaws.com/{}".format(i.text) for i in soup.find_all("key")]
    results = [get_records(i, domain) for i in tqdm(urls)]
    results = [i for l in results for i in l]

    return results


def get_records(url, domain):
    resp = requests.get(url, stream=True)
    records = []

    for record in ArchiveIterator(resp.raw, arc2warc=True):
        if record.rec_type == 'response':
            if record.http_headers.get_header('Content-Type') == 'text/html':
                uri = record.rec_headers.get_header('WARC-Target-URI')
                if domain in uri:
                    records.append(uri)
    return records
