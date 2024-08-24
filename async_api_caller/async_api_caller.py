import aiohttp
import asyncio
import json
import hashlib
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import sqlite3
import numpy as np

class SQLiteCache:
    def __init__(self, db_name='cache.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    expires_at INTEGER
                )
            ''')

    def get(self, key):
        cur = self.conn.cursor()
        cur.execute('SELECT value, expires_at FROM cache WHERE key=?', (key,))
        row = cur.fetchone()
        if row:
            value, expires_at = row
            if expires_at is None or expires_at > int(asyncio.get_event_loop().time()):
                return json.loads(value)
        return None

    def set(self, key, value, ttl=None):
        expires_at = int(asyncio.get_event_loop().time()) + ttl if ttl else None
        with self.conn:
            self.conn.execute('''
                REPLACE INTO cache (key, value, expires_at)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(value), expires_at))

    def clear(self):
        with self.conn:
            self.conn.execute('DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at <= ?', (int(asyncio.get_event_loop().time()),))

    def close(self):
        self.conn.close()


def make_values_json_serializable(d):
    return {key: make_json_serializable(value) for key, value in d.items()}

def make_json_serializable(value):
    if isinstance(value, np.integer):
        return int(value)
    elif isinstance(value, np.floating):
        return float(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()  # Convert NumPy arrays to lists
    elif isinstance(value, (np.bool_, bool)):
        return bool(value)  # Ensure boolean types are handled
    elif isinstance(value, (np.str_, str)):
        return str(value)
    else:
        return value
    
# Function to create a hash for the cache key
def hash_key(url, params):
    # required for numpy types in param list
    params_serialisable = make_values_json_serializable(params)
    params_json = json.dumps(params_serialisable, sort_keys=True)
    key = f"{url}_{params_json}"
    return hashlib.md5(key.encode()).hexdigest()

# Makes the API call asynchronously
async def fetch_data(session, url, params=None, headers=None, cache=None, ttl=360000):
    
    # return cached response if present
    key = hash_key(url, params)
    if cache:
        cached_response = cache.get(key)
        if cached_response:
            return params, cached_response
    try:
        async with session.get(url, params=params, headers=headers) as resp:
            resp.raise_for_status()  # Raises an exception for HTTP errors
            response_json = await resp.json()
            if cache:
                cache.set(key, response_json, ttl)
            return params, response_json
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
        return params, None

# A function that receives a url, header, and list of params that vary 
async def main(url, headers, param_list):
    cache = SQLiteCache()  # Initialize the custom SQLite cache
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
                tasks.append(asyncio.create_task(fetch_data(session, url, params, headers, cache)))

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
