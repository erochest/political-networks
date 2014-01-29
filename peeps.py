#!/usr/bin/env python


from linkedin import linkedin
from pprint import pprint

from keys import *


RETURN_URL   = 'http://localhost:8000'

# Organizing for Action
COMPANY_NAME = 'organizing-for-action'

authentication = linkedin.LinkedInDeveloperAuthentication(
        API_KEY, API_SECRET,
        USER_TOKEN, USER_SECRET,
        RETURN_URL, linkedin.PERMISSIONS.enums.values()
        )

# Pass it in to the app...

application = linkedin.LinkedInApplication(authentication)

# Use the app....

companies = application.get_companies(universal_names=[COMPANY_NAME])
pprint(companies)
for co_info in companies['values']:
    updates = application.get_company_updates(co_info['id'], params={'count': 2})
    pprint(updates)

# updates = application.get_company_updates(COMPANY_ID, params={'count': 2})
# pprint(updates)


