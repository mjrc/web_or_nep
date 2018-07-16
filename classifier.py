import pickle
from nltk.classify import ClassifierI
from sklearn.feature_extraction import DictVectorizer
from statistics import mode
from featureset import build_featureset


class VoteClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    def classify(self, features):
        votes = []

        for classifier in self._classifiers:
            vote = classifier.predict(X)
            votes.append(str(vote))
        str_votes = ""
        for v in votes:
            str_votes += v[0]

        return mode(votes), str_votes

    def classify_confidence(self, features): 

        v = DictVectorizer(sparse=False)
        X = v.fit_transform(features)

        votes = []
        str_votes = ""
        for classifier in self._classifiers:
            vote = classifier.predict(X)
            votes.append(str(vote[0]))
            str_votes += str(vote[0])

        choice_votes = votes.count(mode(votes))
        endvote = mode(votes)
        conf = choice_votes / len(votes)
        
        return endvote, conf, str_votes


open_file = open("pickles/classifier-gnb.pickle", "rb")
GaussianNB_classifier = pickle.load(open_file)
open_file.close() 

open_file = open("pickles/classifier-bnb.pickle", "rb")
BernoulliNB_classifier = pickle.load(open_file)
open_file.close() 

open_file = open("pickles/classifier-lr.pickle", "rb")
LogisticRegression_classifier = pickle.load(open_file)
open_file.close()

open_file = open("pickles/classifier-sgd.pickle", "rb")
SGDClassifier_classifier = pickle.load(open_file)
open_file.close()

open_file = open("pickles/classifier-svc.pickle", "rb")
SVC_classifier = pickle.load(open_file)
open_file.close()

open_file = open("pickles/classifier-lsvc.pickle", "rb")
LinearSVC_classifier = pickle.load(open_file)
open_file.close()

open_file = open("pickles/classifier-nusvc.pickle", "rb")
NuSVC_classifier = pickle.load(open_file)
open_file.close()


votes_classifier = VoteClassifier(  
                                    GaussianNB_classifier, 
                                    BernoulliNB_classifier, 
                                    LogisticRegression_classifier,
                                    SGDClassifier_classifier,
                                    SVC_classifier,
                                    LinearSVC_classifier,
                                    NuSVC_classifier)


def web_or_nep(domain, pagesrc, sonar, wiki):

    sample_domain = build_featureset(domain, sonar, wiki, html=pagesrc, context="classifier")
    features = sample_domain.get_featureset_category_tuple()
    res = votes_classifier.classify_confidence(features)

    return res[0], res[1], res[2]

