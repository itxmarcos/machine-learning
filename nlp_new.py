import time, os, glob
import pandas as pd
import numpy as np
import jellyfish
from typing import List, Dict
from sklearn.metrics import classification_report

date = time.strftime("%Y-%m-%d")

def get_dataframes():
    all_filenames = list(glob.glob('test/*.csv')) # Use glob to match the pattern 'csv'
    return pd.concat([pd.read_csv(f) for f in all_filenames ]) # Combine all files in the list

def clean_datasets(df):
    df_carrefour = df.loc[df['source'] == "carrefour"]
    df_carrefour.dropna(subset=['price'], inplace=True) # Drop rows with None price
    df_carrefour['price'] = pd.to_numeric(df_carrefour['price']).round(decimals = 2) # Cast to numeric + Round price to 2 decimals
    df_carrefour['location'] = df_carrefour['location'].astype(str).str.replace(r'(\d+(\.\d+)?[MCDNPF]?L(\s+\d+PK)?)', '') # Regex expression to parse bottle size from string (e.g. 750ML)
    # Clean DOs
    df_carrefour['location'] = df_carrefour['location'].astype(str).str.replace(r'D.O. ', '')
    df_carrefour['location'] = df_carrefour['location'].astype(str).str.replace(r' - 75 cl', '')
    df_carrefour['location'] = df_carrefour['location'].astype(str).str.replace(r'D.O.Ca. ', '')
    df_carrefour['location'] = df_carrefour['location'].astype(str).str.replace(r'D.O.C. ', '')

    df_vivino = df.loc[df['source'] == "carrefour"]
    df_vivino = df_vivino.drop_duplicates(subset=['id'], keep='first')
    df_vivino.dropna(subset=['price'], inplace=True) # Drop rows with None price
    df_vivino['price'] = pd.to_numeric(df_vivino['price']).round(decimals = 2) # Cast to numeric + Round price to 2 decimals
    df_vivino['location'] = df_vivino['location'].astype(str)
    # Convert number to color (these numbers come from the API specification)
    df_vivino.loc[df_vivino['color']==1, 'color'] = 'Red'
    df_vivino.loc[df_vivino['color']==2, 'color'] = 'White'
    df_vivino.loc[df_vivino['color']==4, 'color'] = 'Rose'

    df_winemag = df.loc[df['source'] == "carrefour"]
    df_winemag = df_winemag.drop_duplicates(subset=['id'], keep='first')
    df_winemag.dropna(subset=['price'], inplace=True) # Drop rows with None price
    df_winemag['price'] = df_winemag['price'].astype(str).str.replace(r'$', '')
    df_winemag['price'] = pd.to_numeric(df_winemag['price']).round(decimals = 2) # Cast to numeric + Round price to 2 decimals
    # Filter region
    df_winemag = df_winemag[df_winemag['location'].str.contains("Northern Spain")]   
    df_winemag['location'] = df_winemag['location'].astype(str).str.replace(r', Northern Spain, Spain', '')
    df_winemag['alcohol_percentage'] = df_winemag['alcohol_percentage'].astype(str).str.replace(r'%', '')
    return df

def df_to_list_of_dicts(ontology_query, crawler_merge) -> List[Dict]:
    wines_ontology = ontology_query[['doLabel', 'wineLabel', 'wineryLabel', 'wine']].to_dict('records') # Convert dataframe to list of dictionaries
    for index in wines_ontology: # Rename fields
        index['doLabel'] = str(index.pop('doLabel'))
        index['wineLabel'] = str(index.pop('wineLabel'))
        index['wineryLabel'] = str(index.pop('wineryLabel'))
        index['wineUrl'] = str(index.pop('wine'))

    wines_crawler = crawler_merge[['location', 'winery', 'name']].to_dict('records') # Convert dataframe to list of dictionaries
    wines_crawler = [dict(x, **{'index':i}) for (i, x) in enumerate(wines_crawler)] # Insert index number in the dictionary

    print('Size wines_ontology:', len(wines_ontology))
    print('Size wines_crawler:', len(wines_crawler))
    return wines_crawler, wines_ontology

def categorize_winery(wines) -> List:
    wineries_aux = list({v['wineryLabel']:v for v in wines}.values()) # List of unique dictionaries
    print('Size wineries_ontology:', len(wineries_aux))
    return [i['wineryLabel'] for i in wineries_aux]

