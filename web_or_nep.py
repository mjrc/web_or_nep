import gensim.models.keyedvectors
import os, sys, configparser
from featureset import build_featureset

from domain import Domain
from classifier import votes_classifier
from utils import store_domain_features
import os

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')

SONAR_DIR = config['analyzer']['SONAR_DIR']
WIKI_DIR = config['analyzer']['WIKI_DIR']

ROOT = config['analyzer']['ROOT_CLASSIFY']

sonar = gensim.models.KeyedVectors.load(SONAR_DIR)
wiki = gensim.models.KeyedVectors.load(WIKI_DIR)

domain_list = []

directories = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d))]

for directory in directories:
    domain = Domain(directory, cat="", directory=str(ROOT + '/' + directory))
    domain_list.append(domain)


i = 0
for domain in domain_list:
    i += 1
    if (i % 1000) == 0:
        store_domain_features(domain_list, kind="classifier", cat="")

    sample_domain = build_featureset(domain, sonar, wiki, context="classifier")
    features = sample_domain.get_featureset_category_tuple()
    res = votes_classifier.classify_confidence(features)

    print("{0:5} {1:8} {2:>10,.2} {3:40} {4:.40}".format(res[0], res[2], res[1], 'http://' + domain.domain_name, domain.title))











