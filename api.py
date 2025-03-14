import yaml
from fake_useragent import UserAgent

ua = UserAgent()

with open("keys.yml", "r") as f:
    keys = yaml.load(f.read(), Loader=yaml.FullLoader)

BASE_URL = "https://restapi.amap.com/v3/bus/linename"
BASE_PARAMS = {
    "platform": "JS",
    "s": "rsv3",
    "sdkversion": "2.0.6.3",
    "logversion": "2.0",
    "extensions": "all",
    "output": "json",
    # "csid": "3F434BC1-71F6-46F2-9450-3BBA8EA65F0B",
    "key": keys["amap"]["key"],
    "jscode": keys["amap"]["jscode"],
    "appname": "bjbus-info",
    "city": "北京",  # City name
    "keywords": "", # Bus name
    "pageIndex": 1, # Page number
    "offset": 10,   # Page size
}


async def get_routes(session, name, page=1, offset=50):
    params = BASE_PARAMS.copy()
    params["keywords"] = name
    params["pageIndex"] = page
    params["offset"] = offset

    headers = {"User-Agent": ua.random}

    async with session.get(BASE_URL, headers=headers, params=params) as resp:
        if resp.status != 200:
            print(f"Failed to get route info for {name}")
            return None
        
        result = await resp.json()
        if result["status"] == 1 or result["info"] == "OK":
            return result
        else:
            print(f"Failed to get route info for {name}")
            return None
