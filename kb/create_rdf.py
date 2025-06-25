from rdflib import Graph, Namespace, URIRef, Literal, RDF
import pandas as pd
import urllib.parse

# Definisco una funziona per creare URI validi
def make_valid_uri(text):
    # Se è null, ritorno vuoto per evitare errori
    if pd.isnull(text):
        return ''
    
    # Rimpiazzo gli spazi con underscore
    text = text.replace(' ', '_')
    return urllib.parse.quote(text)

# Carico il catalogo dei giochi
games_df = pd.read_csv('data/steam_game_catalog.csv')

# Creo il grafo RDF
g = Graph()

# Definisco il namespace
EX = Namespace("http://example.org/steam#")

for index, row in games_df.iterrows():
    game_uri = URIRef(EX[str(row['game_id'])])

    # Aggiungo l'istanza del gioco
    g.add((game_uri, RDF.type, EX.Game))

    # Aggiungo il nome del gioco
    if pd.notnull(row['name']):
        g.add((game_uri, EX.name, Literal(row['name'])))

    # Aggiungo i generi del gioco
    if pd.notnull(row['genres']):
        genres = row['genres'].split(', ')
        for genre in genres:
            genre_uri = URIRef(EX[make_valid_uri(genre)])
            g.add((genre_uri, RDF.type, EX.Genre))
            g.add((game_uri, EX.hasGenre, genre_uri))

    # Aggiungo gli sviluppatori
    if pd.notnull(row['developer']):
        developers = row['developer'].split(', ')
        for developer in developers:
            developer_uri = URIRef(EX[make_valid_uri(developer)])
            g.add((developer_uri, RDF.type, EX.Developer))
            g.add((game_uri, EX.developedBy, developer_uri))

    # Aggiungo i publisher
    if pd.notnull(row['publisher']):
        publishers = row['publisher'].split(', ')
        for publisher in publishers:
            publisher_uri = URIRef(EX[make_valid_uri(publisher)])
            g.add((publisher_uri, RDF.type, EX.Publisher))
            g.add((game_uri, EX.publishedBy, publisher_uri))

    # Aggiungo la data di rilascio
    if pd.notnull(row['release_date']):
        g.add((game_uri, EX.releaseDate, Literal(row['release_date'])))

    # Aggiungo i tag, se presenti
    if 'tags' in games_df.columns and pd.notnull(row['tags']):
        tags = row['tags'].split(', ')
        for tag in tags:
            tag_uri = URIRef(EX[make_valid_uri(tag)])
            g.add((tag_uri, RDF.type, EX.Tag))
            g.add((game_uri, EX.hasTag, tag_uri))

# Salvo il grafo in un file .ttl
g.serialize(destination='kb/steam_kb.ttl', format='turtle')
print("Ho salvato la Knowledge Base con i TAGS nel file steam_kb.ttl")
