import aiohttp
import asyncio

# Makes the API call asynchronously
async def fetch_data(session, url, params=None, headers=None):
    try:
        async with session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()  # Raises an exception for HTTP errors
            response_json = await resp.json()
            return params, response_json
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
        return params, None

# A function that receives a url, header, and list of params that vary 
async def main(url, headers, param_list):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url, params, headers) for params in param_list]
        result = await asyncio.gather(*tasks)

        # Reorder according to original param_list
        sorted_result = sorted(result, key=lambda x: param_list.index(x[0]))
        
        # Extract the sorted responses now
        responses = [r[1] for r in sorted_result if r[1] is not None]

        return responses

def run(url, headers, param_list):
    return asyncio.run(main(url, headers, param_list))
