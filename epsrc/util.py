# coding=utf8

import re
from datetime import datetime

from pyquery import PyQuery

_extract_id_memo = {}

def extract_id(str, type):
    pattern = _extract_id_memo.get(type)

    if not pattern:
        pattern = _extract_id_memo[type] = r"%sId=(\-?\d+)" % type

    m = re.search(pattern, str)
    return int(m.group(1))

def extract_multiple_ids(elem, type):
    res = []

    for el in (PyQuery(x) for x in elem.find("a")):
        o = {}
        o['id'] = extract_id(el.attr.href, type)
        o['name'] = el.text()
        res.append(o)

    return res

def extract_monetary_value(str):
    return float(re.sub(r"[£,]", '', str))

def extract_date(str, format="%d %B %Y"):
    return datetime.strptime(str, format).date().isoformat()
