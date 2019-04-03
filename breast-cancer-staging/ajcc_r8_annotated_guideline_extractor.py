#!/usr/bin/env python

"""
Automatically extract the AJCC 8th staging guidelines from the manual available at:
cancerstaging.org (you will need to sign-up first to download the chapter)
In order to use the following script, first the pdf manual has to be converted
to xml. For the pdf->xml conversion, you can use a software such as Adobe Acrobat DC Pro
or an online service.
"""
from bs4 import BeautifulSoup
from sets import Set
import re
import os, errno

__author__ = "Oshani Seneviratne"
__credits__ = ["Oshani Seneviratne"]
__license__ = "Apache"
__version__ = "2"
__maintainer__ = "Oshani Seneviratne"
__email__ = "senevo@rpi.edu"
__status__ = "Development"

PARSER = "html.parser"
AJCC_R8_RULES = "data/AJCC_R8_Rules.xml"
ANY = "Any"
MAP_FOLDER = "map/R8"
MAP_VAL_FOLDER = "map3/R8"

ABSOLUTE_VAL_FLAG = True   # ABSOLUTE_VAL_FLAG fetermines whether we output just the values for each of the biomarkers
                            # (i.e. 1, Positive, Negative etc) or the value attached to the biomarker type
                            # (Grade1, HER2_Pos, ER_Neg, etc)
POSSIBLE_T_VALUES = {0,1,2,3,4}
POSSIBLE_N_VALUES = {0,1,2,3}
POSSIBLE_M_VALUES = {0,1}
POSSIBLE_GRADE_VALUES = {1,2,3}
POSSIBLE_BIO_MARKER_VALUES = {"Negative" : "Neg", "Positive" : "Pos"}
TNM_PATTERN = re.compile('[Any]*\s*T[is]*[0-4]*[\*]*\s*[Any]*\s*N[0-3]*[mi]*[\*]*\s*[Any]*\s*M[0-1]*')
ACCEPTABLE_STAGES = Set([u'0', u'I', u'IA', u'IB', u'II', u'IIA', u'IIB', u'III', u'IIIA', u'IIIB', u'IIIC', u'IV'])

def correctTNMVal(tnmValue):
    """
    We assume that if there is no specific number attached to the TNM values, it is 'Any'.
    Thus, we remove the occurances of 'Any'.
    Asterisks appear in some of the TNM values for further explanations
    in the manual. We do not need those.
    Furthermore, rhe TNM Values should be separated by spaces, so add those if a space
    does not exist.

    :param tnmValue:
    :return: the corrected TNM Value
    """
    tnmRemovedAny = tnmValue.replace(ANY, "")
    tnmAsterisksReplaced = tnmRemovedAny.replace("*", "")
    tnmSplit = re.split('T|N|M', tnmAsterisksReplaced)
    tVal = tnmSplit[1]
    nVal = tnmSplit[2]
    mVal = tnmSplit[3]
    tnmSpaceCorrected = 'T=T' + tVal
    if ' ' not in tVal:
        tnmSpaceCorrected += ' '
    tnmSpaceCorrected += 'N=N' + nVal
    if ' ' not in nVal:
        tnmSpaceCorrected += ' '
    tnmSpaceCorrected += 'M=M' + mVal
    return tnmSpaceCorrected


def correctGrade(text):
    """
    This is to correct for an error introduced when converting the pdf to xml.
    The error is the inclusion of the watermark "FOR PERSONAL USE ONLY" in some
    of the data items. Upon close inspection of the data, we see that in most of
    the grade values an additional unwanted "SO" appearing from the watermark in
    the grade values.
    :param text:
    :return: corrected grade
    """
    text = text.replace(" ","")
    return text.replace("SO", "")


def correctHER2(text):
    """
    This is to correct for an error introduced when converting the pdf to xml.
    The error is the inclusion of the watermark "FOR PERSONAL USE ONLY" in some
    of the data items. Upon close inspection of the data, we see that in most of
    the HER2 values an additional unwanted "NAL" or "USE" appearing from the watermark in
    the grade values.
    :param text:
    :return: corrected HER2
    """
    text = text.replace(" ", "")
    text = text.replace("NAL", "")
    return text.replace("USE", "")


def correctER(text):
    """
    This is to correct for an error introduced when converting the pdf to xml.
    The error is the inclusion of the watermark "FOR PERSONAL USE ONLY" in some
    of the data items. Upon close inspection of the data, we see that in most of
    the ER values an additional unwanted "USE" appearing from the watermark in
    the grade values.
    :param text:
    :return: corrected ER
    """
    text = text.replace(" ", "")
    return text.replace("USE", "")

def correctPR(text):
    """
    Remove the trailing space in the PR avlues.
    :param text:
    :return: corrected PR
    """
    return text.replace(" ", "")


def getTNMCombinations(tnm):
    """
    Given the tnm string expand the rule set.
    There is no specific value for T, N, or M if the staging rule is applicable for any value of those biomarkers.
    :param tnm:
    :return: all the combinations of TNM with explicit values
    """
    tnmSplit = tnm.split(" ")
    tStr = tnmSplit[0]
    nStr = tnmSplit[1]
    mStr = tnmSplit[2]
    tnmCombinations = []

    if tStr == "T":
        if nStr == "N":
            if mStr == "M":
                for t in POSSIBLE_T_VALUES:
                    for n in POSSIBLE_N_VALUES:
                        for m in POSSIBLE_M_VALUES:
                            tnmCombinations.append("T%d N%d M%d" % (t, n, m))
            else:
                for t in POSSIBLE_T_VALUES:
                    for n in POSSIBLE_N_VALUES:
                        tnmCombinations.append("T%d N%d %s" % (t, n, mStr))
        else:
            for t in POSSIBLE_T_VALUES:
                tnmCombinations.append("T%d %s %s" % (t, nStr, mStr))
    else:
        tnmCombinations.append("%s %s %s" % (tStr, nStr, mStr))
    return tnmCombinations


