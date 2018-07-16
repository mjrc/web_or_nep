#!/usr/bin/env python3
import os
import re, regex 
import sys
import pprint
import logging
import configparser
from domain import Domain
from nltk.metrics import *
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.corpus import stopwords

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + './config.ini')

with open('./resources/dutch-combined.txt', 'r') as handle:
    dutch_words = set()
    for line in handle.readlines():
        dutch_words.add(line.rstrip())

with open('./resources/stopwords.txt', 'r') as handle: 
    dutch_stopwords = set()
    for line in handle.readlines():
        dutch_stopwords.add(line.rstrip())


WORDS = sorted(set([line.lower() for line in dutch_words]))
STOPWORDS = sorted(set(stopwords.words('dutch')).union(stopwords.words('english')).union(dutch_stopwords))
tokenizer = RegexpTokenizer(r'\w+')

# Compile all regexs
idealRE = re.compile(r'/ideal|i-deal|i_deal/i')
ibanRE = re.compile(r'\b[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}')
vast_or_mobiel_RE = re.compile(r'\b((((0)[1-9]{2}[0-9][-]?[1-9][0-9]{5})|((\\+31|0|0031)[1-9][0-9]   [-]?[1-9][0-9]{6}))|(((\\+31|0|0031)6){1}[1-9]{1}[0-9]{7}))')
addressRE = re.compile(r'\b([1-9][e][\s])*([a-zA-Z]+(([\.][\s])|([\s]))?)+[1-9][0-9]*(([-][1-9][0-9]*)|([\s]?[a-zA-Z]+))')
# Current analyticsRE includes: Google Analytics, Clicky, Mint, Kissmetrics, Open Web Analytics, Clicktale, CrazyEgg, Piwik, Yahoo, Optimizery, Woopra, Yandex Metrika, Clickheat, New Relic, comScore, Quantcast, SiteCatalist, Webtrends, Chartbeats and Hotjar.
analyticsRE = re.compile(r'google-analytics\.com\/(?:ga|urchin|(analytics))\.js|boba(?:\.min)?\.js|static\.getclicky\.com|mint/\?js|KM_COOKIE_DOMAIN|OWA\.config\.baseUrl|owa_baseUrl|owa_cmds|clickTaleStartEventSignal|script\.crazyegg\.com/pages/scripts/\d+/\d+\.js|monotracker(?:\.min)?\.js|adinterax\.com|optimizely\.com.*\.js|static\.woopra\.com|mc\.yandex\.ru\/metrika\/watch\.js|cdn\.jsdelivr\.net\/npm\/yandex-metrica-watch\/watch\.js|clickheat.*\.js|NREUM|newrelic|\.scorecardresearch\.com/beacon\.js|COMSCORE\.beacon|\.quantserve\.com/quant\.js|/s[_-]code.*\.js|WTOptimize|chartbeat\.js|//static\.hotjar\.com/c/hotjar-')
smRE = re.compile(r'facebook|twitter|youtube|vimeo|pinterest|linkedin')
sm_deeplink_RE = re.compile(r'(http(s)?:\/\/)?(www\.)?(facebook|twitter|youtube|vimeo|pinterest|linkedin)\.[a-z]{2,6}\/(?!share|intent/tweet|pin/create|js\/pinmarklet|FACEBOOK|TWITTER|YOUTUBE|\/|VIMEO|PINTEREST|LINKEDIN).+')
currency_RE = regex.compile(r'\p{Sc}')
amount_RE = regex.compile(r'^\p{Sc}?([0-9]{1,3},([0-9]{3},)*[0-9]{3}|[0-9]+)(.[0-9][0-9])?$')

fonts_RE = regex.compile(r'(cufon-yui\\.js)|(<link[^>]* href=[^>]+font-awesome(?:\\.min)?\\.css)|(<script[^>]* src=[^>]+fontawesome(?:\\.js)?)|(?:<link[^>]* href=[^>]+glyphicons(?:\\.min)?\\.css|<img[^>]* src=[^>]+glyphicons)|(<link[^>]* href=[^>]+fonts\\.(?:googleapis|google)\\.com)|(googleapis\\.com/.+webfont)|(<link[^>]* href=[^>]+ionicons(?:\\.min)?\\.css)|(use\\.typekit\\.com)|(sifr\\.js)') 


