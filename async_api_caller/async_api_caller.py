#
# A module born out of frustration at how difficult it is to
# use aynsc requests for API calls yet oh how useful they are
# TODO proper exception handling incl. http raise for status
import aiohttp
import asyncio

# makes the API call asyncronously
async def fetch_data(session, url, params=None, headers=None):
    async with session.get(url, params=params, headers=headers) as resp:
        # we return params with responses so we can restore order
        response_json = await resp.json()
        return params, response_json
    
# A function that receives a url, header, and list of params 
# that vary 
async def main(url, headers, param_list):

    async with aiohttp.ClientSession() as session:

        tasks = [] 
        for params in param_list: 
            response_future = asyncio.ensure_future(
                fetch_data(session, url, params, headers)
            )
            tasks.append(response_future)

        result = await asyncio.gather(*tasks)

        # reorder according to original param_list  
        sorted_result = sorted(
            result, key=lambda x: param_list.index(x[0])
        )

        # extract the sorted responses now 
        responses = [r[1] for r in sorted_result]

        return responses
    
def run(url, headers, param_list):

    return asyncio.run(main(url, headers, param_list))
