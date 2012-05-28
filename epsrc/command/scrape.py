import sys
import argparse
import sqlite3

from epsrc.scraper import Scraper

SCHEMA_VERSION = 4

parser = argparse.ArgumentParser(description='Scrape EPSRC Grants on the Web data.')
parser.add_argument('database', type=str,
                    help='The database to fill or update with scraped data.')
parser.add_argument('root_dir', type=str,
                    help='The root directory of the scraped EPSRC grants-on-the-web.')
parser.add_argument('--orgs-only', action='store_true', default=False,
                    help='Only scrape organisation data.')
parser.add_argument('--depts-only', action='store_true', default=False,
                    help='Only scrape department data.')
parser.add_argument('--grants-only', action='store_true', default=False,
                    help='Only scrape grant data.')

def establish_connection(db):
    conn = sqlite3.connect(db)

    schema_version = None

    try:
        schema_version = conn.execute("select version from schema limit 1").fetchone()[0]
    except sqlite3.OperationalError, e:
        pass

    if schema_version != SCHEMA_VERSION:
        print "The database needs to be at schema version %d." % SCHEMA_VERSION
        print "Perhaps you need to run migrate.sh?"
        sys.exit(1)

    conn.execute('pragma foreign_keys=on')

    return conn

def main():
    args = parser.parse_args()
    conn = establish_connection(args.database)

    s = Scraper(conn, args.root_dir)
    if args.orgs_only:
        s.scrape_organisations()
    elif args.depts_only:
        s.scrape_departments()
    elif args.grants_only:
        s.scrape_grants()
    else:
        s.scrape()

if __name__ == '__main__':
    main()