with open('resources/plaatsnamen.txt') as fname:
    PLAATSNAMEN = fname.read().splitlines()

with open('resources/pc6.txt') as fname:
    POSTCODES = fname.read().splitlines()


def get_label_from_domain(domain):
    return domain.split('.')[-2]

def get_html_files(directory):
    """ Returns a list of all HTML files given a directory and domain name """

    if not os.path.isdir(directory):
        sys.exit("'{0}' is no directory".format(directory))

    html_files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.html'):
                html_files.append(os.path.join(root, filename))

    return html_files



def get_index_file(directory):
    """ Returns the HTML of the index file """

    if not os.path.isdir(directory):
        sys.exit("'{0}' is no directory".format(directory))

    html_files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('index.html'):
                html_files.append(os.path.join(root, filename))

    return html_files



def get_soups_from_html_file(html_files):
    soups = []
    for fname in html_files:
        with open(fname, 'r', errors = 'ignore') as handle:
            try:
                text = handle.read()
                soup = BeautifulSoup(text, 'lxml')
                soups.append(soup)

            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                sys.exit(e)
            except ValueError as e:
                print("Could not convert data to an integer.")
                sys.exit(e)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                sys.exit(1)
    return soups



def get_soups_from_html_raw(html_files):
    soups = []
    for raw_html in html_files:
        try:
            soup = BeautifulSoup(raw_html, 'lxml')
            soups.append(soup)
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            sys.exit(e)
        except ValueError as e:
            print("Could not convert data to an integer.")
            sys.exit(e)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit(1)
    return soups



def get_text_from_soups(soups):
    texts = []
    for soup in soups:

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(' ')
        texts.append(text)
    return texts


def get_tokens_from_texts(texts):
    tokenList = []
    for text in texts:
        tokens = word_tokenize(text)
        tokenList.append(tokens)
    return tokenList


def get_sets_from_tokens(tokenList):
    tokenSet = []
    for tokens in tokenList:
        tokenSet.append(set(tokens))
    return tokenSet


def get_substrings_from_string(input_string): 
    lenght = len(input_string)
    substrings = set()
    for i in range(lenght): 
        j = i + 1
        while j <= lenght:
            substrings.add(input_string[i:j])
            j += 1
    return substrings 
            

def get_subwords_from_substrings(substrings, swv, wwv):
    subwords = set()
    for string in substrings:
        try: 
            if (string in swv) and (string in wwv):
            # TODO: make following lookup perform faster
            # if (string in WORDS) and (string in swv) and (string in wwv):
                subwords.add(string)
        except KeyError:
            pass

    return subwords


def get_words_from_subwords(wordset): 
    final_wordset = wordset.copy()

    while len(wordset) > 0:
        longest = max(wordset, key=len)
        wordset.remove(longest)
        
        for element in wordset:
            if element in longest:
                final_wordset.remove(element)

        wordset.intersection_update(final_wordset)
    return final_wordset


def remove_stopwords_from_set(input_set):
    newset = set()
    for word in input_set:
        if word not in STOPWORDS:
            newset.add(word)
    return newset 


def feature_title(index_soup):
    try:
        return index_soup.find('title').text.strip()
    except AttributeError:
        return ''


def feature_metadesc(soups):
    for soup in soups:
        for tag in soup.find_all("meta"):
            if tag.get("name") == "description":
                return str(tag)
    return False


def feature_metakeyw(soups):
    for soup in soups:
        for tag in soup.find_all("meta"):
            if tag.get("name") == "keywords":
                return str(tag)
    return False


def feature_metaog(soups):
    for soup in soups:
        for tag in soup.find_all("meta"):
            if tag.get('property') and "og" in tag.get('property'):
                return tag.get('property')
    return False

