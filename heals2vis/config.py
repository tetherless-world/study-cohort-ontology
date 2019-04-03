# -*- config:utf-8 -*-

import os
import logging
from datetime import timedelta

project_name = "heals2vis"
import importer

import autonomic
import agents.nlp as nlp
import rdflib
from datetime import datetime

# Set to be custom for your project
LOD_PREFIX = 'http://localhost'
#os.getenv('lod_prefix') if os.getenv('lod_prefix') else 'http://hbgd.tw.rpi.edu'

skos = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")

from heals2vis.agent import *

tnm_where='''?Tumor sio:isPartOf ?Subject .
  ?Tumor prov:wasGeneratedBy ?Cancer .
  ?Tumor rdf:type ncit:C3262 . 

  ?T rdf:type [ rdfs:subClassOf sio:Diameter ;
                rdfs:subClassOf ncit:C120284 ] .
  ?T sio:isAttributeOf ?Tumor .
    
  ?N rdf:type [ rdfs:subClassOf sio:Count ] .
  ?N sio:isAttributeOf [ rdf:type ncit:C12745 ;
                         prov:wasDerivedFrom ?Subject ] .
  
  ?M rdf:type [ rdfs:subClassOf sio:StatusDescriptor ] .
  ?M sio:isAttributeOf [ rdf:type ncit:C19151 ;
                         sio:inRelationTo ?Tumor ] .
  
  ?Grade sio:isAttributeOf ?Tumor .
  ?Grade rdf:type [ rdfs:subClassOf ncit:C135461 ] .

  ?ER rdf:type [ rdfs:subClassOf sio:StatusDescriptor ] .
  ?ER sio:isAttributeOf [ rdf:type ncit:C38361 ;
                          prov:wasDerivedFrom ?Subject ] .
  
  ?PR rdf:type [ rdfs:subClassOf sio:StatusDescriptor ] .
  ?PR sio:isAttributeOf [ rdf:type ncit:C17075 ;
                          prov:wasDerivedFrom ?Subject ] .
  
  ?HER2 rdf:type [ rdfs:subClassOf sio:StatusDescriptor ] .
  ?HER2 sio:isAttributeOf [ rdf:type ncit:C17756 ;
                            prov:wasDerivedFrom ?Subject ] .

'''

