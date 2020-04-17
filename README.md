# archive_coverage

## Project structure
`provider_ingestions/` will eventually contain all the underlying functions to query, download, and process links from each platform. Right now, it has functions to make platform queries.

`queries.py` runs the platform queries and is the current home of the URL processing code. 

## Additional files needed
`data/mediacloud_sources.csv` has a list of all Media Cloud media IDs for domains. I generated this by adapting the example in the "Create a CSV file with all media sources." section of the [Media Cloud API documentation](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/api_2_0_spec.md#create-a-csv-file-with-all-media-sources).

You'll also need a [Media Cloud API key](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/api_2_0_spec.md#authentication) and a [News API key](https://newsapi.org/) if you want to query those platforms. 