def feature_links(soups, label):
    internal_links = []
    external_links = []
    hash_links = []
    tel_links = []
    mailto_links = []
    javascript_links = []
    intend_links = []
    map_links = [] 

    for soup in soups:
        for tag in soup.find_all("a"):
            href = tag.get('href')
            if href:
                href = href.lower()
                href_split = href.split('.')

            if not href:
                pass 
            elif href == '#':                 
                hash_links.append(href)
            elif href.startswith('tel:') or href.startswith('"tel:'):
                tel_links.append(href)
            elif href.startswith('mailto:'):
                mailto_links.append(href)
            elif href.startswith('javascript:'):
                javascript_links.append(href)  
            elif href.startswith('intent://'):
                intend_links.append(href)
            elif href.startswith('map:'):
                map_links.append(href)
            elif href.startswith('http://') or href.startswith('https://'):
                if label.lower() in [x.lower() for x in href_split[0:2]]:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            else:
                internal_links.append(href)
            
    return internal_links, external_links, hash_links, tel_links, mailto_links, javascript_links, intend_links, map_links


def feature_ltsimilarity(label, title, sonar, wiki):
    swv = sonar.vocab
    wwv = wiki.vocab

    label_substrings = get_substrings_from_string(label)
    label_subwords = get_subwords_from_substrings(label_substrings, swv, wwv)
    label_words = get_words_from_subwords(label_subwords)
    label_words_clean = remove_stopwords_from_set(label_words)

    title_words = {x.lower() for x in word_tokenize(title)}
    title_words_matched = get_subwords_from_substrings(title_words, swv, wwv)
    title_words_clean = remove_stopwords_from_set(title_words_matched)


    if len(label_words_clean) == 0 or len(title_words_clean) == 0:
        return 0, 0, 0, 0

    sonar_sim = sonar.n_similarity(label_words_clean, title_words_clean)
    wiki_sim = wiki.n_similarity(label_words_clean, title_words_clean)

    sonar_dist = sonar.wmdistance(label_words_clean, title_words_clean)
    wiki_dist = wiki.wmdistance(label_words_clean, title_words_clean)

    # Uncomment this to inspect the words used for similarity and distance measurements
    # with open("features/subwords", "a") as handle:
    #     handle.write("title1:\t{}\n".format(title_words))
    #     handle.write("title2:\t{}\n".format(title_words_matched))
    #     handle.write("labe1l:\t{}\n".format(label_subwords))
    #     handle.write("label2:\t{}\n".format(label_words_clean))
    #     handle.write("simi:\t{} {}\n".format(sonar_sim, wiki_sim))
    #     handle.write("dist:\t{} {}\n\n\n".format(sonar_dist, wiki_dist))

    return sonar_sim, wiki_sim, sonar_dist, wiki_dist


def feature_lexdiv(tokenList):
    combined = []
    for token in tokenList:
        combined += token

    try:
        return len(set(combined)) / len(combined)
    except:
        return 0

def feature_ideal(texts):
    for text in texts:
        res = re.search(idealRE, text)
        if res:
            print(res.group(0))
            return res.group(0)

    return False

def feature_iban(texts):
    for text in texts:
        res = re.search(ibanRE, text)
        if res:
            return res.group(0)
    return False


def feature_currency(texts):
    symbols = []
    amount = []
    for text in texts: 
        symbols = currency_RE.findall(text)
        prices = amount_RE.findall(text)
        return symbols, prices

def feature_phone(texts):

    for text in texts:
        res = re.search(vast_or_mobiel_RE, text)
        if res:
            return res.group(0)
    return False


def feature_address(texts):

    for text in texts:
        res = re.search(addressRE, text)
        if res:
            return res
    return False


def feature_postcode(texts):
    postcodeRE = re.compile(r'\b[1-9][0-9]{3}[\s]?[A-Za-z]{2}')

    for text in texts:
        res = re.search(postcodeRE, text)
        if res and res.group(0).upper() in POSTCODES:
            return res
    return False


def feature_place(sets):
    for setitem in sets:
        for place in PLAATSNAMEN:
            if ' ' + place.lower() + ' ' in setitem:
                logging.debug(place)
                return place
    return False


