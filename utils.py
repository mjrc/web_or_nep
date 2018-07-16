from os.path import isdir
from os import mkdir
import shutil, pickle


def remove_features_directory(kind=""):
    dirname = 'features-{}/'.format(kind)
    print('Writing directory "{0}"'.format(dirname), end="")
    if isdir(dirname):
        shutil.rmtree(dirname, ignore_errors=True)
    mkdir(dirname)

def store_domain_features(domain_list, kind="", cat=""):
    dirname = 'features-{}/'.format(kind)



    for domain in domain_list: 
        for k, v in vars(domain).items():
            filename = '{}{}-{}'.format(dirname, k, cat)
            with open(filename, 'a') as outfile:
                outfile.write('http://{0:<30}\t{1:40}\n'.format(domain.domain_name, str(v)))

    print('done.')
    return




if __name__ == '__main__': 
    pass 
