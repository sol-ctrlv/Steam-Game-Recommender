from rdflib import Graph, Namespace
from collections import defaultdict

# Definisco il namespace utilizzato nella KB RDF
STEAM = Namespace("http://example.org/steam#")

def recommending(profile, played_ids, kb_path="kb/steam_kb.ttl"):
    """
    Genero raccomandazioni da una KB RDF basata su giochi simili a quelli che mi piacciono,
    usando query SPARQL. Il profilo include tag, generi, publisher e anni di uscita preferiti.
    """

    # Carico il grafo RDF
    g = Graph()
    g.parse(kb_path, format="turtle")

    # Funzione per trasformare un testo in una URI RDF valida
    def to_uri(value):
        return value.replace(" ", "_").replace("-", "_").replace("'", "").replace(",", "").replace("&", "and")

    # Creo la lista delle query SPARQL da eseguire
    query_templates = []

    # 1. Query sui tag preferiti
    for tag in profile.get("top_tags", []):
        uri = to_uri(tag)
        query_templates.append(f"""
        SELECT ?game WHERE {{
            ?game steam:hasTag <http://example.org/steam#{uri}> .
        }}
        """)

    # 2. Query sui generi preferiti
    for genre in profile.get("top_genres", []):
        uri = to_uri(genre)
        query_templates.append(f"""
        SELECT ?game WHERE {{
            ?game steam:hasGenre <http://example.org/steam#{uri}> .
        }}
        """)

    # 3. Query sui publisher preferiti
    for pub in profile.get("top_publishers", []):
        uri = to_uri(pub)
        query_templates.append(f"""
        SELECT ?game WHERE {{
            ?game steam:publishedBy <http://example.org/steam#{uri}> .
        }}
        """)

    # 4. Query per gli anni di uscita più frequenti
    for year in profile.get("top_years", []):
        query_templates.append(f"""
        SELECT ?game WHERE {{
            ?game steam:releaseDate "{year}" .
        }}
        """)

    # Inizializzo il dizionario dei risultati
    results = defaultdict(int)

    # Eseguo tutte le query SPARQL generate
    for query in query_templates:
        # Eseguo la query sul grafo g, con il prefisso steam
        res = g.query(query, initNs={"steam": STEAM})
        
        # Per ogni riga dei risultati della query
        for row in res:
            # Converto l'uri in una stringa
            game_uri = str(row[0])
            
            # Estraggo l'ID del gioco e se non si trova nei già giocati
            # incremento il suo score di 1
            game_id = game_uri.split("#")[-1]
            if game_id not in played_ids:
                results[game_id] += 1

    # Avviso in caso di nessun risultato trovato
    if not results:
        print("Nessuna raccomandazione trovata.")

    # Ordino i risultati per punteggio decrescente
    ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)

    # Ritorno la lista finale dei giochi raccomandati
    return [{"game_id": game_id, "score": score} for game_id, score in ranked]
