#!/usr/bin/env python


## TODO:
# - put data into database

from __future__ import absolute_import, division, print_function, unicode_literals

from contextlib import closing
import json
from linkedin import linkedin
import os
import time
from pprint import pprint
import sqlite3

from keys import *


RETURN_URL = 'http://localhost:8000'
DB_NAME = 'obama-orgs.sqlite3'

# Organizing for Action
FREETEXT_SEARCHES = {
        'Obama for America',            # 'obama-for-america',
        'Organizing for Action',        # 'organizing-for-action',
        'Organizing for America',       # this is a group, not organization
        }

PROFILE_SELECTORS = [
        'id,first-name,last-name,headline,positions,educations',
        ]


def page_calls(call, key, selectors, params, start=0):
    print('{} start={}'.format(key, start))
    sparams = params.copy()
    sparams['start'] = start
    result = call(selectors=selectors, params=sparams)
    result = result[key]

    values = result['values']
    for v in values:
        yield v
    time.sleep(1)

    offset = start + len(values)
    if result['_total'] > offset:
        for v in page_calls(call, key, selectors, params, start=offset):
            yield v


def page_companies(app, selectors, params):
    return page_calls(app.search_company, 'companies', selectors, params)


def page_search(app, selectors, params):
    return page_calls(app.search_profile, 'people', selectors, params)


def ego_search():
    users = page_search(application, None, {
        'first-name': 'Eric',
        'last-name': 'Rochester',
        })
    return users


def connect(filename, schema_file='schema.sql'):
    new = not os.path.exists(filename)
    cxn = sqlite3.connect(filename)
    if new:
        with open(schema_file) as f:
            sql = f.read()
        cxn.executescript(sql)
    return cxn


def main():
    authentication = linkedin.LinkedInDeveloperAuthentication(
            API_KEY, API_SECRET,
            USER_TOKEN, USER_SECRET,
            RETURN_URL, linkedin.PERMISSIONS.enums.values()
            )
    application = linkedin.LinkedInApplication(authentication)

    with closing(connect(DB_NAME)) as cxn:
        with closing(cxn.cursor()) as c:
            for term in FREETEXT_SEARCHES:
                c.execute(
                    'INSERT OR IGNORE INTO search_term (term) VALUES (?);',
                    (term,)
                    )
                c.execute('SELECT id FROM search_term WHERE term=?;', (term,))
                search_id = c.fetchone()[0]
                print('{} => {}'.format(term, search_id))
            cxn.commit()

                # print(name)
                # print('=' * len(name))
                # users = page_search(application, None, {
                    # 'company-name': name,
                    # })
                # for user in users:
                    # pprint(application.get_profile(user['id'], selectors=PROFILE_SELECTORS))

                # print()

if __name__ == '__main__':
    main()

