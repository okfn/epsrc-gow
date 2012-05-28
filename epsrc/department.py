from __future__ import print_function

import re

import mechanize
from pyquery import PyQuery

import util

b = browser = mechanize.Browser()

DEPARTMENT_DETAIL_URL = "http://gow.epsrc.ac.uk/NGBOViewDepartment.aspx?DepartmentId=%s"


def scrape_department(id):
    b.open(DEPARTMENT_DETAIL_URL % id)
    return scrape_department_html(id, b.response().read())


def scrape_department_html(id, html):
    department = {'id': id}

    page = PyQuery(html)

    _scrape_name(department, page)
    _scrape_parent(department, page)

    return department


def _scrape_name(o, el):
    o['name'] = ''

    name_el = el.find('#lblDepartmentName').eq(0)

    if name_el:
        o['name'] = name_el.html().strip()


def _scrape_parent(o, el):
    o['organisation'] = {}

    name_el = el.find('#lblOrganisationName').eq(0)

    if name_el:
        o['organisation']['name'] = name_el.html().strip()


