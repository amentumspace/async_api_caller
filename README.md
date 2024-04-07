# async_api_caller

Making asynchronous web API calls using asyncio is complicated. This package abstracts away complexity for the common case of needing to make multiple web API calls while varying query parameters. 

## Installation 

Clone this repo. 

```bash
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

## Sponsor 

[Amentum Scientific](https://amentum.io)

