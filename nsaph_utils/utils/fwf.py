#  Copyright (c) 2022. Harvard University
#
#  Developed by Research Software Engineering,
#  Faculty of Arts and Sciences, Research Computing (FAS RC)
#  Author: Michael A Bouzinier
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import logging
import os
from typing import List, Tuple
from dateutil import parser as date_parser


class FWFColumn:
    def __init__(self, order: int, name: str, type: str, start: int,
                 width: Tuple[int,int]):
        self.name = name
        self.type = type
        self.ord = order
        self.start = start
        self.length = width[0]
        self.end = self.start + self.length
        self.d = width[1]

    def __str__(self) -> str:
        return "{}:[{:d}-{:d}]".format(self.name,
                                       self.start,
                                       self.start + self.length
        )


class FWFMeta:
    def __init__(self, path: str, record_len: int,
                 columns: List[FWFColumn],
                 number_of_rows=None, size=None):
        self.rlen = record_len
        self.ncol = len(columns)
        self.nrows = number_of_rows
        self.size =  os.path.getsize(path)
        if size is not None:
            #assert self.size == size
            logging.warning("Size mismatch: expected: {:,}; actual: {:,}"
                            .format(self.size, size))
        self.path = path
        self.columns = columns
        return


class FWFReader:
    def __init__(self, meta: FWFMeta, ret_dict: bool = False):
        self.metadata = meta
        self.input = None
        self.rdict = ret_dict
        self.line = 0
        self.data= None
        self.good_lines = 0
        self.bad_lines = 0
        self.nb = 1000
        self.nr = 0
        self.b = 0
        self.record_start_pos = 0
        self.eof_len = None

    def column_names(self) -> List[str]:
        return [c.name for c in self.metadata.columns]

    def open(self):
        if self.input is not None:
            return
        if self.eof_len is None:
            with open(self.metadata.path, "rb") as f:
                b = f.read(self.metadata.rlen)
                self.eof_len = 0
                while f.read(1)[0] in [10, 13]:
                    self.eof_len += 1
        self.input = open(self.metadata.path, "rb")

    def close(self):
        if self.input is not None:
            self.input.close()
        return

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def validate(self):
        pass

    def __str__(self):
        return super().__str__() + ": " + self.metadata.path

    def read_record(self):
        i1 = self.record_start_pos + self.metadata.rlen
        data = self.data[self.record_start_pos:i1]
        while i1 < len(self.data) and self.data[i1] in [10, 13]:
            i1 += 1
        self.record_start_pos = i1
        exception_count = 0
        pieces = []
        n = len(self.metadata.columns)
        for c in self.metadata.columns:
            try:
                pieces.append(data[c.start:c.end])
            except:
                raise
        record = []
        for i in range(n):
            column = self.metadata.columns[i]
            s = pieces[i].decode("utf-8")
            try:
                if column.type == "NUM" and not column.d:
                    val = s.strip()
                    if val:
                        record.append(int(val))
                    else:
                        record.append(None)
                elif column.type == "DATE":
                    v = s.strip()
                    if v:
                    #     if len(v) == len(s) - 2:
                    #         v = v + '01'
                    #     elif len(v) == len(s) - 4:
                    #         v = v + '0101'
                         record.append(date_parser.parse(v))
                    else:
                        record.append(None)
                else:
                    record.append(s)
            except Exception as x:
                logging.exception("{:d}: {}[{:d}]: - {}".format(
                    self.line, column.name, column.ord, str(x))
                )
                record.append(s)
                exception_count += 1
                if exception_count > 3:
                    logging.error(data)
                    raise FTSParseException("Too meany exceptions", column.start)
        return record

    def next(self):
        if self.data is None or self.b >= self.nr:
            rlen = self.metadata.rlen + self.eof_len
            # +2 for '\r\n'
            self.data = self.input.read(rlen * self.nb)
            self.nr = len(self.data) / rlen
            self.b = 0
            self.record_start_pos = 0
        try:
            self.line += 1
            self.b += 1
            record = self.read_record()
            self.good_lines += 1
        except FTSParseException as x:
            logging.exception("Line = " + str(self.line) + ':' + str(x.pos))
            self.bad_lines += 1
            self.on_parse_exception()
            return None
        except AssertionError as x:
            logging.exception("Line = " + str(self.line))
            self.bad_lines += 1
            self.on_parse_exception()
            return None
        if self.rdict:
            record = {
                self.metadata.columns[i].name:
                    record[i] for i in range(self.metadata.ncol)
            }
        return record

    def on_parse_exception(self):
        pass


class FTSParseException(Exception):
    def __init__(self, msg:str, pos:int):
        super(FTSParseException, self).__init__(msg, pos)
        self.pos = pos


