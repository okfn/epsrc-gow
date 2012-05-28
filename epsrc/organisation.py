from __future__ import print_function

import re

import mechanize
from pyquery import PyQuery

import util

b = browser = mechanize.Browser()

ORGANISATION_DETAIL_URL = "http://gow.epsrc.ac.uk/NGBOViewOrganisation.aspx?OrganisationId=%s"


def scrape_organisation(id):
    b.open(ORGANISATION_DETAIL_URL % id)
    return scrape_organisation_html(id, b.response().read())


def scrape_organisation_html(id, html):

    organisation = {'id': id}

    page = PyQuery(html)

    _scrape_name(organisation, page)
    _scrape_departments(organisation, page)

    return organisation


def _scrape_name(o, el):
    o['name'] = ''

    pfx = 'Current EPSRC Support By department in '
    name_el = el.find('#lblHeader').eq(0)

    if name_el:
        n = name_el.html().strip()
        if n.startswith(pfx):
            o['name'] = n[len(pfx):]


def _scrape_departments(o, el):
    o['departments'] = ds = []
    for e in (PyQuery(x) for x in el.find('table#dgDetails tr td a')):
        if e.attr.href.startswith('NGBOViewDepartment.aspx?DepartmentId='):
            ds.append({
                'id': util.extract_id(e.attr.href, 'Department'),
                'name': e.text()
            })
