import csv
import json
import pandas as pd

fields = []
regions_list = []

csvFilePath = 'WineClassification.csv'
csv = pd.read_csv(csvFilePath, sep=',') #encoding='latin-1'

print('Field names are: ' + ', '.join(fields))

regions_list = set(csv['doLabel'].tolist())

data_originlist=[]
for region in regions_list:
    data_origin = {'designationOfOrigin': region}
    regionfilter = csv[csv['doLabel']==region]
    winerylist = set(regionfilter['wineryLabel'])
    winerydictlist=[]

    for bodega in winerylist:
        winerydict = {'name': bodega}

        wineryfilter = regionfilter[regionfilter['wineryLabel']==bodega]
        winelist = set(wineryfilter['wineLabel'])
        winedictlist=[]

        for wine in winelist:
            winedict = {'name': wine}

            winefilter = wineryfilter[wineryfilter['wineLabel']==wine]
            colorlist = set(winefilter['colorLabel'])

            colordictlist=[]
            for color in colorlist:
                colordict = {'name': color}


                colordictlist.append(colordict)
            winedict['color']=colordictlist
            winedictlist.append(winedict)

        winerydict['wines']=winedictlist
        winerydictlist.append(winerydict)

    data_origin['wineries']= winerydictlist
    data_originlist.append(data_origin)

data = {'region': data_originlist}
print('DATA:::', data)

jsonFilePath = 'WineClassification_old.json'
with open(jsonFilePath, 'w') as jsonFile:
    jsonFile.write(json.dumps(data, indent=4))