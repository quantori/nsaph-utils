import codecs
import csv
import datetime
import gzip
import io
import json
import logging
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import IO, List
from abc import ABC, abstractmethod

import requests
import yaml
from dateutil.parser import parse
from requests.models import Response
from rpy2.robjects import DataFrame

from nsaph_utils.utils.pyfst import vector2list, FSTReader

logger = logging.getLogger(__name__)


class DownloadTask:
    def __init__(self, destination: str, urls: List = None, metadata = None):
        self.destination = destination
        if urls:
            self.urls = urls
        else:
            self.urls = []
        self.metadata = metadata

    def add_url(self, url: str):
        self.urls.append(url)

    def reset(self):
        os.remove(self.destination)

    def __str__(self):
        dest = os.path.abspath(self.destination)
        if len(self.urls) == 1:
            return "{} ==> {}".format(self.urls[0], dest)
        return "[{:d}]==> {}".format(len(self.urls), dest)

    def is_up_to_date(self, is_transformed: bool = True):
        if len(self.urls) == 1 and not is_transformed:
            return is_downloaded(self.urls[0], self.destination)
        for url in self.urls:
            if not is_downloaded(url, self.destination, 1000):
                return False
        return True


def as_stream(url: str, extension: str = ".csv"):
    """
    Returns the content of URL as a stream. In case the content is in zip
    format (excluding gzip) creates a temporary file

    :param url: URL
    :param extension: optional, when the content is zip-encoded, the extension
        of the zip entry to return
    :return: Content of the URL or a zip entry
    """
    response = requests.get(url, stream=True)
    check_http_response(response)
    raw = response.raw
    if url.lower().endswith(".zip"):
        tfile = tempfile.TemporaryFile()
        download(url, tfile)
        tfile.seek(0)
        zfile = zipfile.ZipFile(tfile)
        entries = [
            e for e in zfile.namelist() if e.endswith(extension)
        ]
        assert len(entries) == 1
        stream = io.TextIOWrapper(zfile.open(entries[0]))
    else:
        stream = raw
    return stream


def as_csv_reader(url: str):
    """
    An utility method to return the CSV content of the URL as CSVReader

    :param url: URL
    :return: an instance of csv.DictReader
    """
    stream = as_stream(url)
    reader = csv.DictReader(stream, quotechar='"', delimiter=',',
        quoting=csv.QUOTE_NONNUMERIC, skipinitialspace=True)
    return reader


def fopen(path: str, mode: str):
    """
    A wrapper to open various types of files

    :param path: Path to file
    :param mode: Opening mode
    :return: file-like object
    """
    if isinstance(path, io.BufferedReader):
        return codecs.getreader("utf-8")(path)
    if path.lower().endswith(".gz"):
        #return io.TextIOWrapper(gzip.open(path, mode))
        return gzip.open(path, mode)
    if 'b' in mode:
        return open(path, mode)
    return open(path, mode, encoding="utf-8")


def check_http_response(r: Response):
    """
    An internal method raises an exception of HTTP response is not OK

    :param r: Response
    :return: nothing, raises an exception if response is not OK
    """
    if not r.ok:
        msg = "HTTP Response: {:d}; Reason: {}".format(r.status_code, r.reason)
        raise Exception(msg)


def download(url: str, to: IO):
    """An utility method to download large binary data to a file-like object"""
    response = requests.get(url, stream=True)
    for chunk in response.iter_content(chunk_size=1048576):
        to.write(chunk)
        print('#', end='')
    print('.', end=' ')
    return


def is_downloaded(url: str, target: str, check_size: int = 0) -> bool:
    """
    Checks if the same data has already been downloaded

    :param check_size: Use default value (0) if target size should be equal
        to source size. If several urls are combined when downloaded
        then specify a positive integer to check that destination file
        size is greater than the specified value. Specifying negative
        value will disable size check
    :param url: URL with data
    :param target: Destination of teh downloads
    :return: True if the destination file exists and is newer than
        URL content
    """
    if os.path.isfile(target):
        response = requests.head(url, allow_redirects=True)
        check_http_response(response)
        headers = response.headers
        remote_size = int(headers.get('content-length', 0))
        remote_date = parse(headers.get('Last-Modified', 0))
        stat = os.stat(target)
        local_size = stat.st_size
        local_date = datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        date_check = local_date > remote_date
        if check_size == 0:
            size_check = local_size == remote_size
        else:
            size_check = local_size > check_size
        return date_check and size_check
    return False


