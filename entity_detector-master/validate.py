import sys
#Configurations
from configuration.config import TASKS
from configuration.config_json import Config
#Datasets
from data.conll import CoNLLDataset
#Models
from model.sequence_tagging.ner_model import NERModel
#Functions
from data.data_utils import process_line
import re
from apirest import evaluate,loadmodel
import json

def main():
    test_duck()

def comparewithmodel():
    loadmodel()
    # extractedtext,extractedentities=loadAncora()
    resultsCon = loadConllEsp()
    text = resultsCon["text"]
    results = evaluate(text.replace("(", ",").replace(")", ","), False, False, False)
    print(compare(resultsCon["entities"], results["entities"]))

def test_chatbot():
    text =  "y en Huesca\ny de Huesca\nQuien es el alcalde de Añon."
    #\n Quien es el alcalde de Bañon.\nQuien es el alcalde de Añón.\nQuien es el alcalde de Bañón.\nque es la Universidad de Zaragoza?.\nque superficie tiene la Diputación Provincial en Zaragoza"

    loadmodel()
    print(evaluate(text.replace("(", ",").replace(")", ","), True, True, False))


def test_duck():
    text ="E. A. H. J., Shaw & Co., una firma de Wall Street, y se trasladó a Seattle, donde comenzó a trabajar en un plan de negocios para lo que finalmente se convertiría en Amazon.com."

        #"¿En qué puntos kilométricos se encuentran los puentes de la autopista ARA-1"
    #"El valor bursátil de Amazon está próximo a los 460.000 millones de dólares, lo que le coloca como la cuarta más grande del índice S&P 500 entre Microsoft y Facebook"

    #    " Amazon.com,  jicalvo@ita.es 1 y dos dias en 1996 %,  $20,3  costo 50.500 $ y 200 euros y lo compraron 2000 libras en el ayuntamiento de Zaragoza: Teruel  y tres 6 7  8€ y 1000 dólar son las 14:00 del 6 de enero de 2019"

    loadmodel()
    print(evaluate(text.replace("(", ",").replace(")", ","), True, True, False))



def loadAncora():
    file = open("resources/fichero200NPAncora.txt", "r", encoding='utf8')

    line = file.read()

    # line="hola  <START:location> Madrid <END> , 22 may ( <START:organization> EFE <END> ) . El presidente de la <START:organization> Asociación Española de Hematología. Hemoterapia <END> , <START:person> Vicente García <END> , aseguró que  en <START:location> España <END> podemos contar con una sangre segura  , gracias a los test que se realizan , pero consideró que  la prueba mas segura es contar con donantes fieles. "

    labels = ["location", "organization", "person", "misc"]
    strend = "<END>"

    lencommon = len("<START:>")
    lenend = len("<END>")

    extractedtext = ""
    extractedentities = []

    currentPosition = 0
    startindex = 0

    textoffset = 0
    endtextoffset = 0
    exit = False
    while exit == False:
        exit = True
        indexend = line.find("<END>", currentPosition)
        if indexend >= 0:
            for label in labels:
                index = line.find("<START:" + label + ">", currentPosition, indexend)
                if index >= 0:
                    entity = {}
                    entity["start"]=0
                    lenlabel = lencommon + len(label)
                    text = line[index + lenlabel:indexend]
                    entity["entity"] = label
                    text2 = text.lstrip()
                    text3 = text.rstrip()
                    numspacesbefore = len(text) - len(text2)
                    numspacesafter = len(text) - len(text3)
                    entity["value"] = text.strip()
                    entity["start"] = len(extractedtext) + (index - currentPosition) + numspacesbefore
                    entity["end"] = entity["start"] + len(text) - numspacesafter - numspacesbefore
                    exit = False
                    extractedentities.append(entity)
                    extractedtext = extractedtext + line[currentPosition:index] + text
                    currentPosition = indexend + lenend
                    break
    extractedtext = extractedtext + line[currentPosition:]
    return extractedtext,extractedentities