def categorize_wines(wineries_list, wines_list_of_dicts): #-> Dictionary:
    valuesList = []
    for key in wineries_list:
        valuesListAux = []
        for value in wines_list_of_dicts:
            if key not in value['wineryLabel']:
                pass
            else:
                valuesListAux.append(value['wineLabel'])
        valuesList.append(valuesListAux)
    return dict(zip(wineries_list, valuesList)) #Wines of wineries dict of lists

def obtain_jaro_distance(str1, str2):
    try:
        return jellyfish.jaro_distance(str1, str2)
    except Exception as e:
        print('Error computing jaro distance', e)
    
# Puedo hacer a la vez buscar bodega + buscar vino
def compute_distance_winery(wineries_ontology, crawler_merge):
    with open('wineries.txt', 'w') as f:
        new_col = []
        black_list = set()
        for index, row in crawler_merge.iterrows():
            aux_dist = []
            for winery_ontology in wineries_ontology:
                aux_dist.append({"index": index, "winery": row['winery'], "winery_ontology": winery_ontology, "distance": obtain_jaro_distance(winery_ontology, row['winery'])})
            maxDistItem = max(aux_dist, key=lambda x:x['distance']) # Get the max distance
            if(maxDistItem['distance'] > 0.9):
                # f.write(f"{maxDistItem['winery']} ----- {maxDistItem['winery_ontology']}\n")
                # print(maxDistItem['winery'], '-----', maxDistItem['winery_ontology'])
                new_col.append({'index': index, 'winery': maxDistItem['winery'], 'winery_ontology': maxDistItem['winery_ontology']})
            else:
                black_list.add(maxDistItem['winery'])
        f.write(str(black_list))
        return new_col

def compute_distance_wine(wines_ontology_dictOfLists, crawler_merge):
    new_col = []
    for index, row in crawler_merge.iterrows():
        aux_dist = []
        if isinstance(row['winery_ontology'], str):
            for wine in wines_ontology_dictOfLists[row['winery_ontology']]:
                aux_dist.append({"index": index, "wine": row['name'], "wine_ontology": wine, "distance": obtain_jaro_distance(wine, row['name'])})
            maxDistItem = max(aux_dist, key=lambda x:x['distance']) # Get the max distance
            if(maxDistItem['distance'] > 0.8):
                # print(maxDistItem['name'], '-----', maxDistItem['wine_ontology'])
                new_col.append({'index': index, 'wine': maxDistItem['wine'], 'wine_ontology': maxDistItem['wine_ontology']})
    return new_col

