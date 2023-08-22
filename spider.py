import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def readurl(url, referer=None):
    if referer:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Referer': referer,
        }
        response = requests.get(url, headers=headers, verify=False)
    else:
        response = requests.get(url, verify=False)

    return response.text