def loadConllEsp():
    file = open("resources/ner/conll2002/esp.testb.txt", "r", encoding='utf8')
    words=[]
    preds=[]
    text=""
    for line in file:
        if line!="\n":
            parts= line.split(" ")
            words.append(parts[0])
            preds.append(parts[1].strip())
        else:
            words.append("\n")
            preds.append("")

    respuesta = {}
    entities = []
    wordIndex = 0
    startindex = 0
    currententity = {}
    currenttext = ""

    for pred in preds:
        #  print(wordIndex)
        t = words[wordIndex]
        wordIndex = wordIndex + 1

        if pred=="":
            if currententity != {} and currententity["entity"] != "other":
                currententity["start"] = 0
                currententity["value"] = currenttext
                startindex = text.find(currenttext, startindex)
                currententity["start"] = startindex
                currententity["end"] = startindex + len(currenttext)
                entities.append(currententity)
            currententity={}
            currenttext = ""
            text = text + t
            startindex=len(text)
        else:
            text = text + " " + t
            if pred.startswith("I"):
                currenttext = currenttext +" "+ t
            elif pred.startswith("B"):
                if currententity != {}:
                    if currententity["entity"] == "other":
                        currententity["start"] = 0
                        startindex = text.find(currenttext, startindex)
                        currententity["value"] = currenttext
                        currententity["start"] = startindex
                        currententity["end"] = startindex + len(currenttext)
                        startindex = currententity["end"]
                        #if other:
                        #     entities.append(currententity)
                    else:
                        currententity["start"] = 0
                        currententity["value"] = currenttext
                        startindex = text.find(currenttext, startindex)
                        currententity["start"] = startindex
                        currententity["end"] = startindex + len(currenttext)
                        startindex = currententity["end"]
                        entities.append(currententity)
                currententity = {}
                currenttext = t;
                currententity["start"] = 0
                if pred == "B-LOC":
                    currententity["entity"] = "location"
                elif pred == "B-ORG":
                    currententity["entity"] = "organization"
                elif pred == "B-PER":
                    currententity["entity"] = "person"
                elif pred == "B-MISC":
                    currententity["entity"] = "misc"
            else:
                if currententity != {} and currententity["entity"] != "other":
                    currententity["start"] = 0
                    currententity["value"] = currenttext
                    startindex = text.find(currenttext, startindex)
                    currententity["start"] = startindex
                    currententity["end"] = startindex + len(currenttext)
                    startindex = currententity["end"]
                    entities.append(currententity)
                    currententity = {}
                    currenttext = ""
                currententity["entity"] = "other"
                currenttext = currenttext +" "+ t

    if currententity != {}:
        currententity["start"] = 0
        currententity["value"] = currenttext
        startindex = text.find(currenttext, startindex)
        currententity["start"] = startindex
        currententity["end"] = startindex + len(currenttext)
        startindex = currententity["end"]
        if currententity["entity"] != "other":
            entities.append(currententity)

    respuesta["text"] = text;
    respuesta["entities"] = entities
    return respuesta



def compare(entities,detectedEntities):

    detectedEntitiesDict={}
    for detected in detectedEntities:
        detectedEntitiesDict[detected["start"]]=detected

    notfoundlist =[]
    founddistlist = []
    foundlenlist = []

    notfound=0
    found=0;
    founddist=0
    foundlen = 0
    for ent in entities:
        try:
            current=detectedEntitiesDict[ent["start"]]
            if current != None:
                if current["entity"]!=ent["entity"]:
                    founddistlist.append((ent,current))
                    founddist=founddist+1
                elif current["value"].strip()==ent["value"].strip():
                    found=found+1
                else:
                    foundlenlist.append((ent,current))
                    foundlen=foundlen+1
        except:
            if ent["entity"] == "organization":
                print(ent["value"])
            notfoundlist.append(ent)
            notfound=notfound+1
    result={}
    result["notfound"]=notfound
    result["found"]=found
    result["founddist"]=founddist
    result["foundlen"] = foundlen
    result["total"]=notfound+founddist+found+foundlen
    result["p_notfound"] = notfound/result["total"]
    result["p_found"] = found/result["total"]
    result["p_founddist"] = founddist/result["total"]
    result["P_foundlen"] = foundlen / result["total"]
    #result["notfoundlist"] =notfoundlist
    #result["founddistlist"] =founddistlist
    #result["foundlenlist"] = foundlenlist

    return result;

if __name__ == "__main__":
    main()
