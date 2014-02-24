#!/usr/bin/env python


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


def page_companies(app, selectors, params, start=0):
    print('page_companies start={}'.format(start))
    sparams = params.copy()
    sparams['start'] = start
    result = app.search_company(
            selectors=selectors,
            params=sparams,
            )
    result = result['companies']

    values = result['values']
    for v in values:
        yield v
    time.sleep(1)

    if result['_total'] > start + len(values):
        for v in page_companies(app, selectors, params, start=start+len(values)):
            yield v


def page_search(app, selectors, params, start=0):
    print('page_search start={}'.format(start))
    sparams = params.copy()
    sparams['start'] = start
    result = app.search_profile(selectors=selectors, params=sparams)
    result = result['people']

    values = result['values']
    for v in values:
        yield v
    time.sleep(1)

    if result['_total'] > start + len(values):
        for v in page_search(app, selectors, params, start=start+len(values)):
            yield v


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
            pprint(user)

        print()

if __name__ == '__main__':
    main()

