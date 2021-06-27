#!/usr/bin/env python3
import requests
import asyncio
import aiohttp
import urllib
import sys
import os
import concurrent.futures
from collections import deque, Counter
from typing import List
from bs4 import BeautifulSoup, SoupStrainer
import time

DUPLICATES = Counter()

def crawl(url):
    # Initialize the queue for our BFS search of child nodes in the graph
    queue = deque()
    queue.appendleft(url)
    asyncio.run(download_links([url]))

    start_time = time.time()
    counter = 0
    # Begin BFS crawl
    while len(queue) > 0:
        curr_url = queue.popleft()
        curr_url_key = url_to_key(curr_url)
        DUPLICATES[curr_url_key] += 1

        print(curr_url)
        child_links = get_child_links(curr_url)
        asyncio.run(download_links(child_links))

        for child_link in child_links:
            queue.appendleft(child_link)

        if counter == 10:
            break
        counter += 1

    print(f"Time taken: {time.time() - start_time}")


def get_child_links(url):
    # Get the file from the repository
    # or download the page if it doesn't exist.
    url_key = url_to_key(url)
    file_path = f"./crawler_repository/{url_key}"
    if not os.path.exists(file_path):
        return []

    with open(file_path) as f:
        page = f.read()

    child_links = []
    parser = 'html.parser'
    soup = BeautifulSoup(page, parser)

    for link in soup.find_all('a', href=True):
        if link["href"].startswith("http") and DUPLICATES[url_to_key(link["href"])] == 0:
            print(f"\t{link['href']}")
            child_links.append(link["href"])

    return child_links


def url_to_key(url):
    return urllib.parse.quote_plus(url.lstrip("http://").lstrip("https://").strip("/"))


async def get_page(url, session):
    try:
        async with session.get(url=url) as response:
            response = await response.read()
            url_key = url_to_key(url)
            with open(f"./crawler_repository/{url_key}", "wb") as f:
                f.write(response)
    except Exception as e:
        print(e)


async def download_links(urls):
    try:
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[ get_page(url, session) for url in urls])

    except Exception as e:
        print(e)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please make sure you're passing in a url and no other arguments")
        sys.exit(1)
    crawl(sys.argv[1])
