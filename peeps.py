#!/usr/bin/env python


## TODO:
# - set up database
# - put data into database

from __future__ import absolute_import, division, print_function, unicode_literals

import json
from linkedin import linkedin
import time
from pprint import pprint

from keys import *


RETURN_URL   = 'http://localhost:8000'

# Organizing for Action
OBAMA_ORGS = {
        'organizing-for-action',
        'obama-for-america',
        # 'OFA-Organizing-America-2500151',
        }
FREETEXT_SEARCHES = {
        'Obama for America',
        'Organizing for Action',
        'Organizing for America',
        }

POLITICAL_ORGANIZATION = 107

CO_SELECTORS=['companies:(id,name,universal-name,website-url,company-type,industries,locations)']
CO_PARAMS={
    'facet': [
        'industry,{}'.format(POLITICAL_ORGANIZATION),
        'location,us',
        ],
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


def main():
    authentication = linkedin.LinkedInDeveloperAuthentication(
            API_KEY, API_SECRET,
            USER_TOKEN, USER_SECRET,
            RETURN_URL, linkedin.PERMISSIONS.enums.values()
            )
    application = linkedin.LinkedInApplication(authentication)

    for name in FREETEXT_SEARCHES:
        print(name)
        print('=' * len(name))
        users = page_search(application, None, {
            'company-name': name,
            })
        for user in users:
            pprint(application.get_profile(user['id'], selectors=PROFILE_SELECTORS))

        print()

if __name__ == '__main__':
    main()

