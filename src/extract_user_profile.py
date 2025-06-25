import requests
import pandas as pd

API_KEY = "BB7FD2D903DC194FE503CE91942870D3"

# Estrae i giochi dell'utente da Steam
def get_user_games(steam_id):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True
    }

    response = requests.get(url, params=params)

    # Ritorno l'errore della richiesta
    if not response.ok:
        print(f"Errore HTTP {response.status_code} - {response.reason}")
        return pd.DataFrame()

    # Provo a memorizzare il corpo della risposta
    try:
        data = response.json()
    except ValueError:
        print("Risposta non valida dalla Steam API.")
        print(f"Risposta: {response.text}")
        return pd.DataFrame()

    games = data.get("response", {}).get("games", [])

    # Controllo se presenta giochi
    if not games:
        print("Nessun gioco trovato per questo utente o profilo privato.")
        return pd.DataFrame()

    # Costruisco il dataframe
    game_id = []
    name = []
    playtime = []

    for g in games:
        game_id.append(g["appid"])
        name.append(g.get("name", "Unknown"))
        
        # Converto i minuti giocati in ore
        playtime.append(g["playtime_forever"] / 60)

    return pd.DataFrame({
        "game_id": game_id,
        "name": name,
        "playtime_hours": playtime
    })

# Costruisco il profilo dell'utente in base ai suoi giochi
def build_user_profile(user_games_df, catalog_df):
    
    """
    Estraggo un profilo utente basato su:
    - i tag più ricorrenti nei giochi che piacciono
    - i generi più frequenti
    - i publisher più comuni
    - gli anni di uscita più rappresentati
    - l'elenco degli ID dei giochi considerati "piaciuti"
    """
    
    # Memorizzo i giochi "piaciuti" (giocati almeno 8 ore)
    # ed estraggo i loro id
    liked_games = user_games_df[user_games_df["playtime_hours"] >= 8]
    liked_ids = liked_games["game_id"].tolist()
    
    # Faccio il join con i catalogo per aggiungere: generi, tag
    # publisher e data di rilascio 
    data_frame = liked_games.merge(catalog_df, on="game_id", how="left")

    # Definisco una funzione per gestire elementi multipli in una stringa come stringhe separate
    # Accedo alla colonna, elimino i valori nulli ed eseguo uno split su ", "
    # e con 'explode()' converto ogni elemento in una riga singola
    def explode_list_column(data_frame, column):
        return data_frame[column].dropna().apply(lambda x: x.split(", ")).explode()

    # Prendo i più frequenti tra: 5 tag, 3 generi 
    # 3 publisher e 4 anni di uscita
    # utilizzo la funzione dichiarata per contare più facilmente tag e generi
    top_tags = explode_list_column(data_frame, "tags").value_counts().head(5).index.tolist()
    top_genres = explode_list_column(data_frame, "genres").value_counts().head(3).index.tolist()
    top_publishers = data_frame["publisher"].dropna().value_counts().head(3).index.tolist()
    top_years = data_frame["release_date"].dropna().apply(lambda x: x[-4:]).value_counts().head(2).index.tolist()

    return {
        "top_tags": top_tags,
        "top_genres": top_genres,
        "top_publishers": top_publishers,
        "top_years": top_years,
        "liked_game_ids": liked_ids
    }