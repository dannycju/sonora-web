import requests
import json

from django.conf import settings

def stack_exchange_api(api, params_dict):
    params = '&'.join('{}={}'.format(attr, val) for attr, val in params_dict.items())
    try:
        settings.STACKEXCHANGE_API_KEY
    except NameError:
        key = ''
    else:
        key = 'key={}&'.format(settings.STACKEXCHANGE_API_KEY)
    url = 'https://api.stackexchange.com/2.2/{}?{}{}'.format(api, key, params)
    resp = requests.get(url)
    if resp.status_code != 200:
        return False
    return resp


# params_dict = {
#     "site": "stackoverflow",
#     "intitle": "data mining",
#     "pagesize": 1,
#     "sort": "relevance",
# }

# resp = stack_exchange_api('search', params_dict)
# if resp:
#     print(json.dumps(resp.json(), indent=2))

