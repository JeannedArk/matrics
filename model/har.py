# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List

import json
import ast


class Har(object):
    def __init__(self, file_path, uid_trace_map):
        self.file_path = file_path
        self.version = None
        self.creator = None
        self.pages: List[HarPage] = None
        self.page_id_page_o_map = None
        self.entries: List[HarEntry] = None
        self.comment = None
        try:
            self.construct_from_file(file_path, uid_trace_map)
        except KeyError as e:
            raise RuntimeError(f"Processing error in file {file_path} : {e}")

    def construct_from_file(self, file_path, uid_trace_map):
        with open(file_path, newline='') as f:
            l = json.load(f)
            log = l['log']
            self.version = log['version']
            self.creator = log['creator']
            self.pages = Har.construct_pages_from_jsono(log['pages'], uid_trace_map)
            self.page_id_page_o_map = {page.id: page for page in self.pages}
            self.entries = Har.construct_entries_from_jsono(log['entries'], self.page_id_page_o_map)
            self.comment = log['comment']

    @staticmethod
    def construct_page_timings_from_jsono(page_timings_j):
        return HarPageTiming(page_timings_j['onLoad'], page_timings_j['comment'])

    @staticmethod
    def construct_pages_from_jsono(pages_j, uid_trace_map):
        pages = []
        for page_j in pages_j:
            actionIdx, traceId = HarPage.parse_title(page_j['title'])
            if traceId in uid_trace_map:
                trace = uid_trace_map[traceId]
            else:
                assert traceId == '-1' and actionIdx == -1,\
                    f"No trace found with actionIdx '{actionIdx}' and traceId '{traceId}' in HarPage."
                trace = None
            page = HarPage(page_j['id'],
                           page_j['startedDateTime'],
                           page_j['title'],
                           Har.construct_page_timings_from_jsono(page_j['pageTimings']),
                           page_j['comment'],
                           actionIdx,
                           traceId,
                           trace)
            pages.append(page)
            if trace is not None:
                trace.network_pages.add(page)
        return pages

    @staticmethod
    def construct_entries_from_jsono(entries_j, page_id_page_o_map) -> List:
        entries = []
        for entry_j in entries_j:
            pageref = page_id_page_o_map[entry_j['pageref']]
            server_ip_address = entry_j['serverIPAddress'] if 'serverIPAddress' in entry_j else ""
            entry = HarEntry(entry_j['pageref'],
                             pageref,
                             entry_j['startedDateTime'],
                             Har.construct_request_from_jsono(entry_j['request']),
                             Har.construct_response_from_jsono(entry_j['response']),
                             entry_j['cache'],
                             Har.construct_timings_from_jsono(entry_j['timings']),
                             server_ip_address,
                             entry_j['comment'])
            entries.append(entry)
            pageref.ref_entries.add(entry)
        return entries

    @staticmethod
    def construct_request_from_jsono(request_j):
        return HarRequest(request_j['method'],
                          request_j['url'],
                          request_j['httpVersion'],
                          request_j['cookies'],
                          request_j['headers'],
                          request_j['queryString'],
                          request_j['headersSize'],
                          request_j['bodySize'],
                          request_j['comment'])

    @staticmethod
    def construct_response_from_jsono(response_j):
        _error = response_j['_error'] if '_error' in response_j else None
        body_size = int(response_j['bodySize'])
        return HarResponse(response_j['status'],
                           response_j['statusText'],
                           response_j['httpVersion'],
                           response_j['cookies'],
                           response_j['headers'],
                           Har.construct_content_from_jsono(response_j['content']),
                           response_j['redirectURL'],
                           response_j['headersSize'],
                           body_size,
                           response_j['comment'],
                           _error)

    @staticmethod
    def construct_timings_from_jsono(timings_j):
        wait = int(timings_j['wait'])
        assert wait >= 0, f"Wait was: {wait}"
        return HarTimings(timings_j['comment'],
                          timings_j['ssl'],
                          timings_j['blocked'],
                          timings_j['receive'],
                          timings_j['dns'],
                          timings_j['send'],
                          timings_j['connect'],
                          wait)

    @staticmethod
    def construct_content_from_jsono(content_j):
        try:
            text = content_j['text'] if 'text' in content_j else ""
            return HarContent(content_j['size'],
                              content_j['mimeType'],
                              text,
                              content_j['comment'])
        except KeyError as e:
            raise KeyError(f"Error processing content_j {content_j} : {e}")


