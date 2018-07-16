import pprint, pickle, random, configparser
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os import listdir
from os.path import isdir, join
from multiprocessing.pool import ThreadPool
from sklearn import preprocessing
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import cross_validate
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from featureset import build_featureset
from domain import Domain
import gensim.models.keyedvectors
from functools import partial
from utils import store_domain_features, remove_features_directory
import warnings
import cProfile


warnings.filterwarnings("ignore", category=FutureWarning)

config = configparser.ConfigParser()
config.read("./config.ini")

CATEGORY_WEB = int(config['analyzer']['CATEGORY_WEB'])
CATEGORY_NEP = int(config['analyzer']['CATEGORY_NEP'])
ROOT_WEB = config['analyzer']['ROOT_WEB']
ROOT_NEP = config['analyzer']['ROOT_NEP']
SONAR_DIR = config['analyzer']['SONAR_DIR']
WIKI_DIR = config['analyzer']['WIKI_DIR']


DATASET = int(config['analyzer']['DATASET'])
TRAININGSET = int(config['analyzer']['TRAININGSET'])

DIRECTORIES_WEB = [d for d in listdir(ROOT_WEB) if isdir(join(ROOT_WEB, d))]
DIRECTORIES_NEP = [d for d in listdir(ROOT_NEP) if isdir(join(ROOT_NEP, d))]

plt.style.use('classic')

sns.set(color_codes=True)
sns.set_style("darkgrid", {"axes.facecolor": ".9"})

pp = pprint.PrettyPrinter(indent=4)

