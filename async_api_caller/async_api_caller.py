import aiohttp
import asyncio
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

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
        with Progress(
            SpinnerColumn(),
            "[progress.description]{task.description}",
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TextColumn("[bold blue]{task.completed}/{task.total}")
        ) as progress:

            task = progress.add_task("Fetching data", total=len(param_list))

            tasks = []
            for params in param_list:
                tasks.append(asyncio.create_task(fetch_data(session, url, params, headers)))

            for task_future in asyncio.as_completed(tasks):
                _ = await task_future
                progress.update(task, advance=1)

            # Reorder according to original param_list
            sorted_result = sorted(tasks, key=lambda x: param_list.index(x.result()[0]))

            # Extract the sorted responses now
            responses = [r.result()[1] for r in sorted_result if r.result()[1] is not None]

            return responses

def run(url, headers, param_list):
    return asyncio.run(main(url, headers, param_list))
