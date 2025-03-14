#!/usr/bin/env python3

import asyncio
import aiosqlite
import aiohttp
import re
from argparse import ArgumentParser

from api import get_routes

MAX_CONCURRENT_REQUESTS = 10


async def init_db(path):
    db = await aiosqlite.connect(path)
    with open("schema.sql") as f:
        await db.executescript(f.read())
    return db


async def fetch_route(session, name):
    routes = await get_routes(session, name)
    return [route for route in routes["buslines"] if route["name"].startswith(name)]


async def process_route(db, route):
    # Insert stops
    for stop in route["busstops"]:
        stop_id = stop["id"][2:] # Remove 'BV' prefix
        try:
            await db.execute("INSERT INTO stop VALUES (?, ?, ?, ?)", (
                stop_id, stop["name"], *stop["location"].split(","),
            ))
        except aiosqlite.IntegrityError:
            # print(f"Stop {stop["id"]} already exists")
            pass

    # Insert route
    route_name = re.match(r"(.+)\(.+--.+\)", route["name"]).group(1) # Remove direction
    start_stop_id = route["busstops"][0]["id"][2:] # Remove 'BV' prefix
    end_stop_id = route["busstops"][-1]["id"][2:]  # Remove 'BV' prefix
    await db.execute("INSERT INTO route VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
        route["id"],
        route["type"] or None,    # Empty list if unknown
        route_name,
        start_stop_id,
        end_stop_id,
        route["loop"],
        route["direc"],
        route["company"] or None, # Empty list if unknown
        route["distance"],
        route["basic_price"],
        route["total_price"],
        route["polyline"],
    ))

    # Insert route stops
    await db.executemany("INSERT INTO route_stop VALUES (?, ?, ?)", (
        (route["id"], stop["sequence"], stop["id"][2:])
        for stop in route["busstops"]
    ))

    await db.commit()


async def fetch_and_process(session, db, name):
    print(f"Fetching route {name}...")
    routes = await fetch_route(session, name)

    print(f"Processing route {name}...")
    for route in routes:
        await process_route(db, route)

    print(f"Route {name} done")


async def main():
    parser = ArgumentParser(description="Fetch and store bus route information")
    parser.add_argument("database", type=str, help="Database filename")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of concurrent requests")
    args = parser.parse_args()

    db = await init_db(args.database)

    # TODO: Add more route names
    names = [f"{i}路" for i in range(1, 1000)]

    connector = aiohttp.TCPConnector(limit=args.limit)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(fetch_and_process(session, db, name)) for name in names]
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            print("Task cancelled")
        except ExceptionGroup as e:
            print(f"Error occurred: {e.exceptions}")
        except Exception as e:
            print(f"Error occurred: {e}")

    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