def write_csv(reader: csv.DictReader,
              writer: csv.DictWriter,
              transformer=None,
              filter=None,
              write_header: bool = True):
    """
    Rewrites the CSV content optionally transforming and
    filtering rows

    :param transformer: An optional callable that tranmsforms a row in place
    :param reader: Input data as an instance of csv.DictReader
    :param writer: Output source should be provided as csv.DictWriter
    :param filter: Optionally, a callable function returning True
        for rows that should be written to the output and False for those
        that should be omitted
    :param write_header: whether to first write header row
    :return: Nothing
    """
    counter = 0
    if write_header:
        writer.writeheader()
    for row in reader:
        if transformer:
            transformer(row)
        if (not filter) or filter(row):
            writer.writerow(row)
        counter += 1
        if (counter % 10000) == 0:
            print("*", end="")
    print()


def count_lines(f):
    with fopen(f, "r") as x:
        return sum(1 for line in x)


class Collector(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def writerow(self, data: List):
        pass

    def flush(self):
        pass


class CSVWriter(Collector):
    def __init__(self, out_stream):
        super().__init__()
        self.out = out_stream
        self.writer = csv.writer(out_stream,
                                 delimiter=',',
                                 quoting=csv.QUOTE_NONE)

    def writerow(self, row: List):
        self.writer.writerow(row)

    def flush(self):
        self.out.flush()


class ListCollector(Collector):
    def __init__(self):
        super().__init__()
        self.collection = []

    def writerow(self, data: List):
        self.collection.append(data)

    def get_result(self):
        return self.collection


def as_dict(json_or_yaml_file: str) -> dict:
    if isinstance(json_or_yaml_file, str) and os.path.isfile(json_or_yaml_file):
        with open(json_or_yaml_file) as f:
            ff = json_or_yaml_file.lower()
            if ff.endswith(".json"):
                content = json.load(f)
            elif ff.endswith(".yml") or ff.endswith(".yaml"):
                content = yaml.safe_load(f)
            else:
                raise Exception("Unsupported format for user request: {}"
                                .format(json_or_yaml_file) +
                                ". Supported formats are: JSON, YAML")
    elif isinstance(json_or_yaml_file, dict):
        content = json_or_yaml_file
    else:
        t = str(type(json_or_yaml_file))
        raise Exception("Unsupported type of the specification: {}".format(t))
    return content


def dataframe2csv(df: DataFrame, dest: str, append: bool):
    t0 = datetime.datetime.now()
    columns = {
        df.colnames[c]: vector2list(df[c]) for c in range(df.ncol)
    }
    t1 = datetime.datetime.now()

    if append:
        mode = "at"
    else:
        mode = "wt"
    with fopen(dest, mode) as output:
        writer = csv.DictWriter(output, columns, quoting=csv.QUOTE_NONNUMERIC)
        if not append:
            writer.writeheader()
        for r in range(df.nrow):
            row = {
                column: columns[column][r] for column in columns
            }
            writer.writerow(row)
    t2 = datetime.datetime.now()
    print("{} + {} = {}".format(str(t1-t0), str(t2-t1), str(t2-t0)))
    return


def fst2csv(path: str, buffer_size = 10000):
    if not path.endswith(".fst"):
        raise Exception("Unknown format of file " + path)
    name = path[:-4]
    dest = name + ".csv.gz"
    n = 0
    t0 = datetime.now()
    with FSTReader(path, returns_mapping=True) as reader, fopen(dest, "wt") as output:
        writer = csv.DictWriter(output, reader.columns, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        width = len(reader.columns)
        for row in reader:
            writer.writerow(row)
            n += 1
            if (n % buffer_size) == 0:
                t2 = datetime.now()
                rate = n / (t2 - t0).seconds
                logging.info("Read {}: {:d} x {:d}; {} {:f} rows/sec".format(path, n, width, str(t2-t0), rate))
    logger.info("Complete. Total read {}: {:d} x {:d}".format(path, width, n))
    return