if __name__ == '__main__':

    print('Starting featureset collection...')

    web_domain_list = []
    nep_domain_list = [] 


    for directory in DIRECTORIES_WEB: 
        domain = Domain(directory, CATEGORY_WEB, str(ROOT_WEB + '/' + directory))
        web_domain_list.append(domain)


    for directory in DIRECTORIES_NEP: 
        domain = Domain(directory, CATEGORY_NEP, str(ROOT_NEP + '/' + directory))
        nep_domain_list.append(domain)


    sonar = gensim.models.KeyedVectors.load(SONAR_DIR)
    wiki = gensim.models.KeyedVectors.load(WIKI_DIR)

    print('Length raw web: ', len(web_domain_list))
    print('Length raw nep: ', len(nep_domain_list))


    print('Profiling build_featureset')
    cProfile.run('build_featureset(web_domain_list[0], sonar=sonar, wiki=wiki)')



    print('Building featureset web')
    with ThreadPool(processes=16) as p:
        web_domain_list = p.map(partial(build_featureset, sonar=sonar, wiki=wiki), web_domain_list[:DATASET])


    print('Building featureset nep')
    with ThreadPool(processes=16) as p:
        nep_domain_list = p.map(partial(build_featureset, sonar=sonar, wiki=wiki), nep_domain_list[:DATASET])


    web_tuplelist = []
    web_dictlist = []

    nep_tuplelist = []
    nep_dictlist = [] 

    remove_features_directory(kind="training")
    store_domain_features(web_domain_list, kind="training", cat="web")
    store_domain_features(web_domain_list, kind="training", cat="nep")

    for domain in web_domain_list: 
        fs_tuple = domain.get_featureset_category_tuple(CATEGORY_WEB)
        web_tuplelist.append(fs_tuple)
        web_dictlist.append(fs_tuple[0])


    for domain in nep_domain_list: 
        fs_tuple = domain.get_featureset_category_tuple(CATEGORY_NEP)
        nep_tuplelist.append(fs_tuple)
        nep_dictlist.append(fs_tuple[0])


    # Move data to Pandas Dataframe 
    web_df = pd.DataFrame(web_dictlist[:DATASET])
    nep_df = pd.DataFrame(nep_dictlist[:DATASET])



    web_tuplelist = web_tuplelist[:DATASET]
    nep_tuplelist = nep_tuplelist[:DATASET]

    print('Length shortened web: ', len(web_tuplelist))
    print('Length shortened nep: ', len(nep_tuplelist))


    # SAVING FEATURESETS TO DISK AND PICKLE
    print('Pickling featureset web')
    save_web_featureset = open("pickles/" + ROOT_WEB.split('/')[-1] + ".pickle", "wb") 
    pickle.dump(web_tuplelist, save_web_featureset)
    save_web_featureset.close()

    with open('features/total-web.txt', 'w') as fname:
        fname.write(pprint.pformat(web_tuplelist, indent=4))

    print('Pickling featureset nep')
    save_nep_featureset = open("pickles/" + ROOT_NEP.split('/')[-1] + ".pickle", "wb")
    pickle.dump(nep_tuplelist, save_nep_featureset)
    save_nep_featureset.close()

    with open('features/total-nep.txt', 'w') as fname:
        fname.write(pprint.pformat(nep_tuplelist, indent=4))


    featuresets = []
    
    print('Plotting features')
    for key in nep_dictlist[0]:
        plt.gcf().clear()
        # print("Plotting: {}. Web: {}, Nep: {}".format(key, web_df[key].dtype, nep_df[key].dtype) )

        if web_df[key].dtype == 'bool':
            if not nep_df[key].dtype == 'bool':
                raise Exception('Inconsistent data. Web and Nep do not match.')

            print("Data type boolean")
            print("Web: {}".format(web_df[key]))
            print("Nep: {}".format(nep_df[key]))

            new_df = pd.concat([web_df[key], nep_df[key]], axis=1)
            new_df.columns = ['web', 'nep']

            fig, ax = plt.subplots(1,2)
            sns.countplot(new_df['web'], ax=ax[0]);
            sns.countplot(new_df['nep'], ax=ax[1]);

            ax[0].set_ylim(0, len(nep_dictlist) * 1.1)
            ax[1].set_ylim(0, len(nep_dictlist) * 1.1)

            plt.suptitle(key, fontsize=12)
            plt.savefig("plots/{}.png".format(key))



        elif web_df[key].dtype == 'float64' or web_df[key].dtype == 'int64':
            print("Data type float or int")
            print("Web: {}".format(web_df[key]))
            print("Nep: {}".format(nep_df[key]))

            try: 
                sns.distplot(web_df[key], color='green', kde=False, rug=True);
                sns.distplot(nep_df[key], color='red', kde=False, rug=True);
                plt.suptitle(key, fontsize=12)
                plt.savefig("plots/{}.png".format(key))
            except np.linalg.linalg.LinAlgError:
                print("LinAlgError - no plot made!")
                

        else:  
            print("Data type undetermined")
            print(web_df[key])
            print(web_df[key].dtype)
            raise Exception('Unkown data type. Cannot plot')
            # sns.kdeplot(df_nep[col], shade=True)




    for item in web_tuplelist:
        featuresets.append(item)
    
    for item in nep_tuplelist:
        featuresets.append(item)

    random.shuffle(featuresets)


    v = DictVectorizer(sparse=False)
    lb = preprocessing.LabelBinarizer()

    X, y = zip(*featuresets)
    X = v.fit_transform(X)
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']


    print("Size featuresets: {}".format(len(featuresets)))
    print("Size set data: {}".format(len(X)))
    print("Size set labels: {}".format(len(y)))


    GaussianNB_classifier = GaussianNB()
    BernoulliNB_classifier = BernoulliNB()
    LogisticRegression_classifier = LogisticRegression()
    SGDClassifier_classifier = SGDClassifier()
    SVC_classifier = SVC()
    LinearSVC_classifier = LinearSVC()
    NuSVC_classifier = NuSVC()


    gnb_scores = cross_validate(GaussianNB_classifier, X, y, scoring=scoring, cv=10)
    bnb_scores = cross_validate(BernoulliNB_classifier, X, y, scoring=scoring, cv=10)
    lr_scores = cross_validate(LogisticRegression_classifier, X, y, scoring=scoring, cv=10)
    sgd_scores = cross_validate(SGDClassifier_classifier, X, y, scoring=scoring, cv=10)
    svc_scores = cross_validate(SVC_classifier, X, y, scoring=scoring, cv=10)
    lsvc_scores = cross_validate(LinearSVC_classifier, X, y, scoring=scoring, cv=10)
    #nusvc_scores = cross_validate(NuSVC_classifier, X, y, scoring=scoring, cv=10)

    gnb_avg = [np.mean(gnb_scores['train_accuracy']), np.mean(gnb_scores['test_precision']), np.mean(gnb_scores['test_recall']), np.mean(gnb_scores['test_f1']), np.mean(gnb_scores['test_roc_auc'])]

    bnb_avg = [np.mean(bnb_scores['train_accuracy']), np.mean(bnb_scores['test_precision']), np.mean(bnb_scores['test_recall']), np.mean(bnb_scores['test_f1']), np.mean(bnb_scores['test_roc_auc'])]

    lr_avg = [np.mean(lr_scores['train_accuracy']), np.mean(lr_scores['test_precision']), np.mean(lr_scores['test_recall']), np.mean(lr_scores['test_f1']), np.mean(lr_scores['test_roc_auc'])]

    sgd_avg = [np.mean(sgd_scores['train_accuracy']), np.mean(sgd_scores['test_precision']), np.mean(sgd_scores['test_recall']), np.mean(sgd_scores['test_f1']), np.mean(sgd_scores['test_roc_auc'])]

    svc_avg = [np.mean(svc_scores['train_accuracy']), np.mean(svc_scores['test_precision']), np.mean(svc_scores['test_recall']), np.mean(svc_scores['test_f1']), np.mean(svc_scores['test_roc_auc'])]

    lsvc_avg = [np.mean(lsvc_scores['train_accuracy']), np.mean(lsvc_scores['test_precision']), np.mean(lsvc_scores['test_recall']), np.mean(lsvc_scores['test_f1']), np.mean(lsvc_scores['test_roc_auc'])]

    #nusvc_avg = [np.mean(nusvc_scores['train_accuracy']), np.mean(nusvc_scores['test_precision']), np.mean(nusvc_scores['test_recall']), np.mean(nusvc_scores['test_f1']), np.mean(nusvc_scores['test_roc_auc'])]

    GaussianNB_classifier.fit(X, y)
    BernoulliNB_classifier.fit(X, y)
    LogisticRegression_classifier.fit(X, y)
    SGDClassifier_classifier.fit(X, y)
    SVC_classifier.fit(X, y)
    LinearSVC_classifier.fit(X, y)
    NuSVC_classifier.fit(X, y)



    print("accuracy/precision/recall/f1/roc-auc")

    print("GNB")
    pp.pprint(gnb_scores)
    pp.pprint(gnb_avg)
    print("\n\n\n")

    print("BNB")
    pp.pprint(bnb_scores)
    pp.pprint(bnb_avg)
    print("\n\n\n")

    print("LR")
    pp.pprint(lr_scores)
    pp.pprint(lr_avg)
    print("\n\n\n")

    print("SGD")
    pp.pprint(sgd_scores)
    pp.pprint(sgd_avg)
    print("\n\n\n")

    print("SVC")
    pp.pprint(svc_scores)
    pp.pprint(svc_avg)
    print("\n\n\n")

    print("LSVC")
    pp.pprint(lsvc_scores)
    pp.pprint(lsvc_avg)
    print("\n\n\n")

    #print("NuSVC")
    #pp.pprint(nusvc_scores)
    #pp.pprint(nusvc_avg)
    print("\n\n\n")


    print('Pickling models')

    save_gnb_classifier = open("pickles/classifier-gnb.pickle", "wb")
    pickle.dump(GaussianNB_classifier, save_gnb_classifier)
    save_gnb_classifier.close()

    save_bnb_classifier = open("pickles/classifier-bnb.pickle", "wb")
    pickle.dump(BernoulliNB_classifier, save_bnb_classifier)
    save_bnb_classifier.close()

    save_lr_classifier = open("pickles/classifier-lr.pickle", "wb")
    pickle.dump(LogisticRegression_classifier, save_lr_classifier)
    save_lr_classifier.close()

    save_sgd_classifier = open("pickles/classifier-sgd.pickle", "wb")
    pickle.dump(SGDClassifier_classifier, save_sgd_classifier)
    save_sgd_classifier.close()

    save_svc_classifier = open("pickles/classifier-svc.pickle", "wb")
    pickle.dump(SVC_classifier, save_svc_classifier)
    save_svc_classifier.close()

    save_lsvc_classifier = open("pickles/classifier-lsvc.pickle", "wb")
    pickle.dump(LinearSVC_classifier, save_lsvc_classifier)
    save_lsvc_classifier.close()

    #save_nusvc_classifier = open("pickles/classifier-nusvc.pickle", "wb")
    #pickle.dump(NuSVC_classifier, save_nusvc_classifier)
    #save_nusvc_classifier.close()

    print("Succeeded. Shutting down.")















    





    



    








