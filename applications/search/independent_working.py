# -*- encoding: utf-8 -*-

import urlparse
from bs4 import BeautifulSoup
import requests
from urllib2 import urlopen
from collections import deque

max_out_links = 0
page_with_max_outlinks = "http://www.ics.uci.edu"
invalid_links = 0


def is_absolute(a):
    return bool(urlparse.urlparse(a).netloc)


def extract_next_links(url):
    outputLinks = []

    data = urlopen(url)

    soup = BeautifulSoup(data, "lxml")

    for link_from_webpage in soup.find_all('a'):

        obtained_link = link_from_webpage.get('href')

        print('\n')
        print(type(obtained_link))
        print(obtained_link)

        obtained_link = str(obtained_link)

        # print(type(obtained_link))
        print('Obtained Link: ' + obtained_link)

        if obtained_link is not None:
            print('not a none type')
            if 'mailto' not in obtained_link:
                print('mailto not here')
                if 'calendar' not in obtained_link:
                    print('Not a calendar')
                    http_url = ''
                    if not is_absolute(obtained_link):
                        print('Not absolute')
                        http = "http"
                        if 'http' not in obtained_link:
                            print('http not in link!')
                            http_url = url + obtained_link
                            print('the newly formed url is::' + http_url)
                        # if http in url:
                        #     print('http found')
                        #     http_url = url
                        # else:
                        #     print('No http found')
                        #     http_url = 'http://' + url
                        # print('http_url: ' + http_url)
                        obtained_link = http_url
                        print('Converted Link: ' + obtained_link)
                    else:
                        if 'ics.uci.edu' in obtained_link:
                            print('Absolute Link: ' + obtained_link)
                            outputLinks.append(obtained_link)
                        else:
                            print('Not a UCI Webite')

            else:
                print('It is Mailto')
        else:
            print('It is None')

    links_count = len(outputLinks)
    global max_out_links
    global page_with_max_outlinks

    if links_count > max_out_links:
        max_out_links = links_count
        page_with_max_outlinks = url
        print "\nPage with current high outlinks is: " + page_with_max_outlinks + " with counts : " + str(max_out_links)

    return outputLinks


file = open('crawled_links.txt', 'r')
link = file.read()

print('link passed: '+ link)

Links = []

# outputLinks = extract_next_links(link)
Links = extract_next_links(link)
print('\n\nOutput Link: ')
print(Links)
print('\n')

for crawled_link in Links:
    count = crawled_link.count('/')
    print(crawled_link + ' : ' + str(count-2))

print('\n\nRemoving Query\n')
for url in Links:
    if '?' in url:
        k = url.rfind('?')
        url = url[:k]
        print(url)
    else:
        print(url)