import time, os, glob, pickle
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

def get_ontology_aux(ontology_query):
    # DF OF WINERIES + URL
    aux_wineries_df = ontology_query[['wineryLabel', 'winery']].copy()
    wineries_df = aux_wineries_df.drop_duplicates(subset=["wineryLabel"]) #Select distinct wineries
    
    # DICT OF WINES + URL FOR EACH WINERY
    wines_dict = {}
    for index, row in wineries_df.iterrows():
        key = row['wineryLabel'] #key
        df_value = ontology_query.query("wineryLabel == @key")[['wineLabel', 'wine']] #value
        wines_dict[key] = df_value
    
    return wineries_df, wines_dict

def obtain_jaro_distance(str1, str2):
    try:
        return jellyfish.jaro_distance(str1, str2)
    except Exception as e:
        print('Error computing jaro distance', e)

# def normalize_winery(name, wineries_df):
#     for index, row in wineries_df.iterrows():
#         match = ontology_query.query("wineryLabel == @key")[['wineLabel', 'wine']] #value

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

def normalize_winery(winery_name):
        matches_winery = []
        for index2, row2 in wineries_df.iterrows():
            distance_winery = obtain_jaro_distance(winery_name, row2['wineryLabel'])
            match_winery = {"winery_name": winery_name, "row2": row2, "distance_winery": distance_winery} #"row": row,
            matches_winery.append(match_winery)
        bestMatchWinery = max(matches_winery, key=lambda x:x['distance_winery']) # Get the max distance_winery
        if(bestMatchWinery['distance_winery']>0.8):
            # print(str(index), '---', bestMatchWinery["row"]["winery"], '---', bestMatchWinery["distance_winery"], '---', bestMatchWinery["row2"]["wineryLabel"])
            return [bestMatchWinery["row2"]["wineryLabel"], bestMatchWinery["row2"]["winery"]]
        else:
            # black_list.append(bestMatchWinery["winery_name"])
            return ["Not found", "Not found"]

def normalize_wine(wine_name, winery_name):
    if winery_name == "Not found":
        return ["Not found", "Not found"]
    wines_df = wines_dict[winery_name] #Filter wines dataframe by winery
    matches_wine = []
    for index3, row3 in wines_df.iterrows():
        distance_wine = obtain_jaro_distance(wine_name, row3['wineLabel'])
        match_wine = {"row3": row3, "distance_wine": distance_wine} #"row": row,
        matches_wine.append(match_wine)
    bestMatchWine = max(matches_wine, key=lambda x:x['distance_wine']) # Get the max distance_wine
    if(bestMatchWine['distance_wine']>0.8):
        # print(str(index), '---', bestMatchWine["row"]["name"], '---', bestMatchWine["distance_wine"], '---', bestMatchWine["row3"]["wineLabel"])
        return bestMatchWine["row3"]["wineLabel"], bestMatchWine["row3"]["wine"]
    else:
        return ["Not found", "Not found"]

def normalize_winery_apply(row):
    return normalize_winery(row['winery'])

def normalize_wine_apply(row):
    winery_name = row['name_winery_ontology']
    wine_name = row['name']
    return normalize_wine(wine_name, winery_name)

# crawler_merge = get_dataframes()
# crawler_merge = clean_datasets(crawler_merge)
ontology_query = pd.read_csv("/home/mcaballero/Policy_Cloud/pro19_0470_src/NLP/ontology_query.csv")
wineries_df, wines_dict = get_ontology_aux(ontology_query)
# wineries_df.to_pickle("wineries_df.pkl") # Serialize dataframe
# with open("wines_dict.pkl", "wb") as wines_pkl:
#     pickle.dump(wines_dict, wines_pkl) # Serialize dictionary

# CREATE NEW COLUMNS winery_ontology and wine_ontology
# for index, row in crawler_merge.iterrows():
#     normalized_winery = normalize_winery(row['winery']) #normalized_winery_name, normalized_winery_url
#     if (normalized_winery is not None): # If the winery is found in the ontology
#         wines_df = wines_dict[normalized_winery[0]] #Filter wines dataframe by winery
#         normalized_wine = normalize_wine(row['name']) #normalized_wine_name, normalized_wine_url
#         if (normalized_wine is not None): # If the wine is found in the ontology
#             print(normalized_winery[0], normalized_wine[0])

black_list = []

if __name__ == "__main__":
    df = get_dataframes()
    df = clean_datasets(df)

    df[['name_winery_ontology', 'url_winery_ontology']] = df.apply(normalize_winery_apply, axis=1, result_type='expand')
    df[['name_wine_ontology', 'url_wine_ontology']] = df.apply(normalize_wine_apply, axis=1, result_type='expand')

    # black_list_set = set(black_list)
    # with open('lista_negra.txt', 'w') as f:
    #     f.write(str(black_list_set))

    # df.to_excel("map-apply.xlsx")

# test(crawler_merge)
