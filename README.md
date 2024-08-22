# async_api_caller

Making asynchronous web API calls using asyncio is pretty complicated. This package abstracts away complexity for the common case of needing to make multiple web API calls while varying query parameters. 

## Installation 

Clone this repo, then: 

```bash
cd async_api_caller/
pip install . 
```

## Usage 

```Python
import async_api_caller
url = "https://ocean.amentum.io/gebco"
headers = {'API-Key': API_KEY}
param_list = [
    {
        "latitude": 42,
        "longitude": 42
    },{
        "latitude": 43,
        "longitude": 43
    }
]

responses_json = async_api_caller.run(
    url, headers, param_list
)
```

## Caching

To avoid making duplicate API calls to metered APIs, responses are automatically cached in a sqlite database `cache.db`. Delete the file to refresh it. 

## Sponsor 

[Amentum Scientific](https://amentum.io)