# base config class; extend it to your needs.
Config = dict(
    # use DEBUG mode?
    DEBUG = False,

    site_name = "heals2vis",

    root_path = '/apps/whyis',

    # use TESTING mode?
    TESTING = False,

    # use server x-sendfile?
    USE_X_SENDFILE = False,

    WTF_CSRF_ENABLED = True,
    SECRET_KEY = "oiaXTKsVmvxwDiOsPp/MJdL2+fSPbCwF",

    nanopub_archive = {
        'depot.storage_path' : "/data/nanopublications",
    },

    file_archive = {
        'depot.storage_path' : '/data/files',
        'cache_max_age' : 3600*24*7,
    },
    vocab_file = "/apps/heals2vis/vocab.ttl",
    WHYIS_TEMPLATE_DIR = [
        "/apps/heals2vis/templates",
    ],
    WHYIS_CDN_DIR = "/apps/heals2vis/static",

    # LOGGING
    LOGGER_NAME = "%s_log" % project_name,
    LOG_FILENAME = "/var/log/%s/output-%s.log" % (project_name,str(datetime.now()).replace(' ','_')),
    LOG_LEVEL = logging.INFO,
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s", # used by logging.Formatter

    PERMANENT_SESSION_LIFETIME = timedelta(days=7),

    # EMAIL CONFIGURATION
    ## MAIL_SERVER = "",
    ## MAIL_PORT = 587,
    ## MAIL_USE_TLS = True,
    ## MAIL_USE_SSL = False,
    ## MAIL_DEBUG = False,
    ## MAIL_USERNAME = '',
    ## MAIL_PASSWORD = '',
    ## DEFAULT_MAIL_SENDER = "Shruthi <charis@rpi.edu",

    # see example/ for reference
    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance
    BLUEPRINTS = [],

    lod_prefix = LOD_PREFIX,
    SECURITY_EMAIL_SENDER = "Shruthi <charis@rpi.edu",
    SECURITY_FLASH_MESSAGES = True,
    SECURITY_CONFIRMABLE = False,
    SECURITY_CHANGEABLE = True,
    SECURITY_TRACKABLE = True,
    SECURITY_RECOVERABLE = True,
    SECURITY_REGISTERABLE = True,
    SECURITY_PASSWORD_HASH = 'sha512_crypt',
    SECURITY_PASSWORD_SALT = 'JzjOQ1lCUZC0C6Es589H7uYPveUh0H5F',
    SECURITY_SEND_REGISTER_EMAIL = False,
    SECURITY_POST_LOGIN_VIEW = "/",
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False,
    SECURITY_DEFAULT_REMEMBER_ME = True,
    ADMIN_EMAIL_RECIPIENTS = [],
    db_defaultGraph = LOD_PREFIX + '/',


    admin_queryEndpoint = 'http://localhost:8080/blazegraph/namespace/admin/sparql',
    admin_updateEndpoint = 'http://localhost:8080/blazegraph/namespace/admin/sparql',
    
    knowledge_queryEndpoint = 'http://localhost:8080/blazegraph/namespace/knowledge/sparql',
    knowledge_updateEndpoint = 'http://localhost:8080/blazegraph/namespace/knowledge/sparql',

    LOGIN_USER_TEMPLATE = "auth/login.html",
    CELERY_BROKER_URL = 'redis://localhost:6379/0',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0',
    default_language = 'en',
    namespaces = [
        importer.LinkedData(
            prefix = LOD_PREFIX+'/doi/',
            url = 'http://dx.doi.org/%s',
            headers={'Accept':'text/turtle'},
            format='turtle',
            postprocess_update= '''insert {
                graph ?g {
                    ?pub a <http://purl.org/ontology/bibo/AcademicArticle>.
                }
            } where {
                graph ?g {
                    ?pub <http://purl.org/ontology/bibo/doi> ?doi.
                }
            }
            '''
        ),
        importer.LinkedData(
            prefix = LOD_PREFIX+'/dbpedia/',
            url = 'http://dbpedia.org/resource/%s',
            headers={'Accept':'text/turtle'},
            format='turtle',
            postprocess_update= '''insert {
                graph ?g {
                    ?article <http://purl.org/dc/terms/abstract> ?abstract.
                }
            } where {
                graph ?g {
                    ?article <http://dbpedia.org/ontology/abstract> ?abstract.
                }
            }
            '''
        )
    ],
    inferencers = {
        "SETLr": autonomic.SETLr(),
        "Class Subsumption Closure": autonomic.Deductor(
            resource="?resource", 
            prefixes="", 
            where = "\t?resource rdfs:subClassOf ?class .\n\t?class rdfs:subClassOf+ ?superClass .",
            construct="?resource rdfs:subClassOf ?superClass .",
            explanation="Since {{class}} is a subclass of {{superClass}}, any class that is a subclass of {{class}} is also a subclass of {{superClass}}. Therefore, {{resource}} is a subclass of {{superClass}}."),
        "Instance Subsumbtion Closure": autonomic.Deductor(
            resource="?resource", 
            prefixes="", 
            where = "\t?resource rdf:type ?class .\n\t?class rdfs:subClassOf+ ?superClass .",
            construct="?resource rdf:type ?superClass .",
            explanation="Any instance of {{class}} is also an instance of {{superClass}}. Therefore, since {{resource}} is a {{class}}, it also is a {{superClass}}."),
        "Object Property Subsumbtion Closure": autonomic.Deductor(
            resource="?resource", 
            prefixes="",
            where = "\t?resource ?p ?o .\n\t?p rdf:type owl:ObjectPropery .\n\t?p owl:subPropertyOf+ ?superProperty .",
            construct="?resource ?superProperty ?o .",
            explanation="Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."),
        "Datatype Property Subsumbtion Closure": autonomic.Deductor(
            resource="?resource",
            prefixes="",
            where = "\t?resource ?p ?o .\n\t?p rdf:type owl:DatatypePropery .\n\t?p owl:subPropertyOf+ ?superProperty .",
            construct="?resource ?superProperty ?o .",
            explanation="Any subject and object related by the property {{p}} is also related by {{superProperty}}. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{superProperty}} {{o}}."),
        "Class Equivalency Closure": autonomic.Deductor(
            resource="?resource", 
            prefixes="",
            where = "\t?resource a ?superClass.\n\t?superClass owl:equivalentClass ?equivClass .", 
            construct="?resource a ?equivClass .",
            explanation="{{superClass}} is equivalent to {{equivClass}}, so since {{resource}} is a {{superClass}}, it is also a {{equivClass}}."),
        "Property Equivalency Closure": autonomic.Deductor(
            resource="?resource", 
            prefixes="",
            where = "\t?resource ?p ?o .\n\t?p owl:equivalentProperty ?equivProperty .", 
            construct="?resource ?equivProperty ?o .",
            explanation="The properties {{p}} and {{equivProperty}} are equivalent. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{resource}} {{equivProperty}} {{o}}."),
        "Property Inversion Closure": autonomic.Deductor(
            resource="?resource", 
            prefixes="",
            where = "\t?resource ?p ?o .\n\t?p owl:inverseOf ?inverseProperty .", 
            construct="?o ?inverseProperty ?resource .",
            explanation="The properties {{p}} and {{inverseProperty}} are inversely related to eachother. Therefore, since {{resource}} {{p}} {{o}}, it is implied that {{o}} {{inverseProperty}} {{resource}}."),
        #"Some Values From": autonomic.Deductor(resource="?resource", prefixes="", where = "", construct="", explanation=""),
        #"Property Path Closure": autonomic.Deductor(resource="?resource", prefixes="", where = "", construct="", explanation=""),
        "Triple Negative Finding":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
 "ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
 "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
                "efo": "http://www.ebi.ac.uk/efo/EFO_"},
            construct="?Subject cst:hasDisease efo:0005537 .",
            where=tnm_where + """
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
     explanation="""{{Subject}} was found to have Triple Negative Breast Cancer since the following are true:
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "Estrogen-receptor Positive Finding":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
"efo": "http://www.ebi.ac.uk/efo/EFO_"},
            construct="?Subject cst:hasDisease efo:1000649 .",
            where=tnm_where + """
  ?ER rdf:type cst:ER_Pos .
""",
     explanation="""{{Subject}} was found to have Estrogen-receptor Positive Breast Cancer since the following are true:
Estrogen receptor status is ER_Pos .
"""),
        "Estrogen-receptor Negative Finding":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