def feature_belastingnum(texts):
    """ Source: https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch04s21.html """
    belastingnumRE = re.compile(r"""
        (AT)?U[0-9]{8} |                              # Austria
        (BE)?0[0-9]{9} |                              # Belgium
        (BG)?[0-9]{9,10} |                            # Bulgaria
        (CY)?[0-9]{8}L |                              # Cyprus
        (CZ)?[0-9]{8,10} |                            # Czech Republic
        (DE)?[0-9]{9} |                               # Germany
        (DK)?[0-9]{8} |                               # Denmark
        (EE)?[0-9]{9} |                               # Estonia
        (EL|GR)?[0-9]{9} |                            # Greece
        (ES)?[0-9A-Z][0-9]{7}[0-9A-Z] |               # Spain
        (FI)?[0-9]{8} |                               # Finland
        (FR)?[0-9A-Z]{2}[0-9]{9} |                    # France
        (GB)?([0-9]{9}([0-9]{3})?|[A-Z]{2}[0-9]{3}) | # United Kingdom
        (HU)?[0-9]{8} |                               # Hungary
        (IE)?[0-9]S[0-9]{5}L |                        # Ireland
        (IT)?[0-9]{11} |                              # Italy
        (LT)?([0-9]{9}|[0-9]{12}) |                   # Lithuania
        (LU)?[0-9]{8} |                               # Luxembourg
        (LV)?[0-9]{11} |                              # Latvia
        (MT)?[0-9]{8} |                               # Malta
        (NL)?[0-9]{9}B[0-9]{2} |                      # Netherlands
        (PL)?[0-9]{10} |                              # Poland
        (PT)?[0-9]{9} |                               # Portugal
        (RO)?[0-9]{2,10} |                            # Romania
        (SE)?[0-9]{12} |                              # Sweden
        (SI)?[0-9]{8} |                               # Slovenia
        (SK)?[0-9]{10}                                # Slovakia
        """)

    for text in texts:
        res = re.search(belastingnumRE, text)
        if res:
            return res
    return False


def feature_belastingstr(texts):
    for text in texts:
        if 'btw' in text.lower() or 'belasting' in text.lower():
            return text
    return False


def feature_analytics(soups):
    """Finds usage of 20 of the most used web analytics software."""
    for soup in soups:
        for script in soup.find_all('script'):
            try:
                res = re.search(analyticsRE, str(script))
            except RecursionError:
                res = None
            if res:
                return res.group(0)
    return False

def feature_fonts(soups):
    fonts = []
    for soup in soups:
        for tag in soup.find_all(['script', 'link']):
            font = fonts_RE.match(str(tag))
            if font is not None:
                fonts.append(font.group(0))
        return len(fonts), fonts
        

def feature_scripts(soups):
    """Finds the number of scripts loaded"""
    for soup in soups:
        scripts = soup.find_all('script')
        scriptscnt = len(scripts)
        return scripts, scriptscnt
    return False

def feature_styles(soups):
    """Finds the number of scripts loaded"""
    for soup in soups:
        styles = soup.find_all('style')
        stylesscnt = len(styles)
        return styles, stylesscnt
    return False


def feature_sm(soups):
    """Checks if social media is mentioned in html hyperlinks ('a' elements)"""
    sm = False
    sm_deep_link = False
    for soup in soups:
        for link in soup.find_all('a'):
            try:
                res = re.search(smRE, str(link).lower())
                if res:
                    sm = str(link)
                    sm_deep_link = feature_sm_deep_link(link, soups)
                    if sm_deep_link:
                        return sm, sm_deep_link
            except RecursionError:
                pass
    return sm, sm_deep_link

"""Check if given html hyperlink is a valid deep link to a kind of social media page of the website"""
def feature_sm_deep_link(link, soups):
    if not link.has_attr('href'):
        return False
    res = re.search(sm_deeplink_RE, link.get('href'))
    if res:
        return res.group(0)
    else:
        return False


def feature_imagescnt(soups):
    for soup in soups:
        images = soup.find_all('img')
        return len(images)
    return 0
 

def print_title(soups):
    for soup in soups:
        try:
            print(soup.find('title').text)
        except IndexError as e:
            return False

    return True


