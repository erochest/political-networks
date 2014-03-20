#!/usr/bin/env python


## TODO:
# - populate the education table
# - set up recruiter as admin on application and generate keys for him

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


def title(msg):
    print(msg)
    print('=' * len(msg))


def insert_term(c, term):
    """Inserts the term into the database and returns the ID. """
    c.execute(
        'INSERT OR IGNORE INTO search_term (term) VALUES (?);',
        (term,)
        )
    c.execute('SELECT id FROM search_term WHERE term=?;', (term,))
    search_id = c.fetchone()[0]
    return search_id


def get_profile_id(c, profile):
    """Return the profile's person.id value from the DB."""
    c.execute('SELECT id FROM person WHERE linkedin_id=?;', (profile['id'],))
    rows = c.fetchall()

    if not rows:
        return None
    else:
        return rows[0][0]


def link_search(c, search_id, person_id):
    c.execute('''
        INSERT OR IGNORE INTO search_term_person
            (search_term_id, person_id)
            VALUES (?, ?);
            ''',
        (search_id, person_id),
        )

def insert_profile(c, search_id, user_profile):
    """Inserts the user profile into the person table and returns the ID."""
    c.execute('''
        INSERT OR IGNORE INTO person
            (linkedin_id, first_name, last_name)
            VALUES (?, ?, ?);
            ''',
        (user_profile['id'], user_profile['firstName'], user_profile['lastName']),
        )
    c.execute(
        'SELECT id FROM person WHERE linkedin_id=?;',
        (user_profile['id'],),
        )
    person_id = c.fetchone()[0]

    link_search(c, search_id, person_id)

    return person_id


def linkedin_date(date):
    if date is None:
        return None

    return '{0[year]:04}-{0[month]:02}-01'.format(date)


def insert_position(c, person_id, position):
    """Inserts one position for a person into the DB and returns the ID."""
    company = position['company']
    c.execute('''
        INSERT INTO position
            (linkedin_id, person_id, is_current, industry, company_name,
             title, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            ''',
        (
            position['id'], person_id, position['isCurrent'],
            company['industry'], company['name'],
            position['title'],
            linkedin_date(position['startDate']),
            linkedin_date(position.get('endDate')),
        ))
    c.execute('SELECT id FROM position WHERE linkedin_id=?;',
              (position['id'],))
    position_id = c.fetchone()[0]
    return position_id


def search_profiles(application, selectors, params):
    users = page_search(application, selectors, params)
    for user in users:
        try:
            profile = application.get_profile(user['id'], selectors=PROFILE_SELECTORS)
        except Exception, ex:
            print('ERROR retrieving profile')
            pprint(user)
            print()
            raise ex
        yield profile


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
                search_id = insert_term(c, term)
                title('{} => {}'.format(term, search_id))

                profiles = search_profiles(application, None, {
                    'company-name': term,
                    })
                n = 0
                for profile in profiles:
                    person_id = get_profile_id(c, profile)
                    if person_id is not None:
                        link_search(c, search_id, person_id)
                        continue

                    person_id = insert_profile(c, search_id, profile)
                    profile['dbid'] = person_id
                    print(
                        '{0[firstName]} {0[lastName]} => {0[dbid]}'.format(
                            profile),
                        )

                    for position in profile['positions'].get('values', []):
                        insert_position(c, person_id, position)

                    n += 1
                    if n >= 10:
                        break

            cxn.commit()


if __name__ == '__main__':
    main()