"efo": "http://www.ebi.ac.uk/efo/EFO_"},
            construct="?Subject cst:hasDisease efo:1000650 .",
            where=tnm_where + """
  ?ER rdf:type cst:ER_Neg .
""",
     explanation="""{{Subject}} was found to have Estrogen-receptor Negative Breast Cancer since the following are true:
Estrogen receptor status is ER_Neg .
"""),
        "Progesterone-receptor Positive Finding":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
"doid": "http://purl.obolibrary.org/obo/DOID_"},
            construct="?Subject cst:hasDisease doid:0060077 .",
            where=tnm_where + """
  ?PR rdf:type cst:PR_Pos .
""",
     explanation="""{{Subject}} was found to have Progesterone-receptor Positive Breast Cancer since the following are true:
Progesterone receptor status is PR_Pos .
"""),
        "Progesterone-receptor Negative Finding":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
"doid": "http://purl.obolibrary.org/obo/DOID_"},
            construct="?Subject cst:hasDisease doid:0060078 .",
            where=tnm_where + """
  ?PR rdf:type cst:PR_Neg .
""",
     explanation="""{{Subject}} was found to have Progesterone-receptor Negative Breast Cancer since the following are true:
Progesterone receptor status is PR_Neg .
"""),

        "HER2-receptor Positive Finding":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
"doid": "http://purl.obolibrary.org/obo/DOID_"},
            construct="?Subject cst:hasDisease doid:0060079 .",
            where=tnm_where + """
  ?HER2 rdf:type cst:HER2_Pos .
""",
     explanation="""{{Subject}} was found to have HER2-receptor Positive Breast Cancer since the following are true:
Progesterone receptor status is HER2_Pos .
"""),
        "HER2-receptor Negative Finding":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
