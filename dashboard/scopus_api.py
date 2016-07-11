import requests
import json
# import pprint

from django.conf import settings

try:
    settings.SCOPUS_API_KEY
except NameError:
    raise

def scopus_api(api, params_dict):
    params = '&'.join('{}={}'.format(attr, val) for attr, val in params_dict.items())
    url = 'http://api.elsevier.com/content/{}?{}'.format(api, params)
    headers = {'Accept':'application/json', 'X-ELS-APIKey': settings.SCOPUS_API_KEY}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(resp.status_code)
        return False
    return resp



# # Scopus Search

# params_dict = {
#     'query': 'TITLE-ABS-KEY(data mining)',
#     'field': 'identifier,doi,url,title,author,description,coverDate,coverDisplayDate,citedby-count',
#     'count': 1,
#     'sort': 'relevancy,-citedby-count',
# }

# resp = scopus_api('search/scopus', params_dict)
# if resp:
#     print(json.dumps(resp.json(), indent=2))

# results = resp.json()
# scopus_ids = [str(r['dc:identifier']) for r in results['search-results']["entry"]]

# for sid in scopus_ids:
#     print(sid)



# # Abstract Retrieval

# scopus_info_params_dict = {
#     'field': 'authors,title,publicationName,volume,issueIdentifier,prism:pageRange,coverDate,article-number,doi,citedby-count,prism:aggregationType'
# }

# resp = scopus_api('abstract/scopus_id/'+scopus_ids[1], scopus_info_params_dict)
# if resp:
#     print(json.dumps(resp.json(), indent=2))

# results = resp.json()
# scopus_info = {
#     'title': results['abstracts-retrieval-response']['coredata']['dc:title'],
#     'journal': results['abstracts-retrieval-response']['coredata']['prism:publicationName'],
#     'volume': results['abstracts-retrieval-response']['coredata']['prism:volume'],
#     'articlenum': (results['abstracts-retrieval-response']['coredata'].get('prism:pageRange') or \
#                 results['abstracts-retrieval-response']['coredata'].get('article-number')),
#     'date': results['abstracts-retrieval-response']['coredata']['prism:coverDate'],
#     'doi': 'doi:' + (results['abstracts-retrieval-response']['coredata']['prism:doi'] if 'prism:doi' in results['abstracts-retrieval-response']['coredata'] else ''),
#     'cites': int(results['abstracts-retrieval-response']['coredata']['citedby-count'])
# }
# if 'authors' in results['abstracts-retrieval-response']:
#     scopus_info['authors'] = ', '.join([au['ce:indexed-name'] for au in results['abstracts-retrieval-response']['authors']['author']])
# else:
#     scopus_info['authors'] = ''
# pprint.pprint(scopus_info)
