# -*- encoding: utf-8 -*-

import urlparse
from bs4 import BeautifulSoup
import requests



def is_absolute(a):
    return bool(urlparse.urlparse(a).netloc)


outputLinks = []
invalid_links = 0
# url = raw_input("Enter a website to extract the URL's from: ")
url = 'www.google.com'

# r = ""
#
# try:
#     r = requests.get("http://" + url)
# except requests.exceptions.ConnectionError:
#     invalid_links += 1
#
# if r.status_code != 200:
#     invalid_links += 1

r = requests.get("http://" + url)

data = r.text

soup = BeautifulSoup(data, "lxml")

for link in soup.find_all(['a', 'img', 'li', 'h1', 'h2', 'h3', 'h4']):
        obtained_link = link.get('href')

    #if not str(obtained_link).startswith('mailto'):

        http_url = ''

        if 'mailto' not in obtained_link:
            if obtained_link is not None:
                if not obtained_link.find('calendar') != -1:
                    if not is_absolute(obtained_link):
                        http_ = "http"
                        if http_ in url:
                            print "ayeeeeeeee"
                            http_url = url
                        else:
                            http_url = http_ + url
                obtained_link = urlparse.urljoin(http_url, obtained_link)
                print obtained_link
                outputLinks.append(obtained_link)

outputLinks = [validItem for validItem in outputLinks if validItem != '#']

print(len(outputLinks))
# # print(outputLinks)
for item in outputLinks:
    print(item)


print "Invalid links: " + str(invalid_links)

