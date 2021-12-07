# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

import errno
import re
import socket
import typing

try:
    import memcache

    HAVE_MEMCACHE = True
except ImportError:
    HAVE_MEMCACHE = False


def iter_window(data, n_per_window=50):
    assert (n_per_window > 0)
    a = []

    for x in data:
        if len(a) >= n_per_window:
            yield a
            a = []
        a.append(x)

    if a:
        yield a


class QueryRecord:
    def __init__(self, asn, ip, prefix, cc, owner):
        def fix(x):
            x = x.strip()
            try:
                x = str(x.decode('ascii', 'ignore'))
            except AttributeError:
                pass  # for Python 3
            return x

        self.asn = fix(asn)
        self.ip = fix(ip)
        self.prefix = fix(prefix)
        self.cc = fix(cc)
        self.owner = fix(owner)

        self.key = self.ip

    def todict(self):
        return {'asn': self.asn, 'ip': self.ip, 'prefix': self.prefix, 'country_code': self.cc, 'owner': self.owner}

    def __str__(self):
        return "%-10s %-16s %-16s %s '%s'" % (self.asn, self.ip, self.prefix, self.cc, self.owner)

    def __repr__(self):
        return "<%s instance: %s|%s|%s|%s|%s>" % (self.__class__, self.asn, self.ip, self.prefix, self.cc, self.owner)


class ASRecord:
    def __init__(self, asn, cc, owner):
        def fix(x):
            x = x.strip()
            if x == "NA":
                return None
            try:
                x = str(x.decode('ascii', 'ignore'))
            except AttributeError:
                pass  # for Python 3
            return x

        self.asn = fix(asn)
        self.cc = fix(cc)
        self.owner = fix(owner)

        self.key = "AS" + self.asn

    def todict(self):
        return {'asn': self.asn, 'country_code': self.cc, 'owner': self.owner}

    def __str__(self):
        return "%-10s %s '%s'" % (self.asn, self.cc, self.owner)

    def __repr__(self):
        return "<%s instance: %s|%s|%s>" % (self.__class__, self.asn, self.cc, self.owner)