def build_featureset(domain, sonar="", wiki="", html="", context="trainer"):

    logging.debug("Analyzing domain '{0}'".format(domain.domain_name))

    if context == "trainer":
        html_files = [ domain.directory + '/index.html' ]
        index_soups = get_soups_from_html_file(html_files)
    elif context == "classifier":
        html_files = [ domain.directory + '/index.html' ]
        index_soups = get_soups_from_html_file(html_files)

        # from database so only index - push to empty list
        # html_files = [ html ]
        # index_soups = get_soups_from_html_raw(html_files)
    else: 
        raise

    index_title = feature_title(index_soups[0])
    domain.title = index_title
    domain.titlecnt = len(tokenizer.tokenize(index_title))

    domain.sm_link, domain.sm_deep_link = feature_sm(index_soups)

    logging.debug("Checking presence of Analytics...")
    domain.analytics = feature_analytics(index_soups)
    
    domain.fonts = feature_fonts(index_soups)

    scripts = feature_scripts(index_soups)
    domain.scripts = scripts[0]
    domain.scriptscnt = scripts[1]

    styles = feature_styles(index_soups)
    domain.styles = styles[0]
    domain.stylescnt = styles[1]
    
    logging.debug("Counting the amount of images...")
    domain.imagecnt = feature_imagescnt(index_soups)

    index_texts = get_text_from_soups(index_soups)
    index_tokens = get_tokens_from_texts(index_texts)
    index_set = set(index_tokens[0])

    symbols_price = feature_currency(index_texts)

    domain.currency = symbols_price[0]
    domain.currencycnt = len(domain.currency)

    domain.price = symbols_price[1]

    # Uncomment codeblock below to print domains which cause an IndexError
    # try:
    #     test = index_soups[0]
    #     test = feature_title(index_soups[0])
    # except IndexError:
    #     print('----------')
    #     print(domain.domain_name)
    #     print(index_soups)

    domain.label = get_label_from_domain(domain.domain_name)

    domain.metadesc = feature_metadesc(index_soups)

    try: 
        domain.metadesccnt = len(tokenizer.tokenize(domain.metadesc))
    except TypeError: 
        # metadesc is 'False' and no length is available
        domain.metadesccnt = 0 

    domain.metakeyw = feature_metakeyw(index_soups)

    try: 
        domain.metakeywcnt = len(tokenizer.tokenize(domain.metadesc))
    except TypeError: 
        # metakeyw is 'False' and no length is available
        domain.metakeywcnt = 0 


    domain.metaog = feature_metaog(index_soups)

    links = feature_links(index_soups, domain.label)
    domain.links_internal = links[0]
    domain.links_external = links[1]
    domain.links_hash = links[2]
    domain.links_mailto = links[3]
    domain.links_javascript_links = links[4]
    domain.links_intend = links[5]
    domain.links_map = links[6]

    domain.lexcnt = len(index_tokens[0])
    domain.lexunq = len(index_set)

    try: 
        domain.lexdiv = domain.lexcnt / domain.lexunq
    except ZeroDivisionError: 
        domain.lexdiv = 0 

    label_title_similarity = feature_ltsimilarity(domain.label, domain.title, sonar, wiki)
    domain.label_title_similarity_sonar = label_title_similarity[0]
    domain.label_title_similarity_wiki = label_title_similarity[1]
    domain.label_title_wmdistance_sonar = label_title_similarity[2]
    domain.label_title_wmdistance_wiki = label_title_similarity[3]

    domain.distance_edit = edit_distance(domain.domain_name, index_title)
    domain.distance_jaccard = jaccard_distance(set(domain.domain_name), set(index_title))
    domain.phone = feature_phone(index_texts)
    domain.place = feature_place(index_texts)
    domain.ideal = feature_iban(index_texts)
    return domain


# Run file directly to test
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read("./config.ini")
    ROOT_WEB = config['analyzer']['ROOT_WEB']
    CATEGORY = config['analyzer']['CATEGORY_WEB']

    pp = pprint.PrettyPrinter(indent=4)
    d = Domain("www.os3.nl", CATEGORY, ROOT_WEB + "www.os3.nl")
    domain = build_featureset(d)
    pp.pprint(domain.get_featureset_category_tuple(CATEGORY))
