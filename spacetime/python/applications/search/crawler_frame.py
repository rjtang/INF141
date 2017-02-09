import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Producer, GetterSetter, Getter
#from lxml import html,etree
import re, os
from time import time
from collections import Counter
from BeautifulSoup import BeautifulSoup

try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs


logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
url_count = (set() 
    if not os.path.exists("successful_urls.txt") else 
    set([line.strip() for line in open("successful_urls.txt").readlines() if line.strip() != ""]))
MAX_LINKS_TO_DOWNLOAD = 3000

@Producer(ProducedLink)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):

    def __init__(self, frame):
        self.starttime = time()
        # Set app_id <student_id1>_<student_id2>...
        self.app_id = "87082176"
        # Set user agent string to IR W17 UnderGrad <student_id1>, <student_id2> ...
        # If Graduate studetn, change the UnderGrad part to Grad.
        self.UserAgentString = "IR W17 Undergrad 87082176"
		
        self.frame = frame
        assert(self.UserAgentString != None)
        assert(self.app_id != "")
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def initialize(self):
        self.count = 0
        l = ProducedLink("http://www.ics.uci.edu", self.UserAgentString)
        print l.full_url
        self.frame.add(l)

    def update(self):
        for g in self.frame.get(OneUnProcessedGroup):
            print "Got a Group"
            outputLinks, urlResps = process_url_group(g, self.UserAgentString)
            for urlResp in urlResps:
                if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
                    urlResp.dataframe_obj.bad_url += [self.UserAgentString]
            for l in outputLinks:
                if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                    lObj = ProducedLink(l, self.UserAgentString)
                    self.frame.add(lObj)
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
        print "downloaded ", url_count, " in ", time() - self.starttime, " seconds."
        try:
            os.remove("analytics.txt")
        except:
            pass
        with open("analytics.txt", "a+") as analytics:
            try:
                subdomains = open("valid_domains.txt")
                count = Counter(subdomains)

                analytics.write("Most Popular Subdomains:\n")
                analytics.write("--------------------------------------------------\n")
                analytics.write('\n\n'.join('{}{}'.format(key, value) for key, value in count.most_common()))
                analytics.write("\n")
                analytics.write("\n")

                analytics.write("Number of Invalid Links:\n")
                analytics.write("--------------------------------------------------\n")
                invalid = open("invalid_domains.txt").readlines()
                analytics.write(str(len(invalid)) + "\n")
                analytics.write("\n")
                analytics.write("\n")

                analytics.write("Most Out Links:\n")
                analytics.write("--------------------------------------------------\n")
                outs = open("output_links.txt").readlines()
                outs_count = Counter (outs)
                analytics.write('\n'.join('%s %s' % x for x in outs_count.most_common(1)))
                analytics.write("\n")
                analytics.write("\n")

                analytics.write("Average Download Time:\n")
                analytics.write("--------------------------------------------------\n")
                analytics.write(str((time() - self.starttime )/len(url_count)) + " - seconds/download \n")

            except:
                pass
        pass

def save_count(urls):
    global url_count
    urls = set(urls).difference(url_count)
    url_count.update(urls)
    if len(urls):
        with open("successful_urls.txt", "a") as surls:
            surls.write(("\n".join(urls) + "\n").encode("utf-8"))

def process_url_group(group, useragentstr):
    rawDatas, successfull_urls = group.download(useragentstr, is_valid)
    save_count(successfull_urls)
    return extract_next_links(rawDatas), rawDatas
    
#######################################################################################
'''
STUB FUNCTIONS TO BE FILLED OUT BY THE STUDENT.
'''
def extract_next_links(rawDatas):
    outputLinks = list()
    '''
    rawDatas is a list of objs -> [raw_content_obj1, raw_content_obj2, ....]
    Each obj is of type UrlResponse  declared at L28-42 datamodel/search/datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.

    Suggested library: lxml
    '''
    for obj in rawDatas:
        soup = BeautifulSoup(obj.content)
        soup.prettify()
        for link in soup.findAll('a'):
            try:
                relativeLink = link['href']
                parsedLink = urlparse(relativeLink)
                if parsedLink.scheme == "" and parsedLink.netloc == "" and parsedLink.path <= "":
                    pass
                elif parsedLink.path >= "" and parsedLink.netloc <= "":
                    host = urlparse(obj.url).netloc
                    outputLinks.append((host + relativeLink))
                else:
                    outputLinks.append(relativeLink)
            except:
                pass
    with open("output_links.txt", "a+") as outputs:
        for link in outputLinks:
            outputs.write((link + "\n").encode('utf-8'))
    return outputLinks

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be downloaded or not.
    Robot rules and duplication rules are checked separately.

    This is a great place to filter out crawler traps.
    '''
    with open("valid_domains.txt", "a+") as validDomains:
        with open("invalid_domains.txt", "a+") as invalidDomains:
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]\
                or "ganglia" in parsed.netloc\
                or "calendar" in parsed.netloc\
                or "/" in parsed.query \
                or ".php/" in parsed.path\
                or parsed.netloc.count(".") > 3\
                or ".." in url\
                or "./" in url\
                or parsed.netloc.endswith(".")\
                or parsed.netloc.endswith("http:")\
                or url <= ""\
                or parsed.path.count("/") > 25:
                    invalidDomains.write(parsed.netloc + "\n")
                    return False
            try:
                if ".ics.uci.edu" in parsed.hostname \
                    and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                    + "|thmx|mso|arff|rtf|jar|csv"\
                    + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
                        validDomains.write(parsed.netloc + "\n")
                        return True
            except TypeError:
                print ("TypeError for ", parsed)
