

class Domain:

    domain_name = None
    label = None
    category = None 
    directory = None

    features = {}
    title = None
    titlecnt = None 
    metadesc = None
    metadesccnt = None 
    metakeyw = None
    metakeywcnt = None
    metaog = None

    links_internal = None
    links_external = None
    links_hash = None 
    links_mailto = None
    links_javascript = None
    links_intend = None
    links_map = None 

    scripts = None
    scriptscnt = None 
    styles = None 
    stylescnt = None 

    lexcnt = None
    lexunq = None 
    lexdiv = None

    label_title_similarity_sonar = None 
    label_title_similarity_wiki = None
    label_title_wmdistance_sonar = None 
    label_title_wmdistance_wiki = None 

    distance_edit = None
    distance_jaccard = None

    imagecnt = None

    iban = None
    ideal = None

    currency = None 
    currencycnt = None

    phone = None
    address = None
    postcode = None
    place = None

    analytics = None
    fonts = None
    sm_link = None
    sm_deep_link = None

    def __init__(self, name, cat="", directory=""):
        self.domain_name = name
        self.category = cat
        self.directory = directory

    def get_featureset_category_tuple(self, cat=""):
        fs = {}

        #fs['domain'] = self.domain_name
        #fs['title'] = self.title

        # Is a boolean 
        if not (self.metadesc is None):
            if self.metadesc:
                fs['metadesc'] = True
            else:
                fs['metadesc'] = False 

        # Is a zero or higher integer 
        if not (self.metadesccnt is None):
            fs['metadesccnt'] = self.metadesccnt

        # Is a boolean 
        if not (self.metakeyw is None):
            if self.metakeyw:
                fs['metakeyw'] = True
            else:  
                fs['metakeyw'] = False 
        
        # Is a zero or higher integer 
        if not (self.metakeywcnt is None):
            fs['metakeywcnt'] = self.metakeywcnt

        if not (self.metaog is None):
            if self.metaog:
                fs['metaog'] = True
            else:
                fs['metaog'] = False

        if not (self.links_internal is None):
            fs['links_internal'] = len(self.links_internal)
        
        if not (self.links_external is None):
            fs['links_external'] = len(self.links_external)

        if not (self.links_hash is None):
            fs['links_hash'] = len(self.links_hash)

        if not (self.links_mailto is None):
            fs['links_mailto'] = len(self.links_mailto)

        if not (self.links_javascript is None):
            fs['links_javascript'] = len(self.links_javascript)

        if not (self.links_intend is None):
            fs['links_intend'] = len(self.links_intend)

        if not (self.links_map is None):
            fs['links_map'] = len(self.links_map)

        if not (self.styles is None):
            if self.styles:
                fs['styles'] = True
            else:
                fs['styles'] = False 

        if not (self.stylescnt is None):
            fs['stylescnt'] = self.stylescnt

        if not (self.scripts is None):
            if self.scripts:
                fs['scripts'] = True
            else:
                fs['scripts'] = False 

        if not (self.scriptscnt is None):
            fs['scriptscnt'] = self.scriptscnt 

        if not (self.imagecnt is None):
            fs['imagecnt'] = self.imagecnt

        if not (self.lexcnt is None):
            fs['lexcnt'] = self.lexcnt

        if not (self.lexunq is None):
            fs['lexunq'] = self.lexunq

        if not (self.lexdiv is None):
            fs['lexdiv'] = self.lexdiv

        if not (self.label_title_similarity_sonar is None) and not (self.label_title_similarity_wiki is None):
            fs['lt_sim_sonar'] = self.label_title_similarity_sonar
            fs['lt_sim_wiki'] = self.label_title_similarity_wiki

        if not (self.label_title_wmdistance_sonar is None) and not (self.label_title_wmdistance_wiki is None):
            fs['lt_dist_sonar'] = self.label_title_wmdistance_sonar
            fs['lt_dist_wiki'] = self.label_title_wmdistance_wiki

        if not (self.distance_edit is None):
            fs['distance_edit'] = self.distance_edit

        if not (self.distance_jaccard is None):
            fs['distance_jaccard'] = self.distance_jaccard

        if not (self.iban is None):
            if self.iban:
                fs['iban'] = True
            else:
                fs['iban'] = False

        if not (self.currency is None): 
            if self.currency: 
                fs['currency'] = True
            else: 
                fs['currency'] = False

        if not (self.currencycnt is None): 
            fs['currencycnt'] = self.currencycnt

        if not (self.phone is None):
            if self.phone:
                fs['phone'] = True
            else:
                fs['phone'] = False

        if not (self.address is None):
            if self.address:
                fs['address'] = True
            else:
                fs['address'] = False

        if not (self.postcode is None):
            if self.postcode:
                fs['postcode'] = True
            else:
                fs['postcode'] = False

        if not (self.place is None):
            if self.place:
                fs['place'] = True
            else:
                fs['place'] = False

        if not (self.analytics is None):
            if self.analytics:
                fs['analytics'] = True
            else:
                fs['analytics'] = False

        if not (self.sm_link is None):
            if self.sm_link:
                fs['sm_link'] = True
                if self.sm_deep_link:
                    fs['sm_deep_link'] = True
                else:
                    fs['sm_deep_link'] = False
            else:
                fs['sm_link'] = False
                fs['sm_deep_link'] = False

        if not cat is "":
            return fs, cat 
        else:
            return fs
