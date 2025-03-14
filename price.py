#!/usr/bin/env python3

import asyncio
import aiohttp
import os.path
from math import ceil
from argparse import ArgumentParser

from api import get_routes
from coord import gcj02_to_wgs84
from distance import vincenty, GCJ02, WGS84


async def fetch_route(session, name):
    routes = await get_routes(session, name)
    return [route for route in routes["buslines"] if route["name"].startswith(name)]


def get_stop_distances(route, use_wgs84=False):
    nodes = [[float(k) for k in lng_lat.split(",")] for lng_lat in route["polyline"].split(";")]
    if use_wgs84:
        nodes = [gcj02_to_wgs84(lng, lat) for lng, lat in nodes]

    params = WGS84 if use_wgs84 else GCJ02
    dists = [vincenty(lng1, lat1, lng2, lat2, params) for (lng1, lat1), (lng2, lat2) in zip(nodes[:-1], nodes[1:])]

    stop_locs = [[float(k) for k in stop["location"].split(",")] for stop in route["busstops"]]
    if use_wgs84:
        stop_locs = [gcj02_to_wgs84(lng, lat) for lng, lat in stop_locs]

    start = 0
    indices = [start := nodes.index(stop_loc, start) for stop_loc in stop_locs]
    stop_dists = [sum(dists[:index]) / 1000 for index in indices]

    return stop_dists


def distance_to_number(dists, upgoing=True):
    numbers = [ceil(dist) + 1 for dist in dists]
    if not upgoing:
        end = numbers[-1] + 1
        numbers = [end - number for number in numbers]
    return numbers


async def main():
    parser = ArgumentParser(description="Get pricing information of a bus route")
    parser.add_argument("route", type=str, help="Name of the bus route")
    parser.add_argument("--wgs84", action="store_true", help="Use WGS84 coordinates")
    parser.add_argument("--output", type=str, help="Output directory, print to stdout if not specified")
    args = parser.parse_args()

    async with aiohttp.ClientSession() as session:
        routes = await fetch_route(session, args.route)

    for route in routes:
        print("Processing route:", route["name"])
        stop_dists = get_stop_distances(route, args.wgs84)
        # TODO: Check the direction (upgoing/downgoing) of the route
        stop_numbers = distance_to_number(stop_dists)

        if args.output is not None:
            filename = os.path.join(args.output, route["name"] + ".csv")
            with open(filename, "w", encoding="utf-8") as f:
                f.write("number,stop,distance\n")
                for stop, dist, number in zip(route["busstops"], stop_dists, stop_numbers):
                    f.write(f"{number},{stop['name']},{dist:.3f}\n")
        else:
            print("Name:", route["name"])
            print("number,stop,distance")
            for stop, dist, number in zip(route["busstops"], stop_dists, stop_numbers):
                print(f"{number},{stop["name"]},{dist:.3f}")
            print()


if __name__ == "__main__":
    asyncio.run(main())
