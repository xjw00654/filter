# DNS 异常审核

[![wakatime](https://wakatime.com/badge/github/xjw00654/filter.svg)](https://wakatime.com/badge/github/xjw00654/filter)

## 目录

- [环境需求](环境需求)
- [数据解析](#数据解析)
- [异步数据捕获](#异步数据捕获)
- [静态文件查询](#静态文件查询)
- [API查询接口](#API接口)
- [特征计算模块](#特征计算模块)
- [使用方式](#使用方式)

## 环境需求

- `Python >= 3.6` for runtime environment
- `pytorch` for `dga_analysis` module in [main.py](main.py)
- `dpkt` for pcap package loading
- `tqdm` for progress bar illustration
- `numpy` for data process
- `socket` for ip conversion
- `memocach` for memory caching speedup query
- `numba` for acceleration of simple loop
- `urllib` for static file download
- `pydb` for key-value like memory cache

## 数据解析

相关代码所在位置: [code](package_parser/main.py)

- **FUNCTION**
  - `pcap_parser_generator(line 9)`: pcap 包解析生成器，给定pcap包文件目录，返回一个数据迭代器，其中会过滤所有的非DNS数据包，同时在迭代过程中会产生一个进度条便于掌控当前数据处理速度。

## 异步数据捕获

相关代码所在位置: [code](package_puller/main.py)

- **FUNCTION**
  - `get_cdn_ip(line: 15)` 获取cdnip列表并构建pydb内存数据库
  - `get_wl_db(line 30)` 获取白名单列表并构建pydb内存数据库
  - `sent_data(line 62)` 监测指定目录，当未处理数据超过`n_procs+1`时，往未处理数据队列中运送未处理数据，每10s进行一次文件目录查询，注意3600s没有新文件产生将会做一次最终处理并向队列输送停止标识
  - `filter_wl(line 125)` 白名单过滤主函数（多进程的进程函数对象），从未处理队列中拿数据，处理并在处理完成后将原始数据删除

## 静态文件查询

对应数据下载代码: [utils.py](utils.py)

- [ip_geoIP](analyzer/dns_layer/functional/ip_geoIP.py) datasets
  - **VARIABLE**
    - `_UA(line: 11)`: User-Agent值，可以设定为自己的UA，也可以使用自己的值
    - `_LICENSE_KEY(line: 14)`: 序列号，请访问 [链接](https://www.maxmind.com/en/home) 自行注册获取
  - **CLASS**
    - `Client(line: 84)`: 查询客户端，初始化参数有两个（都是关于GeoIP数据库的下载）:
      - 初始化参数:
        - `download_new_mmdb: bool = False` 默认不进行更新，且如果更新间隔小于一天也，即使设置也不会进行下载(feature not bug :-) )
        - `force = False = False` 是否要强制更新，具体看上一条
      - 调用函数:
        - `query_asn(ip: [str, list])` -> dict: asn查询接口，支持批量查询（给定list of str）
        - `query_country(ip: [str, list])` -> dict: 国家查询接口，支持批量查询（给定list of str）
        - `query_city(ip: [str, list])` -> dict: 城市查询接口，支持批量查询（给定list of str）
        - `query_all(ip: [str, list])` -> dict: asn，城市，国家联合查询接口，支持批量查询（给定list of str）
  - **FUNCTION**
    - `download_mmdb(line: 24)`：Client类用到的数据下载接口函数，内嵌哈希校验，利用tempfile下载到临时文件中，校验无误后移动到指定目录位置
- [domain name whitelist](analyzer/dns_layer/functional/ip_geoIP.py) datasets
  - **VARIABLE**
    - `_UA(line: 9)`: User-Agent值，可以设定为自己的UA，也可以使用自己的值
    - `_V2RAY_RULES_URLs(line: 15)`: 防火墙下载链接，字典形式，以key(数据名)和value(下载链接)的形式存在，可以自行添加（注意不支持lic校验）
    - `_TOP1m_URLs(line: 33)`: top1m数据下载链接，字典形式，以key(数据供应商)和value(下载链接)的形式存在，可以自行添加（注意不支持lic校验）
  - **FUNCTION**
    - `generate_whitelist_domain_names(line: 99)`:
          生成域名白名单，包含v2ray-rules以及alexa-1m历史排名数据，具体的调用情况可以参考[ip_geoIP::Client](#ip_geoIP)
- [gibberish](analyzer/dns_layer/functional/gibberish_detect/gib_detect.py) value
  - **CLASS**
    - `Client(line: 13)`:
          检查该文本段是否符合人的发音标准，该数值的预测需要[训练](analyzer/dns_layer/functional/gibberish_detect/gib_detect_train.py)
          ，训练后会生成静态模型文件(static_files/gib_model.pki)
      - 初始化参数: None
      - 调用函数:
        - `query(string: str, with_prob: bool = True) -> dict` : 单记录查询接口，支持返回预测概率
        - `query_batch(string: str, with_prob: bool = True) -> dict`: 批量查询接口，支持返回预测概率

## API查询接口

- [ICP Query](analyzer/dns_layer/functional/icp_query.py) ICP查询接口
  - **VARIABLE**
    - `_ICP_API_KEY(line: 11)`: 站长之家查询KEY，请登录 [链接](http://my.chinaz.com/ChinazAPI/Statistics/AccessStatistics)
          开通自己的key，免费100条
  - **FUNCTION**
    - `icp_api_query(line: 12)`: ICP记录查询接口，提供domain_name即可

- [WHOIS Query](analyzer/dns_layer/functional/whois_query.py) WHOIS查询接口
  - **VARIABLE**
    - `WHOIS_API_KEY(line: 11)`: 站长之家查询KEY，请登录 [链接](http://my.chinaz.com/ChinazAPI/Statistics/AccessStatistics)
          开通自己的key，免费100条
    - `_RE(line: 15)`: 网站的正则表达式
  - **FUNCTION**
    - `whois_api_query(line: 171)`: whois单条域名查询接口，给定参数`domain_name`返回对应的字典信息，错误返回None
    - `whois_api_query_batch_async(line: 141)`: whois批量查询的异步接口，给定`domain_names`list形式的域名列表传送数据，异步传送数据并轮询查询结果接口

- [BGP Query](analyzer/dns_layer/functional/ip_bgp_query.py) BGP查询接口
  - **FUNCTION**
    - `_iter_window(line: 17)`: 滑动窗函数，随机获取特定数量的记录
  - **CLASS**
    - `Client(line: 87)`: BGP PREFIX查询客户端
      - 初始化参数:
        - `host: str = ’whois.cymru.com‘` 查询主机地址
        - `port: int = 43` 查询主机端口
        - `memcache_host: str = localhost:11211` 内存缓存地址
      - 调用函数
        - `read_and_discard()`: 非阻塞式读取响应内容
        - `disconnect()`: 显式关闭socket链接
        - `get_cached(ips: list) -> dict`: 从缓存中到到响应的结果，减少重复查询的情况，减轻服务器负载
        - `cache(k) -> None`: 缓存结果到MEMCACHE或是内存对象中去，优化后续查询
        - `query(ip: str)`: 单个IP的查询接口，注意大量并发该接口效率非常非常低
        - `query_many(ips: typing.Union[set, list]) -> typing.Generator`: 请求多个ip地址的结果
    - `ASRecord(line: 59)`: AS号查询类，不建议使用
    - `QueryRecord(line: 31)`: 基础查询基础类，不建议使用

## 特征计算模块

- [D-score 值](analyzer/dns_layer/functional/d_score.py) Dscore 计算函数
  - **FUNCTION**
    - `d_score(line: 11)`: 给定两个经纬度(lat1, lng1, lng2, lat2)，利用HaversineRAD，计算两个点（经纬度）之间的欧氏距离
    - `d_score_fast(line: 35)`: 利用简化方法，牺牲一定精度快速计算两个点（经纬度）之间的欧氏距离

- [nlp 特征值](analyzer/dns_layer/functional/domain_name_nlp_features.py) 域名的NLP特征计算函数
  - **FUNCTION**
    - `cal_ngram(line: 100)`: 计算ngram特征，主要是频率特征，具体有两个参数一个是ngram中的`n`，还有一个是需要计算的数据`data`字段
    - `cal_freq(line: 132)`: 计算频率特征，包含数字字符，元音字符，非元音字符，重复字符，连续字符，连续非元音字符的数量。
    - `get_features(line: 78)`: 计算ngram特征，默认参数`tfidf_feature: bool = True`的情况下，返回TF-IDF的特征值
    - `get_whitelist_from_txt(line: 22)`: 获取白名单数据集
    - `get_dga_from_txt(line: 22)`: 从360数据上获取dga域名数据

- [entropy 值](analyzer/dns_layer/functional/entropy.py) 域名的熵值计算
  - **FUNCTION**
    - `cal_entropy_batch(line: 13)`: 计算一个批次中所有数据的熵值，需要一个list或者tuple，或者np.ndarray，支持`do_length_normalization`
          域名长度归一化，和对是否需要将字符数据中的'.'纳入熵值计算的判断
    - `cal_entropy_group(line: 38)`: 对于整组的字符串数据进行熵值计算，返回一个整体的熵值，需要一个list或者tuple，或者是已经整合成一个的str**不需要使用间隔符**
    - `cal_entropy(line: 59)`: 计算单个字符串的熵值
    -

- [AX 值](analyzer/fast_flucos.py) 暂时还存在问题，短期效率上需要提升

## 使用方式

#### demo.1 [代码位置](analyzer/dns_layer/pcap_A_record_statistics.py)

demo.1的核心功能是将一个完整的pcap包中所有的A记录数据进行捕捉，并以A记录数据中的IP为key，整合整个pcap包中重复（同dst的响应）的数据，将所有记录的ttl值，以及一些bgp、icp、asn值的查询结果进行整合保存

- 调用方式：使用12行的`pcap_A_record_statistics`函数，给定`pcap`参数的值，即可得到响应的完整的处理结果
- 参数介绍：
  - `pcap`: pcap包所在目录
  - `do_asn_query`: 是否对记录同步查询asn值
  - `do_city_query`: 是否对记录同步查询城市位置
  - `do_country_query`: 是否对记录同步查询国家位置
  - `do_bgp_prefix_query`: 是否对记录同步查询BGP头信息
- 处理时间：12c AMD R5 3600U 笔记本大约2w条数据/s

#### demo.2 [代码位置](analyzer/ip_layer/pcap_same_src_ip.py)

demo.2的核心功能与demo.1完全相悖，主要是将整个pcap包中所有的A记录数据进行捕捉，但是以A记录中的域名为key，整合重复的结果

- 调用方式：使用40行的`pcap_same_src_ip`函数，给定`pcap_g`参数的值，即可得到响应的完整的处理结果
- 参数介绍：
  - `pcap_g`: pcap包数据迭代器，具体参考[code](package_parser/main.py)
- 处理时间：12c AMD R5 3600U 笔记本大约2w条数据/s
