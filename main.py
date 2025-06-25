from src.extract_user_profile import get_user_games, build_user_profile
from src.recommend_games import recommending
from src.evaluation import evaluate_models, predict_liked_games
from src.models_trainer import train_models
import pandas as pd
import os

# Variabili costanti
STEAM_ID = "76561198361352402" # Inserire il proprio SteamID per predizioni personalizzate
CATALOG_PATH = "data/steam_game_catalog.csv"
USER_DATA_PATH = "data/steam_user_backup.csv"
KB_PATH = "kb/steam_kb.ttl"
OUTPUT_PATH = "output/raccomandazioni.csv"
MODELS_DIR = "output/models/"

# Estraggo i giochi dell'utente
print("Scarico giochi utente da Steam API...")
try:
    # Provo a connettermi al profilo utente 
    user_games = get_user_games(STEAM_ID)
    if user_games.empty:
        raise Exception()
    
    # Salvo i giochi dell'utente in un csv
    user_games.to_csv(USER_DATA_PATH, index=False)
except:
    # Nel caso la connessione non vada a buon fine, uso la cache locale
    print("Uso la cache locale per i giochi utente.")
    user_games = pd.read_csv(USER_DATA_PATH)

# Carico il catalogo giochi
catalog = pd.read_csv(CATALOG_PATH)

# Costruisco il profilo dell'utente e prendo i giochi da lui giocati
print("Costruisco profilo utente...")
profile = build_user_profile(user_games, catalog)
played_ids = user_games["game_id"].tolist()

# Raccomando giochi usando la KB RDF
print("Genero raccomandazioni dalla KB RDF...")
recomm = recommending(profile, played_ids, kb_path=KB_PATH)

# Costruisco un DataFrame con le prime 15 raccomandazioni
recommendation = pd.DataFrame(recomm[:15])
if recommendation.empty:
    print("Nessuna raccomandazione trovata.")
    exit()

# Converto "game_id" da stringa ad intero e faccio il join con il catalogo per ricavare: nome, tag e generi
recommendation["game_id"] = recommendation["game_id"].astype(int)
recommendation = recommendation.merge(catalog[["game_id", "name", "genres", "tags"]], on="game_id", how="left")

# Salvo le raccomandazioni
os.makedirs("output", exist_ok=True)
recommendation.to_csv(OUTPUT_PATH, index=False)

print("\nTop giochi consigliati:")
for _, row in recommendation.iterrows():
    print(f"- {row['name']} (score: {row['score']})")

# Addestro e valuto i modelli supervisionati
train_models(USER_DATA_PATH, CATALOG_PATH, MODELS_DIR)
evaluate_models(USER_DATA_PATH, CATALOG_PATH, MODELS_DIR)

# Raccomando giochi tramite modello supervisionato (RandomForest)
model_path = os.path.join(MODELS_DIR, "RandomForest.pkl")
predict_liked_games(model_path, catalog, played_ids)