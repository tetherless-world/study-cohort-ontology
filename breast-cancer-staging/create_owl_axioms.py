#!/usr/bin/python

# Generate the OWL Axioms for the Breast Cancer staging according to the AJCC 8th Revision.
# The Mappings for various cancer stages are available in the map folder.

import os
import re
from rdflib import Graph

__author__ = "Oshani Seneviratne"
__credits__ = ["Oshani Seneviratne"]
__license__ = "Apache"
__version__ = "2"
__maintainer__ = "Oshani Seneviratne"
__email__ = "senevo@rpi.edu"
__status__ = "Development"

STAGING_ONTOLOGY_DIR = "ontologies/"
MAP_DIR = "map/"
STAGING_REVISIONS = {"R7", "R8"}


def getFileName(revision, format="xml"):
    """
    Create a filename based on the format passed in. Defaults to xml.
    :param revision:
    :param format:
    :return:
    """
    fileExtension = ""
    if format != "xml":
        fileExtension = "." + format
    return STAGING_ONTOLOGY_DIR + revision + "/ajcc_" + revision + "_staging_axioms.owl" + fileExtension


def createOntology(revision):

    source = 'AJCC Cancer Staging ' + revision + \
             '\n\t\t\tThis ontology is our interpretation of the staging criteria available at '
    if revision == 'R7':
        source += '\n\t\t\thttps://cancerstaging.org/references-tools/quickreferences/Documents/BreastMedium.pdf. '
    if revision == 'R8':
        source += '\n\t\t\thttps://cancerstaging.org/references-tools/deskreferences/Pages/default.aspx ' \
                  '(The breast cancer chapter was obtained by signing up as a Software Developer). '
    source += '\n\t\t\tWe, the developers of the ontology, assume full responsibility for the statements contained ' \
              '\n\t\t\tin this file.'

    # print header RDF
    header = '''<?xml version="1.0"?>

    <!DOCTYPE rdf:RDF [
        <!ENTITY dc "http://purl.org/dc/terms/" >
        <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
        <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
        <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
        <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
        <!ENTITY skos "http://www.w3.org/2004/02/skos/core#" >
        <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
        <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
        <!ENTITY cst "http://idea.tw.rpi.edu/projects/heals/ontologies/cancer_staging_terms.owl#" >
        <!ENTITY ncit "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#" >
    ]>

    <rdf:RDF xmlns="http://idea.tw.rpi.edu/projects/heals/ontologies/{0}/ajcc_{0}_staging_axioms.owl#"
        xml:base="http://idea.tw.rpi.edu/projects/heals/ontologies/{0}/ajcc_{0}_staging_axioms.owl"
        xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
        xmlns:dc="http://purl.org/dc/terms/"
        xmlns:owl="http://www.w3.org/2002/07/owl#"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:skos="http://www.w3.org/2004/02/skos/core#"
        xmlns:ncit="http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#"
        xmlns:cst="http://idea.tw.rpi.edu/projects/heals/ontologies/cancer_staging_terms.owl#">

        <owl:Ontology rdf:about="http://idea.rpi.edu/ontologies/{0}/ajcc_{0}_staging_axioms.owl">
            <owl:versionInfo rdf:datatype="http://www.w3.org/2001/XMLSchema#string">version 0.1</owl:versionInfo>
            <dc:version></dc:version>>
            <dc:creator rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Tetherless World Constellation, 
                Rensselaer Polytechnic Institute
            </dc:creator>
            <dc:title xml:lang="en">AJCC Cancer Staging Ontology - {0}</dc:title>
            <dc:source xml:lang="en">{1}</dc:source>
            <dc:license xml:lang="en" rdf:about="http://www.apache.org/licenses/LICENSE-2.0"/>
            <owl:imports rdf:resource="http://idea.tw.rpi.edu/projects/heals/ontologies/cancer_staging_terms.owl"/>
        </owl:Ontology>
    '''.format(revision, source)

    body = ""

    mapFileDirForRevision = MAP_DIR + revision + "/"

    for file in sorted(os.listdir(mapFileDirForRevision)):
        if file.endswith(".map"):
            # Opening the file and split it by \n
            arq = open(mapFileDirForRevision + file);
            seq = arq.read().split("\n");

            line = 0;

            className = file.replace(".map", "");

            # if the second line begins with "ncit:", then that's the corresponding NCI thesaurus concept
            ncit_equivalent_to = "";
            m = re.compile("^ncit:\s*(.*)\s*$").match(seq[line]);
            if m:
                ncit_equivalent_to = "<owl:equivalentClass rdf:resource=\"&ncit;" + m.group(1) + "\"/>";
                line = line + 1;

            # Class Name Header
            body += '\n\n\t<!-- ' + className + ' -->'

            for axiom in seq[line:(len(seq))]:
                if ncit_equivalent_to:
                    body += '<owl:Class rdf:about="&cst;%s">%s</owl:Class> ' % (className, ncit_equivalent_to);
                if axiom != "":  # Do not print any empty lines
                    body += '''\n\t<owl:Class>
        <rdfs:subClassOf rdf:resource="&cst;%s" />
        <owl:intersectionOf rdf:parseType="Collection">''' % (className)
                    x = axiom.split(" ");
                    for tnm in x:
                        if tnm:
                            body += '\n\t\t\t<rdf:Description rdf:about="&cst;%s"/>' % (tnm)

                    body += '''\n\t\t</owl:intersectionOf>
        </owl:Class>'''

    body += ''
    body += '''</rdf:RDF>'''

    rdfXMLContent = header+body

    # Write the RDF/XML file
    fpXML = open(getFileName(revision),"w")
    fpXML.write(rdfXMLContent)
    fpXML.close()

    # Write the ttl file
    # We use the turtle parser
    # The parsers available: http://rdflib.readthedocs.io/en/stable/plugin_parsers.html
    g = Graph()
    g.parse(data=rdfXMLContent, format="xml")
    g.serialize(destination=getFileName(revision, "ttl"), format='turtle')


def main():
    """
    The main function.
    :return:
    """

    for revision in STAGING_REVISIONS:
        createOntology(revision)

if __name__ == '__main__':
    main()