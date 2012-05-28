from __future__ import print_function

import datetime
import glob
from itertools import repeat
import json
import os
import re
import sys

from epsrc.grant import scrape_grant_html
from epsrc.organisation import scrape_organisation_html
from epsrc.department import scrape_department_html

PATHS = {
    'grant': 'NGBOViewGrant.aspx?GrantRef=*',
    'department': 'NGBOViewDepartment.aspx?DepartmentId=*',
    'organisation': 'NGBOViewOrganisation.aspx?OrganisationId=*'
}

def timestamp():
    return str(datetime.datetime.utcnow())

def batch(iterable, size=100):
    iterable = iter(iterable)
    while True:
        res = []
        try:
            for _ in xrange(size):
                res.append(iterable.next())
            yield res
        except StopIteration:
            if res:
                yield res
            raise StopIteration()

class ScrapeError(Exception):
    pass


class Scraper(object):

    def __init__(self, conn, root_dir):
        self.conn = conn
        self.root_dir = root_dir

    def scrape(self):
        self.scrape_organisations()
        self.scrape_departments()
        self.scrape_grants()

    def scrape_organisations(self):
        self._scrape('organisation')

    def scrape_departments(self):
        self._scrape('department')

    def scrape_grants(self):
        self._scrape('grant')

    def _scrape(self, typ):
        print("Scraping %ss" % typ, file=sys.stderr)
        paths = os.path.join(self.root_dir, PATHS[typ])
        files = glob.iglob(paths)

        for b in batch(files):
            self._scrape_batch(typ, b)

    def _scrape_batch(self, typ, files):
        for f in files:
            id = f.split('=')[-1].replace('%2F', '/')
            print("  %s" % id, file=sys.stderr)
            org = globals()['scrape_%s_html' % typ](id, open(f).read())
            getattr(self, '_process_%s' % typ)(org)

        self.conn.commit()
        print("  COMMITTED BATCH", file=sys.stderr)

    def _process_organisation(self, organisation):
        depts = organisation.pop('departments', [])
        self.update_or_create_organisation(organisation)

        for d in depts:
            d['organisation_id'] = organisation['id']
            self.update_or_create_department(d)

    def _process_department(self, dept):
        org = dept.pop('organisation')
        org['id'] = self._get_organisation_id_by_name(org['name'])
        self.update_or_create_organisation(org)
        dept['organisation_id'] = org['id']
        self.update_or_create_department(dept)

    def _process_grant(self, grant):
        curs = self.conn.cursor()

        # Create skeleton grant to satisfy FK constraints
        self.update_or_create_grant({'id': grant['id']})

        # First, update PI. We have the id from the scrape.
        try:
            grant['principal_investigator_id'] = grant['pi']['id']
            self.update_or_create_person(grant.pop('pi'))
        except KeyError:
            f = open('error_grants.txt', 'a')
            print(grant['id'], file=f)
            print("ERROR GRANT %s" % grant['id'], file=sys.stderr)
            f.close()
            return

        # Second, department and organisation. We need to retrieve ids from
        # the database.

        org = grant.pop('organisation')
        dept = grant.pop('department')

        org['id'] = self._get_organisation_id_by_name(org['name'])
        if org['id'] is None:
            # We don't already have a reference to this organisation anywhere, so make up an id
            # that's far outside the range used by EPSRC, and set the local_id flag
            org['id'] = curs.execute('select max(max(id), 1<<16)+1 from organisations').fetchone()[0]
            org['local_id'] = True
            self._create_object('organisations', **dept)

        self.update_or_create_organisation(org)

        dept['id'] = self._get_department_id_by_name(dept['name'], org)
        if dept['id'] is None:
            # We don't already have a reference to this department anywhere, so make up an id
            # that's far outside the range used by EPSRC, and set the local_id flag
            dept['id'] = curs.execute('select max(max(id), 1<<16)+1 from departments').fetchone()[0]
            dept['organisation_id'] = org['id']
            dept['local_id'] = True
            self._create_object('departments', **dept)

        self.update_or_create_department(dept)

        grant['department_id'] = dept['id']

        # Project partners

        for o in grant.pop('project_partners'):
            self.update_or_create_organisation(o)

            sql = '''insert or ignore into grants_project_partners
                     (grant_id, organisation_id, created_at, modified_at)
                     values (?, ?, ?, ?)'''

            t = timestamp()
            curs.execute(sql, (grant['id'], o['id'], t, t))

        # Sectors

        for s in grant.pop('sectors'):
            s_id = self.update_or_create_sector(s)

            sql = '''insert or ignore into grants_sectors
                     (grant_id, sector_id, created_at, modified_at)
                     values (?, ?, ?, ?)'''

            t = timestamp()
            curs.execute(sql, (grant['id'], s_id, t, t))

        # Research topics

        for rt in grant.pop('research_topics'):
            parent = -1

            for t in rt:
                t_id = self.update_or_create_research_topic(t, parent)

                sql = '''insert or ignore into grants_research_topics
                         (grant_id, research_topic_id, created_at, modified_at)
                         values (?, ?, ?, ?)'''

                ts = timestamp()
                curs.execute(sql, (grant['id'], t_id, ts, ts))

                parent = t_id

        # Co-investigators and Other investigators

        sql = '''insert or ignore into grants_investigators
                 (grant_id, person_id, type, created_at, modified_at)
                 values (?, ?, ?, ?, ?)'''

        t = timestamp()

        for p in grant.pop('other_investigators'):
            self.update_or_create_person(p)
            curs.execute(sql, (grant['id'], p['id'], 'other', t, t))

        for p in grant.pop('co_investigators'):
            self.update_or_create_person(p)
            curs.execute(sql, (grant['id'], p['id'], 'co', t, t))

        # Related grants

        for rg_id in grant.pop('related_grants'):
            sql = '''insert or ignore into grants_related_grants
                     (grant_id, related_grant_id, created_at, modified_at)
                     values (?, ?, ?, ?)'''

            t = timestamp()
            curs.execute(sql, (grant['id'], rg_id, t, t))

        # Finally, process grant itself

        grant['panel_history'] = json.dumps(grant['panel_history'])

        self.update_or_create_grant(grant)

    def update_or_create_grant(self, grant):
        self._update_or_create_object('grants', **grant)

    def update_or_create_person(self, person):
        self._update_or_create_object('people', **person)

    def update_or_create_organisation(self, organisation):
        self._update_or_create_object('organisations', **organisation)

    def update_or_create_department(self, department):
        self._update_or_create_object('departments', **department)

    def update_or_create_sector(self, sector):
        sql = '''insert or ignore into sectors
                 (name, created_at, modified_at)
                 values (?, ?, ?)'''

        t = timestamp()
        self.conn.execute(sql, (sector, t, t))

        sql = 'select id from sectors where name=?'
        (s_id,) = self.conn.execute(sql, (sector,)).fetchone()
        return s_id

    def update_or_create_research_topic(self, name, parent_id):
        sql = '''insert or ignore into research_topics
                 (name, parent_id, created_at, modified_at)
                 values (?, ?, ?, ?)'''

        t = timestamp()
        self.conn.execute(sql, (name, parent_id, t, t))

        sql = 'select id from research_topics where name=? and parent_id=?'
        (rt_id,) = self.conn.execute(sql, (name, parent_id)).fetchone()

        return rt_id

    def _update_or_create_object(self, table, **kwargs):
        sql = 'select count(*) from %s where id=?'
        params = (kwargs['id'],)
        res = self.conn.execute(sql % table, params).fetchone()

        if res[0] == 0:
            self._create_object(table, **kwargs)
        else:
            self._update_object(table, **kwargs)

    def _create_object(self, table, **kwargs):
        col_clause = ', '.join(kwargs.keys())
        val_clause = ', '.join(repeat('?', len(kwargs)))

        t = timestamp()

        params = kwargs.values()
        params.append(t)
        params.append(t)

        sql = 'insert into %s (%s, created_at, modified_at) values (%s, ?, ?)'
        self.conn.execute(sql % (table, col_clause, val_clause), params)

    def _update_object(self, table, **kwargs):
        uid = kwargs['id']
        del kwargs['id']

        if not kwargs.keys():
            return

        set_clause = ', '.join(map(lambda x: x + '=?', kwargs.keys()))

        params = kwargs.values()
        params.append(timestamp())
        params.append(uid)

        sql = 'update %s set %s, modified_at=? where id=?'
        self.conn.execute(sql % (table, set_clause), params)

    def _get_organisation_id_by_name(self, name):
        curs = self.conn.cursor()

        sql = '''select o.id from organisations as o where o.name = ?'''
        curs.execute(sql, (name,))

        id_ = curs.fetchone()

        if id_ is None:
            return None
        else:
            return id_[0]

    def _get_department_id_by_name(self, name, org):
        curs = self.conn.cursor()

        sql = '''select d.id from departments as d where d.name = ? and d.organisation_id = ?'''
        curs.execute(sql, (name, org['id']))

        id_ = curs.fetchone()

        if id_ is None:
            return None
        else:
            return id_[0]
