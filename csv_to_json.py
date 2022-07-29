import csv
import json
import pandas as pd

data_originlist=[]

csv = pd.read_csv('WineClassification.csv', sep=',', encoding = 'utf-8')
regions_df = csv[['doLabel','DO']].drop_duplicates()
regions_list = []
for region in regions_df.itertuples(index=False):
    data_origin = {'designationOfOrigin': region.__getattribute__('doLabel'),'iri': region.__getattribute__('DO')}     
    regionfilter = csv[csv['doLabel']==region.__getattribute__('doLabel')]
    winery_df = regionfilter[['wineryLabel','winery']].drop_duplicates()
    
    winerydictlist=[]
    for bodega in winery_df.itertuples(index=False):
        winerydict = {'name': bodega.__getattribute__('wineryLabel'),'iri': bodega.__getattribute__('winery')}
        wineryfilter = regionfilter[regionfilter['wineryLabel']==bodega.__getattribute__('wineryLabel')]
        wine_df = wineryfilter[['wineLabel','wine']].drop_duplicates()
        
        winedictlist=[]
        for wine in wine_df.itertuples(index=False):
            winedict = {'name': wine.__getattribute__('wineLabel'), 'iri': wine.__getattribute__('wine')}
            winefilter = wineryfilter[wineryfilter['wineLabel']==wine.__getattribute__('wineLabel')]
            color_df = winefilter[['colorLabel']].drop_duplicates()

            colordictlist=[]
            for color in color_df.itertuples(index=False):
                colordict = {'name': color.__getattribute__('colorLabel')}

            colordictlist.append(colordict)
            winedict['color']=colordictlist
            winedictlist.append(winedict)
        winerydict['wines']=winedictlist
        winerydictlist.append(winerydict)
    data_origin['wineries']= winerydictlist
    data_originlist.append(data_origin)

data = {'region': data_originlist}
with open('WineClassification.json', 'w', encoding='utf8') as json_file:
    json_file.write(json.dumps(data, indent=4, ensure_ascii=False))
    json_file.close()
