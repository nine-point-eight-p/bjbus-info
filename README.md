# bjbus-info

通过高德地图 API 获取北京公交路线数据。

## 项目结构

### 脚本

- `info.py`：通过 API 获取全部公交路线信息，并存储在一个 SQLite 数据库中。信息包括：

    - 路线：ID、类型、名称、始末站、是否为环线、对向路线、运营公司、线路长度、基础票价、最高票价、线路轨迹、经停车站

    - 车站：ID、名称、经纬度坐标

- `price.py`：通过 API 获取指定公交路线的经停车站和轨迹，计算每个车站距起始站的距离，得到站号。

### 其他

- `api.py`：向高德地图 API 发送请求。

- `coord.py`：坐标系转换，引用自 [coordTransform_py](https://github.com/wandergis/coordTransform_py).

- `distance.py`：根据 [Haversine 公式](https://en.wikipedia.org/wiki/Haversine_formula)或 [Vincenty 公式](https://en.wikipedia.org/wiki/Vincenty%27s_formulae)计算两个经纬度坐标之间的距离。

## 如何运行

1. 配置环境：

    ```
    python=3.13.2
    aiohttp=3.11.10
    aiosqlite=0.18.0
    fake-useragent=2.0.3
    pyyaml=6.0.2
    ```

2. 获取高德 JS API 的访问权限（[参考链接](https://blog.csdn.net/qq_22841387/article/details/127221064)），将 key 和安全密钥填入当前目录下的 `keys.yaml` 中，格式如下：

    ```yaml
    amap:
      key: <你的 key>
      jscode: <你的安全密钥>
    ```

3. 运行脚本：

    ```shell
    ./info.py -h
    usage: info.py [-h] [--limit LIMIT] database

    Fetch and store bus route information

    positional arguments:
    database       Database filename

    options:
    -h, --help     show this help message and exit
    --limit LIMIT  Maximum number of concurrent requests
    ```

    ```shell
    ./price.py -h
    usage: price.py [-h] [--wgs84] [--output OUTPUT] route

    Get pricing information of a bus route

    positional arguments:
    route            Name of the bus route

    options:
    -h, --help       show this help message and exit
    --wgs84          Use WGS84 coordinates
    --output OUTPUT  Output directory, print to stdout if not specified
    ```

## 参考资料

### 高德 API

- [使用高德 JS API 获取公交数据](https://blog.csdn.net/sheyueyu/article/details/135442164)

- [高德 API 文档](https://lbs.amap.com/api/javascript-api-v2/guide/services/bus)

- [高德 API 示例](https://lbs.amap.com/demo/javascript-api-v2/example/bus-info/search-bus-route)

- [高德 JS 加载](https://lbs.amap.com/api/javascript-api-v2/guide/abc/load)

### 坐标系

- [常见地图坐标系](https://github.com/lhywell/map/blob/master/docs/3.1README.md)

- [WGS84 与 GCJ02 转换公式](https://blog.csdn.net/feinifi/article/details/120547127)

- [WGS84 与 GCJ02 转换实现](https://blog.csdn.net/weixin_43773218/article/details/132145772)