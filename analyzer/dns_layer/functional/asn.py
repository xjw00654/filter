# coding: utf-8
# author: jwxie - xiejiawei000@gmail.com

from typing import Tuple, List, Union
from hashlib import sha256

_BASE_URL = f'https://download.maxmind.com/app/geoip_download'
_LICENSE_KEY = 'YzIkjIjASarh4lpT'  # !!jwxie!!

URLs = dict(
    asn=f'{_BASE_URL}?edition_id=GeoLite2-ASN&license_key={_LICENSE_KEY}&suffix=tar.gz',
    city=f'{_BASE_URL}?edition_id=GeoLite2-City&license_key={_LICENSE_KEY}&suffix=tar.gz',
    country=f'{_BASE_URL}?edition_id=GeoLite2-Country&license_key={_LICENSE_KEY}&suffix=tar.gz'
)
SHA256 = {k: v + '.sha256' for k, v in URLs.items()}


def download_mmdb():
    pass


def load_state_dict_from_url(url, model_dir=None, map_location=None, progress=True, check_hash=False, file_name=None):
    r"""Loads the Torch serialized object at the given URL.

    If downloaded file is a zip file, it will be automatically
    decompressed.

    If the object is already present in `model_dir`, it's deserialized and
    returned.
    The default value of ``model_dir`` is ``<hub_dir>/checkpoints`` where
    ``hub_dir`` is the directory returned by :func:`~torch.hub.get_dir`.

    Args:
        url (string): URL of the object to download
        model_dir (string, optional): directory in which to save the object
        map_location (optional): a function or a dict specifying how to remap storage locations (see torch.load)
        progress (bool, optional): whether or not to display a progress bar to stderr.
            Default: True
        check_hash(bool, optional): If True, the filename part of the URL should follow the naming convention
            ``filename-<sha256>.ext`` where ``<sha256>`` is the first eight or more
            digits of the SHA256 hash of the contents of the file. The hash is used to
            ensure unique names and to verify the contents of the file.
            Default: False
        file_name (string, optional): name for the downloaded file. Filename from ``url`` will be used if not set.

    """

    if model_dir is None:
        hub_dir = get_dir()
        model_dir = os.path.join(hub_dir, 'checkpoints')

    try:
        os.makedirs(model_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            # Directory already exists, ignore.
            pass
        else:
            # Unexpected OSError, re-raise.
            raise

    parts = urlparse(url)
    filename = os.path.basename(parts.path)
    if file_name is not None:
        filename = file_name
    cached_file = os.path.join(model_dir, filename)
    if not os.path.exists(cached_file):
        sys.stderr.write('Downloading: "{}" to {}\n'.format(url, cached_file))
        hash_prefix = None
        if check_hash:
            r = HASH_REGEX.search(filename)  # r is Optional[Match[str]]
            hash_prefix = r.group(1) if r else None
        download_url_to_file(url, cached_file, hash_prefix, progress=progress)

    if _is_legacy_zip_format(cached_file):
        return _legacy_zip_load(cached_file, model_dir, map_location)
    return torch.load(cached_file, map_location=map_location)



def ip_asn(
        ip: str
) -> Tuple[Union[List[int], str], str]:
    """ 给定ip，返回IP地址对应的国家以及asn号
    :param self:
    :param ip: IP地址
    :return: ASN记录，国家
    """
    asnrec = geoIP.org_by_addr(ip)
    country = self.gl.getCountry(ip)
    if asnrec == None:
        return ['Unknown', 'Unknown']
    else:
        return [asnrec.split(' ')[0], country]
