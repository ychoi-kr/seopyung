import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def readurl(url):
    return requests.get(url, verify=False).text

