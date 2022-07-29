import glob, re, time, logging, shutil, os, subprocess
import pandas as pd
from pandas import DataFrame
import rdflib
from rdflib.plugins.sparql.processor import SPARQLResult
import jellyfish
date = time.strftime("%Y-%m-%d")

def datasets_by_source():
    """
    Obtain the datasets by source
    """
    # Change to current day directory
    os.chdir(f'/home/mcaballero/Policy_Cloud/dataset/{date}/')
    fpattern = r'{}{}.csv'
    files = glob.glob(fpattern.format('*','*'))
    sources = sorted({re.split(r'(\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])).(\w+)', f.strip('dataset\\'))[0] for f in files})
    print('Crawler sources: ', sources)
    return {source: pd.concat((pd.read_csv(f) for f in glob.glob(fpattern.format(source, '*'))), ignore_index=True) for source in sources}

def clean_crawler_datasets(df):
    if "carrefour" in df:
        df['carrefour'].dropna(subset=['price'], inplace=True) # Drop rows with None price
        df['carrefour']['price'] = pd.to_numeric(df['carrefour']['price']).round(decimals = 2) # Cast to numeric + Round price to 2 decimals
        df['carrefour']['location'] = df['carrefour']['location'].astype(str).str.replace(r'(\d+(\.\d+)?[MCDNPF]?L(\s+\d+PK)?)', '') # Regex expression to parse bottle size from string (e.g. 750ML)
        
        # Clean DOs
        df['carrefour']['location'] = df['carrefour']['location'].astype(str).str.replace(r'D.O. ', '')
        df['carrefour']['location'] = df['carrefour']['location'].astype(str).str.replace(r' - 75 cl', '')
        df['carrefour']['location'] = df['carrefour']['location'].astype(str).str.replace(r'D.O.Ca. ', '')
        df['carrefour']['location'] = df['carrefour']['location'].astype(str).str.replace(r'D.O.C. ', '')
    if "vivino" in df:
        df['vivino'] = df['vivino'].drop_duplicates(subset=['id'], keep='first')
        df['vivino'].dropna(subset=['price'], inplace=True) # Drop rows with None price
        df['vivino']['price'] = pd.to_numeric(df['vivino']['price']).round(decimals = 2) # Cast to numeric + Round price to 2 decimals
        df['vivino']['location'] = df['vivino']['location'].astype(str)
        
        # Convert number to color (these numbers come from the API specification)
        df['vivino'].loc[df['vivino']['color']==1, 'color'] = 'Red'
        df['vivino'].loc[df['vivino']['color']==2, 'color'] = 'White'
        df['vivino'].loc[df['vivino']['color']==4, 'color'] = 'Rose'

    if "winemag" in df:
        df['winemag'] = df['winemag'].drop_duplicates(subset=['id'], keep='first')
        
        df['winemag'].dropna(subset=['price'], inplace=True) # Drop rows with None price
        df['winemag']['price'] = df['winemag']['price'].astype(str).str.replace(r'$', '')
        df['winemag']['price'] = pd.to_numeric(df['winemag']['price']).round(decimals = 2) # Cast to numeric + Round price to 2 decimals

        # Filter region
        df['winemag'] = df['winemag'][df['winemag']['location'].str.contains("Northern Spain")]   
        df['winemag']['location'] = df['winemag']['location'].astype(str).str.replace(r', Northern Spain, Spain', '')

        df['winemag']['alcohol_percentage'] = df['winemag']['alcohol_percentage'].astype(str).str.replace(r'%', '')
        
    return df

def df_to_list_of_dicts(ontology_query):
    """
    Convert pandas DataFrame into a list of dictionaries.
    """
    wines_ontology = ontology_query[['doLabel', 'wineLabel', 'wine']].to_dict('records')
    for index in wines_ontology: #Rename fields
        index['location'] = str(index.pop('doLabel'))
        index['name'] = str(index.pop('wineLabel'))
        index['url'] = str(index.pop('wine'))

    wines_crawler = crawler_merge[['location', 'name']].to_dict('records')
    wines_crawler = [dict(x, **{'index':i}) for (i, x) in enumerate(wines_crawler)] #Insert index number in the dictionary

    print('Size wines_ontology:', len(wines_ontology))
    print('Size wines_crawler:', len(wines_crawler))
    return wines_crawler, wines_ontology

def obtain_distance(str1, str2):
    try:
        return jellyfish.jaro_distance(str1, str2)
    except Exception:
        print('Error computing jaro distance')

