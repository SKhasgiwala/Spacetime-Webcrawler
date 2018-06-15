# -*- encoding: utf-8 -*-
import csv
import logging
from datamodel.search.AusawantTgkulkarSkhasgiw_datamodel import AusawantTgkulkarSkhasgiwLink, \
    OneAusawantTgkulkarSkhasgiwUnProcessedLink, add_server_copy, get_downloaded_content
from datamodel.search.AusawantTgkulkarSkhasgiw_datamodel import AusawantTgkulkarSkhasgiwProjectionLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter, ServerTriggers
from lxml import html, etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

from bs4 import BeautifulSoup
import requests
import urlparse

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
invalid_links = 0
crawl_limit = 3000
local_count = 0

# Create files for analytics if they don't exist
try:
    f = open("max_outlinks.txt", "r")
    line = f.read()
    a, page_with_max_outlinks, max_out_links = line.split("-")
    f.close()
except IOError:
    max_out_links = 0
    page_with_max_outlinks = "http://www.ics.uci.edu/"
except ValueError:
    max_out_links = 0
    page_with_max_outlinks = "http://www.ics.uci.edu/"

try:
    invalid_file = open("invalid.txt", "r")
    invalid_links = invalid_file.read()
except IOError:
    invalid_file = open("invalid.txt", "w")
invalid_file.close()

try:
    with open('subdomain.csv', mode='r') as infile:
        reader = csv.reader(infile)
        subdomain_log = {rows[0]: rows[1] for rows in reader}
except IOError:
    open('subdomain.csv', mode='w')


@Producer(AusawantTgkulkarSkhasgiwLink)
@Getter(AusawantTgkulkarSkhasgiwProjectionLink)
@GetterSetter(OneAusawantTgkulkarSkhasgiwUnProcessedLink)
@ServerTriggers(add_server_copy, get_downloaded_content)
class CrawlerFrame(IApplication):

    def __init__(self, frame):
        self.starttime = time()
        self.app_id = "AusawantTgkulkarSkhasgiw"
        self.frame = frame

    def initialize(self):
        self.count = 0
        l = AusawantTgkulkarSkhasgiwLink("http://www.ics.uci.edu/")
        print l.full_url
        self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get(OneAusawantTgkulkarSkhasgiwUnProcessedLink)
        if unprocessed_links:
            link = unprocessed_links[0]
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    global local_count
                    global crawl_limit
                    ls = self.frame.get(AusawantTgkulkarSkhasgiwProjectionLink)
                    local_count = len(ls)
                    print('Count: ' + str(local_count))
                    if local_count < crawl_limit:
                        self.frame.add(AusawantTgkulkarSkhasgiwLink(l))
                    else:
                        self.shutdown()

    def shutdown(self):
        global local_count
        global crawl_limit
        file = open('count.csv', 'w')
        file.write(str(local_count))
        file.close()
        print('Final Count: ' + str(local_count))
        if local_count >= crawl_limit:
            print('Crawling Limit Reached')
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")


# For detecting whether the url is relative or absolute
def is_absolute(a):
    return bool(urlparse.urlparse(a).netloc)


# Counting subdomains and writing them to a file
def count_subdomain(l):
    d = dict()
    for a in l:
        url = urlparse.urlparse(a)
        subdomain = url.hostname.split('.')[0]
        if "www" in subdomain:
            subdomain = url.hostname.split('.')[1]
        if subdomain in subdomain_log:
            curr_val = int(subdomain_log[subdomain]) + 1
            subdomain_log[subdomain] = str(curr_val)
        else:
            subdomain_log[subdomain] = "1"

    with open('subdomain.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in subdomain_log.items():
            writer.writerow([key, value])


def extract_next_links(rawDataObj):
    outputLinks = []
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    
    Suggested library: lxml
    '''

    url = rawDataObj.url

    r = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, "lxml")

    for link in soup.find_all('a'):
        obtained_link = link.get('href')

        if (obtained_link is not None) and is_ascii(obtained_link):  # Check for invalid characters and None type
            if ('mailto' not in str(obtained_link)) and (
                    "calendar" not in obtained_link):  # Check for presence of mailto links and calendar (for crawler trap)
                http_url = get_absolute(url, obtained_link)
                obtained_link = urlparse.urljoin(http_url, obtained_link)
                if '?' in obtained_link:  # Identifying links with query parameters
                    position = obtained_link.rfind('?')
                    obtained_link = obtained_link[:position]
                outputLinks.append(obtained_link)
            count_subdomain(outputLinks)

    links_count = len(outputLinks)
    check_max_outlinks(links_count, url)
    return outputLinks


# Detecting which page has maximum outputlinks and writing to file
def check_max_outlinks(links_count, url):
    global max_out_links
    global page_with_max_outlinks
    if url == page_with_max_outlinks:
        max_out_links += links_count

    if links_count > max_out_links:
        max_out_links = links_count
        page_with_max_outlinks = url
        max_links_file = open("max_outlinks.txt", "w")
        max_links_file.write("Page with current high outlinks is- " + page_with_max_outlinks + " - " + str(
            max_out_links))
        max_links_file.close()


# Detecting invalid characters
def is_ascii(word):
    return all(ord(c) < 128 for c in word)


# Derive absolute link from relative url
def get_absolute(http_url, obtained_link):
    if not is_absolute(obtained_link):
        http_ = "http"
        if http_ not in http_url:
            http_url = http_ + "://" + http_url
    return http_url


def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    global invalid_links
    if invalid_links == "":
        invalid_links = 0
    parsed = urlparse.urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        invalid_links += 1
        write_invalid_file = open("invalid.txt", "w")
        write_invalid_file.write(str(invalid_links))
        return False

    try:
        r = requests.get(url)
        if r.status_code != 200:
            invalid_links += 1
            write_invalid_file = open("invalid.txt", "w")
            write_invalid_file.write(str(invalid_links))
            return False

        lower_ = ".ics.uci.edu" in parsed.hostname and not re.match(
            ".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" + "|thmx|mso|arff|rtf|jar|csv" + "|rm|smil|wmv|swf|wma|zip|rar|gz)$",
            parsed.path.lower())

        if not lower_:
            invalid_links += 1
            write_invalid_file = open("invalid.txt", "w")
            write_invalid_file.write(str(invalid_links))
        return lower_

    except TypeError:
        print ("TypeError for ", parsed)
        return False

    except requests.exceptions.ConnectionError:
        invalid_links += 1
        write_invalid_file = open("invalid.txt", "w")
        write_invalid_file.write(str(invalid_links))
        return False