"doid": "http://purl.obolibrary.org/obo/DOID_"},
            construct="?Subject cst:hasDisease doid:0060080 .",
            where=tnm_where + """
  ?HER2 rdf:type cst:HER2_Neg .
""",
     explanation="""{{Subject}} was found to have HER2-receptor Negative Breast Cancer since the following are true:
Progesterone receptor status is HER2_Neg .
"""),
"OncoTypeDX Testing":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#",
"doid": "http://purl.obolibrary.org/obo/DOID_"},
            construct="?Subject cst:hasRecommendedTest 'OncoTypeDX Testing'^^xsd:string .",
            where=tnm_where + """
  ?ER rdf:type cst:ER_Pos .
  ?N rdf:type cst:N0 .
""",
     explanation="""{{Subject}} can be prescribed OncoTypeDX Testing:
Estrogen receptor status is ER_Pos .
Degree of spread to lymph nodes is N0 .
"""),
        "R7 Stage 0 (0)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                      "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage I (0)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                      "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_I .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage I since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage I (1)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_I .",
            where=tnm_where + """
  ?T rdf:type cst:T1mic .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage I since the following are true: 
Primary Tumor size is T1mic . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IA (0)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IA (1)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                      "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R7 Stage IB (0)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                      "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IB (1)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                      "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (0)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                      "cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (1)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (2)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (3)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
"""),
        "R7 Stage IIB (0)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIB (1)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst":"http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (0)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (1)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
 "ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (2)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (3)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (4)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (5)":autonomic.Deductor(
            resource="?Tumor",
            prefixes={
"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
"cst": "http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#"},
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
                "R7 Stage 0 (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage I (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_I .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage I since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage I (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_I .",
            where=tnm_where + """
  ?T rdf:type cst:T1mic .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage I since the following are true: 
Primary Tumor size is T1mic . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IA (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IA (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R7 Stage IB (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IB (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIA (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
"""),
        "R7 Stage IIB (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIB (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIA (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIA (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIA (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIA (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIA (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIA (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIA (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIA (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R7 Stage IIIB (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIB (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIB (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IIIC (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IIIC .",
            where=tnm_where + """
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IIIC since the following are true: 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
"""),
        "R7 Stage IV (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R7_Stage_IV .",
            where=tnm_where + """
  ?M rdf:type cst:M1 .
""",
            explanation="""{{Tumor}} was found to have stage R7 Stage IV since the following are true: 
Presence of distant metastasis is M1 . 
"""),
        "R8 Stage 0 (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage 0 (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage 0 (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_0 .",
            where=tnm_where + """
  ?T rdf:type cst:Tis .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage 0 since the following are true: 
Primary Tumor size is Tis . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (24)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (25)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (26)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (27)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (28)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (29)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (30)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (31)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (32)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (33)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (34)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (35)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (36)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (37)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (38)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (39)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (40)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (41)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (42)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (43)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (44)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (45)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (46)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (47)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (48)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (49)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (50)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (51)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (52)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (53)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IA (54)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (55)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IA (56)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IB (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1mi .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1mi . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (24)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (25)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (26)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (27)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (28)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (29)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (30)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (31)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IB (32)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (24)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (25)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (26)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (27)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (28)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (29)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (30)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (31)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (32)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (33)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (34)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (35)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (36)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (37)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (38)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (39)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (40)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (41)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (42)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (43)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (44)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (45)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (46)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (47)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (48)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (49)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (50)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (51)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (52)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIA (53)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (54)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (55)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (56)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (57)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (58)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (59)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (60)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (61)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (62)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (63)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (64)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (65)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (66)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (67)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (68)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (69)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (70)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (71)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (72)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (73)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (74)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (75)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIA (76)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (24)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (25)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (26)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (27)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (28)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (29)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (30)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (31)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIB (32)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (33)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (34)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (35)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (36)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (37)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIB (38)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (24)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (25)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (26)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (27)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (28)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (29)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (30)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (31)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (32)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (33)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (34)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (35)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (36)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (37)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (38)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (39)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (40)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (41)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (42)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (43)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (44)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (45)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (46)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (47)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (48)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (49)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (50)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (51)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (52)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (53)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (54)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (55)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (56)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (57)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (58)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (59)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (60)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (61)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (62)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (63)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (64)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (65)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (66)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (67)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (68)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIA (69)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (70)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (71)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (72)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (73)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (74)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (75)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (76)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (77)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (78)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (79)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (80)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIA (81)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIA .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIA since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (24)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (25)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (26)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (27)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (28)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (29)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (30)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (31)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (32)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (33)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (34)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (35)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (36)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (37)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (38)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (39)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (40)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (41)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (42)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (43)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (44)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (45)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (46)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (47)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (48)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (49)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (50)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (51)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (52)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (53)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (54)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (55)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (56)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (57)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (58)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (59)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (60)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (61)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (62)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (63)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (64)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (65)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (66)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (67)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (68)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (69)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (70)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (71)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (72)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (73)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (74)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (75)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (76)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (77)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (78)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (79)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (80)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (81)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (82)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (83)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (84)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (85)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (86)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (87)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIB (88)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (89)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (90)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIB (91)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIB .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIB since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIC (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T0 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T0 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T1 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T1 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T2 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T2 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T3 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T3 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIC (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIC (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIC (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IIIC (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N0 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N0 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N1 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N1 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T4 .
  ?N rdf:type cst:N2 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T4 . 
Degree to spread of lymph nodes is N2 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IIIC (24)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IIIC .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N3 .
  ?M rdf:type cst:M0 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IIIC since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N3 . 
Presence of distant metastasis is M0 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (0)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (1)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (2)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (3)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (4)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (5)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (6)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (7)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade1 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade1 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (8)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (9)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (10)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (11)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (12)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (13)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (14)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (15)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade2 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade2 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (16)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (17)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (18)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (19)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Pos .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Pos .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (20)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (21)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Pos .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Pos .
Progesterone receptor status is PR_Neg .
"""),
        "R8 Stage IV (22)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Pos .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Pos .
