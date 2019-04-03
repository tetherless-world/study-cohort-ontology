import autonomic
from rdflib import *
from slugify import slugify
import nanopub
import json

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
sioc_types = Namespace("http://rdfs.org/sioc/types#")
sioc = Namespace("http://rdfs.org/sioc/ns#")
sio = autonomic.sio
dc = autonomic.dc
np = autonomic.np
prov = autonomic.prov
graphene = autonomic.graphene
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
seerkb = Namespace("http://idea.rpi.edu/heals/kb/seer#")
ncit = Namespace("http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#")
pr = Namespace("http://purl.obolibrary.org/obo/PR_")
cst = Namespace("http://idea.rpi.edu/ontologies/cancer_staging_terms.owl#")
uberon = Namespace("http://purl.obolibrary.org/obo/UBERON_")
hasco = Namespace("http://hadatac.org/ont/hasco#")

class InferStage(autonomic.UpdateChangeService):
    activity_class = graphene.StagingAgent

    def getInputClass(self):
        #return seerkb.tumor 
	return ""

    def getOutputClass(self):
        return ""

    def get_query(self):
        return '''
#PREFIX rdfs: <''' + rdfs + '''>
#PREFIX rdf: <''' + rdf + '''>
PREFIX foaf: <''' + self.app.NS.foaf + '''>
PREFIX np: <''' + np + '''>
PREFIX sio: <''' + sio + '''>
PREFIX hasco: <''' + hasco + '''>
PREFIX prov: <''' + prov + '''>
PREFIX ncit: <''' + ncit + '''>
#PREFIX pr: <''' + pr + '''>
SELECT DISTINCT ?Tumor WHERE {
?Tumor sio:isPartOf ?Subject .
?Tumor prov:wasGeneratedBy ?Cancer .
?Tumor rdf:type ncit:C3262 . 
}
'''
    def process(self, i, o):
        print "Processing", i.identifier, self
        tumorResults = self.app.db.query('''
PREFIX ncit: <''' + ncit + '''>
SELECT DISTINCT ?GradeVal ?OncoDXVal ?HER2Val ?ERVal ?PRVal ?TVal ?NVal ?MVal where {

?Tumor sio:isPartOf ?Subject .
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

FILTER(str(?Tumor)="%s") .
}''' % (i.identifier) )
        #for key in tumorResults.json.keys() :
        #    print tumorResults.json[key]
	resultsDict = {"HER2Val":None,"ERVal":None,"PRVal":None,"TVal":None,"NVal":None,"MVal":None,"GradeVal":None,"OncoDXVal":None}
        '''HER2Val = None
        ERVal = None
        PRVal = None
        TVal = None
        NVal = None
        MVal = None
        GradeVal = None
        OncoDXVal = None'''
        for key in tumorResults.json["results"]["bindings"][0].keys():
	    resultsDict[key] = tumorResults.json["results"]["bindings"][0][key]["value"]
        print resultsDict
'''
        if "HER2Val" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["HER2Val"]["value"]
            resultsDict["ER2Val"] = tumorResults.json["results"]["bindings"][0]["HER2Val"]["value"]
        if "ERVal" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["ERVal"]["value"]
            ERVal = tumorResults.json["results"]["bindings"][0]["ERVal"]["value"]
        if "PRVal" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["PRVal"]["value"]
            PRVal = tumorResults.json["results"]["bindings"][0]["PRVal"]["value"]
        if "TVal" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["TVal"]["value"]
            TVal = tumorResults.json["results"]["bindings"][0]["TVal"]["value"]
        if "NVal" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["NVal"]["value"]
            NVal = tumorResults.json["results"]["bindings"][0]["NVal"]["value"]
        if "MVal" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["MVal"]["value"]
            MVal = tumorResults.json["results"]["bindings"][0]["MVal"]["value"]
        if "GradeVal" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["GradeVal"]["value"]
            GradeVal = tumorResults.json["results"]["bindings"][0]["GradeVal"]["value"]
        if "OncoDXVal" in tumorResults.json["results"]["bindings"][0].keys() :
            #print tumorResults.json["results"]["bindings"][0]["OncoDXVal"]["value"]
            OncoDXVal = tumorResults.json["results"]["bindings"][0]["OncoDXVal"]["value"]'''