def modifyIfNeededAndWrite(file, tnmCombination, grade, her2, er, pr):
    """
    Fix the biomarker values output in the map files based on the
    flag to either output the absolute value or not.
    :param file:
    :param tnmCombination:
    :param grade:
    :param her2:
    :param er:
    :param pr:
    :return:
    """
    #if not ABSOLUTE_VAL_FLAG:
    grade = "G=Grade" + str(grade)
    her2 = "H=HER2_" + POSSIBLE_BIO_MARKER_VALUES.get(her2)
    er = "E=ER_" + POSSIBLE_BIO_MARKER_VALUES.get(er)
    pr = "P=PR_" + POSSIBLE_BIO_MARKER_VALUES.get(pr)
    file.write("%s %s %s %s %s\n" % (tnmCombination, grade, her2, er, pr))


def writeToFiles(tnm, grade, her2, er, pr, stage):
    """
    Write to the map files corresponding to the stage.
    :param tnm:
    :param grade:
    :param her2:
    :param er:
    :param pr:
    :param stage:
    :return:
    """

    fileName = "%s/R8_Stage_%s.map" % (getMapFolder(), stage)

    f = open(fileName, "a")

    for tnmCombination in getTNMCombinations(tnm):
        if ANY in grade:
            if ANY in her2:
                if ANY in er:
                    if ANY in pr:
                        for g in POSSIBLE_GRADE_VALUES:
                            for h in POSSIBLE_BIO_MARKER_VALUES:
                                for e in POSSIBLE_BIO_MARKER_VALUES:
                                    for p in POSSIBLE_BIO_MARKER_VALUES:
                                        modifyIfNeededAndWrite(f,tnmCombination, g, h, e, p)
                    else:
                        for g in POSSIBLE_GRADE_VALUES:
                            for h in POSSIBLE_BIO_MARKER_VALUES:
                                for e in POSSIBLE_BIO_MARKER_VALUES:
                                    modifyIfNeededAndWrite(f, tnmCombination, g, h, e, pr)
                else:
                    for g in POSSIBLE_GRADE_VALUES:
                        for h in POSSIBLE_BIO_MARKER_VALUES:
                            modifyIfNeededAndWrite(f, tnmCombination, g, h, er, pr)
            else:
                for g in POSSIBLE_GRADE_VALUES:
                    modifyIfNeededAndWrite(f, tnmCombination, g, her2, er, pr)
        else:
            modifyIfNeededAndWrite(f, tnmCombination, grade, her2, er, pr)

    f.close()

def getMapFolder():
    """
    Depending on the type of output required, absolute values as opposed to values attached to the bio
    markers, return the correct map folder.
    :return:
    """
    if ABSOLUTE_VAL_FLAG:
        return MAP_VAL_FOLDER
    else:
        return MAP_FOLDER


def cleanMapFiles():
    """
    Delete the contents of the map folder.
    This step is needed since the values are appended to the files each time the script is run.
    :return:
    """
    mapFolder = getMapFolder()
    try:
        os.makedirs(mapFolder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    for theFile in os.listdir(mapFolder):
        filePath = os.path.join(mapFolder, theFile)
        try:
            if os.path.isfile(filePath):
                os.unlink(filePath)
        except Exception as e:
            print(e)


def main():
    """
    Main Function.
    :return:
    """
    with open(AJCC_R8_RULES) as fp:
        soup = BeautifulSoup(fp, PARSER)

    tables = soup.find_all('table')
    tableCount = 0
    ruleCounter = 0;

    for table in tables:
        # The data is available in multiple pages as seperate tables
        tableCount += 1
        print("\nProcessing table %d ..." % tableCount)

        tnms = []
        grade = her2 = er = pr = stage = None

        for tr in table.find_all('tr'):
            print('\tProcessing row %s:' % tr)

            headers = tr.find_all('th')

            if headers:
                for header in headers:
                    parsedTNM = TNM_PATTERN.findall(header.text)
                    if parsedTNM != None:
                        tnms = []
                        for tnmValue in parsedTNM:
                            tnms.append(correctTNMVal(tnmValue))
            rowData = tr.find_all('td')
            numData = len(rowData)
            if numData >= 2:
                stage = rowData[numData - 1].text.replace(" ", "")
                pr = correctER(rowData[numData - 2].text)
            if numData >= 3:
                er = correctER(rowData[numData - 3].text)
            if numData >= 4:
                her2 = correctHER2(rowData[numData - 4].text)
            if numData >= 5:
                grade = correctGrade(rowData[numData - 5].text)

            for tnm in tnms:
                if (grade != None and her2 != None and er != None and pr != None and (
                        (stage != None) and (stage in ACCEPTABLE_STAGES))):
                    print("\t\tFound TNM=%s, Grade=%s, HER2=%s, ER=%s, PR=%s, Stage=%s" % (
                    tnm, grade, her2, er, pr, stage))
                    ruleCounter += 1
                    writeToFiles(tnm, grade, her2, er, pr, stage)

    print("Processed %d staging rules from the AJCC manual." % ruleCounter)

if __name__ == '__main__':
    cleanMapFiles()
    main()