@dataclass
class HarPageTiming:
    onLoad: int
    comment: str


class HarPage(object):
    def __init__(self,
                 id,
                 startedDateTime,
                 title,
                 pageTimings,
                 comment,
                 actionIdx: int,  # Added
                 traceId: str,  # Added
                 trace: object  # Added
                 ):
        self.id = id
        self.startedDateTime = startedDateTime
        self.title = title
        self.pageTimings = pageTimings
        self.comment = comment
        self.actionIdx = actionIdx
        self.traceId = traceId
        self.trace = trace
        # Entries that are referencing this page
        self.ref_entries = set()

    @staticmethod
    def parse_title(title):
        """
        Example:
            actionIdx:3;traceId:12d86c17-78e4-4dac-a9eb-51c82eb6ea5d
        """
        d = ast.literal_eval(title)
        return int(d['actionIdx']), d['traceId']

    def __str__(self):
        return f"Page:\n" \
               f"Title: {self.title}\n" \
               f"ActionIdx: {self.actionIdx}\n" \
               f"TraceId: {self.traceId}\n" \
               f"Started date time: {self.startedDateTime}"

    def copy(self):
        page_copy = HarPage(id=self.id,
                            startedDateTime=self.startedDateTime,
                            title=self.title,
                            pageTimings=self.pageTimings,
                            comment=self.comment,
                            actionIdx=self.actionIdx,
                            traceId=self.traceId,
                            trace=self.trace)
        return page_copy

    def graph_info(self):
        return f"Page:\n" \
               f"Title: {self.title}\n" \
               f"ActionIdx: {self.actionIdx}\n" \
               f"Started date time: {self.startedDateTime}\n" \
               f"Entries: {[entry.graph_info() for entry in self.ref_entries]}"


@dataclass
class HarRequest:
    method: str
    url: str
    httpVersion: str
    cookies: list
    headers: list
    queryString: list
    headersSize: int
    bodySize: int
    comment: str

    def graph_info(self):
        return f"Request(url: {self.url} headersSize: {self.headersSize} bodySize: {self.bodySize})"


@dataclass
class HarContent:
    size: int
    mimeType: str
    text: str
    comment: str

    def graph_info(self):
        return f"Content(size: {self.size})"


@dataclass
class HarResponse:
    status: int
    statusText: str
    httpVersion: str
    cookies: list
    headers: list
    content: HarContent
    redirectURL: str
    headersSize: int
    bodySize: int
    comment: str
    _error: str

    def graph_info(self):
        return f"Response(headersSize: {self.headersSize} bodySize: {self.bodySize} {self.content.graph_info()})"


@dataclass
class HarTimings:
    comment: str
    ssl: int
    blocked: int
    receive: int
    dns: int
    send: int
    connect: int
    wait: int


class HarEntry(object):
    def __init__(self,
                 pageref: str,
                 pageref_o: HarPage,  # Added
                 startedDateTime: str,
                 request: HarRequest,
                 response: HarResponse,
                 cache: None,
                 timings: HarTimings,
                 serverIPAddress: str,
                 comment: str):
        self.pageref = pageref
        self.pageref_o = pageref_o
        self.startedDateTime = startedDateTime
        self.request = request
        self.response = response
        self.cache = cache
        self.timings = timings
        self.serverIPAddress = serverIPAddress
        self.comment = comment

    def __hash__(self):
        return id(self)

    def graph_info(self):
        return f"Entry({self.request.graph_info()} {self.response.graph_info()}"
