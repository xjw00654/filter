# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com


import hashlib
import os
import shutil
import typing
from tempfile import NamedTemporaryFile
from urllib.request import urlopen, Request

from tqdm.auto import tqdm


def exception(caller: typing.Callable, inp: typing.Any, res: typing.Any) -> bool:
    assert res == caller(inp)
    return True


def download_url_to_file(
        url: str,
        dst: str,
        hash_prefix: None = None,
        progress: bool = True,
        user_agent: str = 'DNS-FILTER'
) -> None:
    """ 内容下载模块，会先将文件下载到临时文件内，确认下载正常后移动数据到指定目录内
    :param url: 内容的下载链接
    :param dst: 下载后保存的位置
    :param hash_prefix: 下载文件的哈希值
    :param progress: 是否要展示下载进度条(基于tqdm)
    :param user_agent: 下载请求的UA值
    :return: 没有返回，None
    """

    file_size = None  # 获取文件大小
    req = Request(url, headers={"User-Agent": user_agent})
    u = urlopen(req)
    meta = u.info()
    if hasattr(meta, 'getheaders'):
        content_length = meta.getheaders("Content-Length")
    else:
        content_length = meta.get_all("Content-Length")
    if content_length is not None and len(content_length) > 0:
        file_size = int(content_length[0])

    # 确认文件目录是否存在
    dst = os.path.expanduser(dst)
    dst_dir = os.path.dirname(dst)
    f = NamedTemporaryFile(delete=False, dir=dst_dir)

    try:
        if hash_prefix is not None:
            sha256 = hashlib.sha256()
        with tqdm(total=file_size, disable=not progress,
                  unit='B', unit_scale=True, unit_divisor=1024) as pbar:
            while True:
                buffer = u.read(8192)
                if len(buffer) == 0:
                    break
                f.write(buffer)
                if hash_prefix is not None:
                    sha256.update(buffer)
                pbar.update(len(buffer))

        f.close()
        if hash_prefix is not None:  # 做哈希检验
            print('哈希校验中...')
            digest = sha256.hexdigest()
            if digest[:len(hash_prefix)] != hash_prefix:
                raise Exception(rf'校验错误，sha256校验错误 (expected "{hash_prefix}", got "{digest}")')
            print('sha256校验通过')
        shutil.move(f.name, dst)
    finally:
        f.close()
        if os.path.exists(f.name):
            os.remove(f.name)