"""),
        "R8 Stage IV (23)":autonomic.Deductor(
            resource="?Tumor",

            prefixes= {'cst': 'http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#', 'ncit': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#', 'efo': 'http://www.ebi.ac.uk/efo/EFO_'}, 
            construct="?Tumor cst:hasAJCCStage cst:R8_Stage_IV .",
            where=tnm_where + """
  ?T rdf:type cst:T .
  ?N rdf:type cst:N .
  ?M rdf:type cst:M1 .
  ?Grade rdf:type cst:Grade3 .
  ?HER2 rdf:type cst:HER2_Neg .
  ?ER rdf:type cst:ER_Neg .
  ?PR rdf:type cst:PR_Neg .
""",
            explanation="""{{Tumor}} was found to have stage R8 Stage IV since the following are true: 
Primary Tumor size is T . 
Degree to spread of lymph nodes is N . 
Presence of distant metastasis is M1 . 
Grade is Grade3 . 
HER2 status is HER2_Neg .
Estrogen receptor status is ER_Neg .
Progesterone receptor status is PR_Neg .
"""),
#        "HTML2Text" : nlp.HTML2Text(),
#        "EntityExtractor" : nlp.EntityExtractor(),
#        "EntityResolver" : nlp.EntityResolver(),
#        "TF-IDF Calculator" : nlp.TFIDFCalculator(),
#        "SKOS Crawler" : autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related])
    },
    inference_tasks = [
#        dict ( name="SKOS Crawler",
#               service=autonomic.Crawler(predicates=[skos.broader, skos.narrower, skos.related]),
#               schedule=dict(hour="1")
#              )
    ]
)


# config class for development environment
Dev = dict(Config)
Dev.update(dict(
    DEBUG = True,  # we want debug level output
    MAIL_DEBUG = True,
    EXPLAIN_TEMPLATE_LOADING = True,
    DEBUG_TB_INTERCEPT_REDIRECTS = False
))

# config class used during tests
Test = dict(Config)
Test.update(dict(
    TESTING = True,
    WTF_CSRF_ENABLED = False
))

