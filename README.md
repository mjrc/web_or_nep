# Content-based Classification of Fraudulent Webshops 

This repository contains the source code, the pickled AdaBoost model and plots of the Content-based Classification of Fraudulent Webshops research. This research was peformed by Sjors Haanen and Mick Cox, as a part of the Research Project 2 Course, [System & Network Engineering](https://www.os3.nl/), University of Amsterdam. 

<p align="center">
 <img width="600" src="https://raw.githubusercontent.com/mjrc/web_or_nep/master/images/sne-sidn.png">
</p>


## Abstract ## 

Fraudulent webshops form a problem on the Internet and the Dutch Consumers Association (Consumentenbond) reports that at least one out of five webshops in the .nl top level domain (TLD) acts in a fraudulent manner. Content-based classification can be part of the detection and mitigation strategy. This method demonstrates the viability of this approach, and follows multiple steps. First, we identified prerequisites necessary for
running a successful fraudulent webshop. Second, based on these prerequisites, features were engineered to classify these fraudulent webshops. Third, a classification model was trained, resulting in an
F1-score of 99.15% using 10-fold cross validation. Fourth, this trained model classified an unlabelled dataset of 4.9M domains. Although results include many false positives, we estimate the precision to be 30.1%. This would imply that out of 32,815 positively classified domains, 9,877 are correctly identified fraudulent webshops. Furthermore, we also estimate that results in general will improve if more optimisations are
conducted. Ultimately, our contribution is constituted on the demonstration that a content-based classification method is viable and the presentation and analysis of characteristics and features used. 


## Documentation ## 

The directory includes the following: 
 - /features: contains the feature values extracted during training an classification
 - /pickles: contains the pickled models created during training
 - /plots: contains automaticly generated plots of each feature during training
 - /sets: contains input files for both classes 
 - /resources: includes ancillary files such as stopwords, city names and a dictionairy 
 - config.ini: used for configuring location of classes and size of dataset
 - trainer.py: can be used to start feature extraction and training
 - web_or_nep.py: used for testing the model on unlabeled samples
 - classifier.py: invoked by web_or_nep.py and contains classifier logic and confidence calculation  
 - featuresets.py: invoked by trainer.py and classifier.py to extract features
 - domain.py: contains the class for a domain


### Configuration ### 
Before running either trainer.py or web_or_nep.py, make sure the SoNaR500 and Wiki word vectors are available and pointed to in config.ini. These can be downloaded from [Dutch Embeddings](https://github.com/clips/dutchembeddings). 