class Client:
    """
    BGP prefix查询在线客户端
    """

    def __init__(self, host="whois.cymru.com", port=43, memcache_host='localhost:11211'):
        """
        BGP prefix查询在线客户端初始化函数

        :param host: 查询主机，默认whois.cymru.com
        :param port: 查询主机的端口，默认43
        :param memcache_host: 查询缓存MEMCACHE的端口
        """
        self.host = host
        self.port = port
        self._connected = False
        self.c = None
        if HAVE_MEMCACHE and memcache_host:
            self.c = memcache.Client([memcache_host])

    @staticmethod
    def _make_key(arg):
        """
        创建缓存的键值

        :param arg: 缓存的内容
        :return: 缓存的键值
        """
        if arg.startswith("AS"):
            return "cymru-whois:as:" + arg
        else:
            return "cymru-whois:ip:" + arg

    def _connect(self) -> None:
        """
        创建socket链接到服务器的43端口

        会创建socket请求响应文件self.file对象
        :return:
        """
        self.socket = socket.socket()
        self.socket.settimeout(5.0)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(10.0)
        self.file = self.socket.makefile("rw")

    def _send_line(self, line: str) -> None:
        """
        发起请求内容

        :param line: 请求的ip地址
        :return:
        """
        self.file.write(line + "\r\n")
        self.file.flush()

    def _read_line(self) -> str:
        """
        读取响应内容

        :return:
        """
        return self.file.readline()

    def _disconnect(self) -> None:
        """
        关闭socket请求链接

        :return:
        """
        self.file.close()
        self.socket.close()

    def read_and_discard(self):
        """
        非阻塞式读取响应内容，避免

        :return:
        """
        self.socket.setblocking(False)
        try:
            try:
                self.file.read(1024)
            except socket.error as e:
                # 10035 is WSAEWOULDBLOCK for windows systems on older python versions
                if e.args[0] not in (errno.EAGAIN, errno.EWOULDBLOCK, 10035):
                    raise
        finally:
            self.socket.setblocking(True)

    def _begin(self):
        """
        显式创建socket链接，请求BGPPREFIX+ASNNUMBER+CC并指定notrunc

        :return:
        """
        self._connect()
        self._send_line("BEGIN")
        self._read_line()  # discard the message "Bulk mode; one IP per line. [2005-08-02 18:54:55 GMT]"
        self._send_line("PREFIX\nASNUMBER\nCOUNTRYCODE\nNOTRUNC")
        self._connected = True

    def disconnect(self) -> None:
        """
        显式关闭socket链接

        :return:
        """
        if not self._connected: return

        self._send_line("END")
        self._disconnect()
        self._connected = False

    def get_cached(self, ips: list) -> dict:
        """
        从缓存中到到响应的结果，避免重复查询

        :param ips:
        :return:
        """
        if not self.c:
            return {}
        keys = [self._make_key(ip) for ip in ips]
        values = self.c.get_multi(keys)
        # convert key:value pair into just value
        return dict((k.split(":")[-1], v) for k, v in list(values.items()))

    def cache(self, k) -> None:
        """
        缓存结果到MEMCACHE或是内存对象中去，前者效率更高，没有对象的创建开销

        :param k: 缓存的结果对象
        :return:
        """

        if not self.c:
            return
        self.c.set(self._make_key(k.key), k, 60 * 60 * 6)

    @staticmethod
    def _is_valid_ip(ip: str) -> bool:
        ipv4_eval_exp = re.compile(
            "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        ipv6_eval_exp = re.compile("^([\\da-fA-F]{1,4}:){7}([\\da-fA-F]{1,4})$")

        if ipv4_eval_exp.match(ip) or ipv6_eval_exp.match(ip):
            return True
        else:
            return False

    def query(self, ip):
        """
        单个IP的查询接口，注意千万不要把这个查询接口丢到循环里面去，大可爱们！直接用query_many或者query_many_dict接口

        :param ip: 需要查询的ip值
        :return:
        """

        if self._is_valid_ip(ip):
            return list(self.query_many([ip]))[0]
        else:
            raise Exception('输入错误，不是合法IP地址')

    def query_many(self, ips: typing.Union[set, list]) -> typing.Generator:
        """
        请求多个ip地址的结果

        :param ips:
        :return:
        """
        ips = [e for e in [str(ip).strip() for ip in ips] if self._is_valid_ip(e)]

        for batch in iter_window(ips, 100):
            cached = self.get_cached(batch)
            not_cached = [ip for ip in batch if not cached.get(ip)]
            # print "cached:%d not_cached:%d" % (len(cached), len(not_cached))
            if not_cached:
                for rec in self._query_many_raw(not_cached):
                    cached[rec.key] = rec
            for ip in batch:
                if ip in cached:
                    yield cached[ip]

    def query_many_dict(self, ips: list) -> dict:
        """
        请求查询多个ip地址，并以ip：记录的形式返回结果

        :param ips: IP地址列表
        :return: 字典的的形式返回结果，K为IP，V为记录
        """
        ips = set(ips)
        return dict((e.key, e) for e in self.query_many(ips))

    def _query_many_raw(self, ips: list) -> typing.Generator:
        """
        大批量数据进行数据请求，使用非阻塞的模式批量数据请求

        :param ips: ip列表
        :return:
        """
        if not self._connected:
            self._begin()
        ips = set(ips)
        for ip in ips:
            self._send_line(ip)

        need = len(ips)
        last = None
        while need:
            result = self._read_line()
            if 'Error: no ASN or IP match on line' in result:
                need -= 1
                continue
            parts = result.split("|")
            if len(parts) == 5:
                response = QueryRecord(*parts)
            else:
                response = ASRecord(*parts)

            # check for multiple records being returned for a single IP
            # in this case, just skip any extra records
            if last and response.key == last.key:
                continue

            self.cache(response)
            yield response
            last = response
            need -= 1

        self.read_and_discard()


if __name__ == "__main__":
    c = Client()
    r = c.query('216.90.108.31')
    print(r)