def append_aux_list(x, i, location):
    try:
        return [{"name_crawler": x, "name_ontology": y['name'], "distance": obtain_distance(x, y['name']), "index": i, "url":y['url']} for y in location]
    except Exception:
        print('Error appending aux_list')

def categorize_do(wines):
    calatayud = []
    campoDeBorja = []
    carinena = []
    somontano = []

    for x in wines:
        # RegEx is case insensitive
        if re.search('Calatayud', x['location']):
            calatayud.append(x)
        elif re.search('Campo de Borja', x['location']):
            campoDeBorja.append(x)
        elif re.search('Cariñena', x['location']):
            carinena.append(x)
        elif re.search('Somontano', x['location']):
            somontano.append(x)
    return calatayud, campoDeBorja, carinena, somontano

def compute_distance(list_crawler, list_ontology, source):
    list_distance = []

    for x in list_crawler:
        max_aux_list = max(append_aux_list(x['name'], x['index'], list_ontology), key=lambda x:x['distance'])        
        list_distance.append(max_aux_list)
    
    print('Total matches found for', source, '-->', len(list_distance))
    return list_distance

def append_distances_to_df(crawler_merge):
    # Create new dataframe column matching list values according to index
    crawler_merge.loc[df_distance_calatayud['index'],'distance'] = df_distance_calatayud['distance'].tolist()
    crawler_merge.loc[df_distance_calatayud['index'],'name_ontology'] = df_distance_calatayud['name_ontology'].tolist()
    crawler_merge.loc[df_distance_calatayud['index'],'url'] = df_distance_calatayud['url'].tolist()

    crawler_merge.loc[df_distance_campoDeBorja['index'],'distance'] = df_distance_campoDeBorja['distance'].tolist()
    crawler_merge.loc[df_distance_campoDeBorja['index'],'name_ontology'] = df_distance_campoDeBorja['name_ontology'].tolist()
    crawler_merge.loc[df_distance_campoDeBorja['index'],'url'] = df_distance_campoDeBorja['url'].tolist()

    crawler_merge.loc[df_distance_carinena['index'],'distance'] = df_distance_carinena['distance'].tolist()
    crawler_merge.loc[df_distance_carinena['index'],'name_ontology'] = df_distance_carinena['name_ontology'].tolist()
    crawler_merge.loc[df_distance_carinena['index'],'url'] = df_distance_carinena['url'].tolist()

    crawler_merge.loc[df_distance_somontano['index'],'distance'] = df_distance_somontano['distance'].tolist()
    crawler_merge.loc[df_distance_somontano['index'],'name_ontology'] = df_distance_somontano['name_ontology'].tolist()
    crawler_merge.loc[df_distance_somontano['index'],'url'] = df_distance_somontano['url'].tolist()
    return crawler_merge

if __name__ == "__main__":
    df = datasets_by_source() #Dictionary of dataframes
    print('DEBUG:::', subprocess.run(['pwd']))
    df = clean_crawler_datasets(df)
    crawler_merge = pd.concat(list(df.values()), ignore_index=True) # Dynamic dict size
    ontology_query = pd.read_csv("/home/mcaballero/Policy_Cloud/pro19_0470_src/NLP/ontology_query.csv")
    wines_crawler, wines_ontology = df_to_list_of_dicts(ontology_query) #List of dictionaries
    
    calatayud_crawler, campoDeBorja_crawler, carinena_crawler, somontano_crawler = categorize_do(wines_crawler)
    calatayud_ontology, campoDeBorja_ontology, carinena_ontology, somontano_ontology = categorize_do(wines_ontology)
    
    distance_calatayud = compute_distance(calatayud_crawler, calatayud_ontology, "Calatayud")
    distance_campoDeBorja = compute_distance(campoDeBorja_crawler, campoDeBorja_ontology, "Campo de Borja")
    distance_carinena = compute_distance(carinena_crawler, carinena_ontology, "Cariñena")
    distance_somontano = compute_distance(somontano_crawler, somontano_ontology, "Somontano")
    
    # From list to dataframe
    df_distance_calatayud = pd.DataFrame(distance_calatayud)
    df_distance_campoDeBorja = pd.DataFrame(distance_campoDeBorja)
    df_distance_carinena = pd.DataFrame(distance_carinena)
    df_distance_somontano = pd.DataFrame(distance_somontano)

    crawler_merge = append_distances_to_df(crawler_merge)
    crawler_merge.dropna(subset=['distance'], inplace=True) # Delete columns which are not of the four main Aragon´s DOs

    crawler_merge.to_csv(f'similar_wines{date}.csv', index=False, encoding='utf-8') #Save the dataframe
