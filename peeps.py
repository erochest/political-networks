#!/usr/bin/env python


import json
from linkedin import linkedin
import time
from pprint import pprint

from keys import *


RETURN_URL   = 'http://localhost:8000'

# Organizing for Action
COMPANY_NAME = 'organizing-for-action'
POLITICAL_ORGANIZATION = 107

SELECTORS=['companies:(id,name,universal-name,website-url,company-type,industries,locations)']
PARAMS={
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


def main():
    authentication = linkedin.LinkedInDeveloperAuthentication(
            API_KEY, API_SECRET,
            USER_TOKEN, USER_SECRET,
            RETURN_URL, linkedin.PERMISSIONS.enums.values()
            )
    application = linkedin.LinkedInApplication(authentication)

    with open('industry-pol.json', 'wb') as f:
        json.dump(list(page_companies(application, SELECTORS, PARAMS, start=0)), f)


if __name__ == '__main__':
    main()