def test(crawler_merge):
    test_crawler = ["Aquilon Garnacha 2016", "Alto Moncayo 2014 Aquilon Garnacha (Campo de Borja)", "Alto Moncayo 2014 Garnacha (Campo de Borja)", "Atteca Tinto Joven", "Batán de Salas 2015 Chardonnay (Somontano)", "Colección Pago Los Canteras Syrah Somontano 2018", "Bodega Otto Bestué 2015 Bestué de Otto Bestué Chardonnay (Somontano)", "Bodegas Añadas 2006 Care Crianza Tempranillo-Merlot (Cariñena)", "Bodegas Aragonesas 2019 Coto de Hayas Verdejo (Campo de Borja)", "Bodegas Paniza 2016 Garnacha Rosé (Cariñena)", 
    "Bodegas Pirineos 2003 Marboré Red (Somontano)", "Bodegas Virgen del Águila 2004 Señorío del Águila Reserva Red (Cariñena)", "Tres Picos Garnacha 2019", "Tres Picos Garnacha 2018", "Borsao 2012 Viura (Campo de Borja)", "Castillo de Maluenda 2011 Punto y Coma Viñas Viejas Garnacha (Calatayud)", "Don Ramón 2002 Tinto Red (Campo de Borja)", "El Escocés Volante 2007 El Puño Unfiltered Red Wine Red (Calatayud)", "El Pensador 2010 Tempranillo (Campo de Borja)", "Reserva Cabernet Sauvignon 2013", 
    "Enate 2009 Crianza Red (Somontano)", "Cabernet 2013", "Figaro 2015 Tinto Niño Jesús Garnacha (Calatayud)", "Grandes Vinos y Viñedos 2005 Corona d'Aragón Reserva Red (Cariñena)", "Ignacio Marín 2009 Gran Reserva Castillo de Tornos Red (Cariñena)", "Laus Tinto", "Las Valles 2014 Viura-Chardonnay (Cariñena)", "Marques de la Musa 2011 Garnacha (Cariñena)", "Montevicor 2008 Centenaria Garnacha (Calatayud)", "Olvena 2007 Chardonnay (Somontano)", 
    "Pago Aylés 2012 Aldeya Garnacha (Cariñena)", "3 de Tres Mil 2016", "Pagos del Moncayo 2013 PdM Moncayo Garnacha-Syrah (Campo de Borja)", "Pagos Familia Langa 2012 Real de Aragón Garnacha (Calatayud)", "Bodegas Paniza 2018 Viñas de Paniza Oak Aged Chardonnay (Cariñena)", "Quo 2007 Old Vines Grenache (Campo de Borja)", "Tres Ojos 2009 Macabeo (Calatayud)", "Tres Ojos 2012 Rosado (Calatayud)", "Viñas del Vero 2009 La Miranda de Secastilla Garnacha Blanca Grenache Blanc (Somontano)", "Viñas del Vero 2010 Gewürztraminer (Somontano)"]
    test_ontology_true = ["Aquilon", "Aquilon", "Alto Moncayo", "Atteca Tinto Joven 2018", "Batán de Salas Chardonnay", "", "", "", "Coto de Hayas Verdejo", "Fabula de Paniza Garnacha Rosado", 
    "Marbore Cuvee", "", "Borsao tres picos", "Borsao tres picos", "", "", "", "", "", "", 
    "", "Enate Crianza", "Enate Cabernet-Cabernet", "", "Corona de Aragon Reserva", "", "Laus Tinto Joven", "", "", "", 
    "", "", "3 de Tresmil", "Prados Coleccion Garnacha", "", "Viñas de Paniza Syrah", "", "", "", ""]
    test_ontology_pred = []

    for x in test_crawler:
        y = crawler_merge.loc[crawler_merge['name'].str.contains(x, case=False, regex=False)]
        if(len(y['wine_ontology'])>1):
            test_ontology_pred.append(y['wine_ontology'].iloc[0])
        elif(len(y['wine_ontology'])<1):
            test_ontology_pred.append("")
        else:
            test_ontology_pred.append(y['wine_ontology'].item())
    list_of_tuples = list(zip(test_crawler, test_ontology_true, test_ontology_pred)) # Get the list of tuples from three lists and merge them by using zip().
    test_df = pd.DataFrame(list_of_tuples, columns=['test_crawler', 'test_ontology_true', 'test_ontology_pred']) # Converting lists of tuples into pandas Dataframe.
    print(test_df)
    print(classification_report(test_ontology_true, test_ontology_pred))

if __name__ == "__main__":
    crawler_merge = get_dataframes()
    crawler_merge = clean_datasets(crawler_merge)

    ontology_query = pd.read_csv("/home/mcaballero/Policy_Cloud/pro19_0470_src/NLP/ontology_query.csv")
    wines_crawler, wines_ontology = df_to_list_of_dicts(ontology_query, crawler_merge)

    wineries_ontology_list = categorize_winery(wines_ontology)
    new_col_winery = compute_distance_winery(wineries_ontology_list, crawler_merge)
    crawler_merge["winery_ontology"] = np.nan # Create new empty column
    # Fill that col with the wineries from the ontology matching the same index
    for i in new_col_winery:
        crawler_merge.loc[crawler_merge.index[i['index']], 'winery_ontology'] = i['winery_ontology']

    wines_ontology_dictOfLists = categorize_wines(wineries_ontology_list, wines_ontology)
    new_col_wine = compute_distance_wine(wines_ontology_dictOfLists, crawler_merge)
    crawler_merge["wine_ontology"] = np.nan # Create new empty column
    # Fill that col with the wines from the ontology matching the same index
    for i in new_col_wine:
        crawler_merge.loc[crawler_merge.index[i['index']], 'wine_ontology'] = i['wine_ontology']

    # test(crawler_merge)

    crawler_merge.to_excel("nlp_new.xlsx")