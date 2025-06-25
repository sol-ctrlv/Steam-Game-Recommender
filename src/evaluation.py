import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.preprocessing._label")

def evaluate_models(user_data_path, catalog_path, models_path):
    """
    Valuto modelli supervisionati salvati in models_path usando i dati utente e catalogo.
    """
    print("Valuto i modelli supervisionati...")

    # Carico i giochi dell'utente e il catalogo con tag e generi
    user_data = pd.read_csv(user_data_path)
    catalog = pd.read_csv(catalog_path)

    # Unisco i due dataset per associare tag e generi ai giochi giocati
    data = user_data.merge(catalog, on="game_id", how="left")
    
    # Converto le stringhe tipo "Action, RPG, Indie" in liste ["Action", "RPG", "Indie"]
    data["tag_list"] = data["tags"].fillna("").apply(lambda s: s.split(", "))
    data["genre_list"] = data["genres"].fillna("").apply(lambda s: s.split(", "))

    # Creo l'etichetta binaria "Piaciuto": 
    # 1 se il gioco è stato giocato per almeno 8 ore, altrimenti 0
    data["liked"] = (data["playtime_hours"] >= 8).astype(int)

    # Divido i giochi in training set e test set
    X = data[["tag_list", "genre_list"]]
    y = data["liked"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Carico i vettori binari salvati
    binary_tags = joblib.load(os.path.join(models_path, "binary_tags.pkl"))
    binary_genres = joblib.load(os.path.join(models_path, "binary_genres.pkl"))

    # Converto le liste di tag e generi in vettori binari 
    # sia per training che per test
    # es. ["Action", "Multiplayer"] → [1, 1, 0, 0, 0, ...]
    X_tags_train = binary_tags.transform(X_train["tag_list"])
    X_genres_train = binary_genres.transform(X_train["genre_list"])
    X_tags_test = binary_tags.transform(X_test["tag_list"])
    X_genres_test = binary_genres.transform(X_test["genre_list"])
    
    # Unisco i due vettori verticalmente sia per training che per test, 
    # rendendoli colonne in una matrice dove le righe sono i giochi 
    X_train_final = np.hstack([X_tags_train, X_genres_train])
    X_test_final = np.hstack([X_tags_test, X_genres_test])

    # Valuto ciascun modello salvato
    for model_name in ["NaiveBayes.pkl", "DecisionTree.pkl", "RandomForest.pkl", "LogisticRegression.pkl"]:

        # Carico il modello
        model = joblib.load(os.path.join(models_path, model_name))
        
        # Faccio la predizione sul training set
        y_pred = model.predict(X_test_final)
        print(f"\n{model_name.replace('.pkl','')}:")
        
        # Confronto le Y di test e predette
        print(classification_report(y_test, y_pred))


def predict_liked_games(model_path, catalog, played_ids):
    """
    Predico giochi potenzialmente piaciuti all'utente tra quelli non ancora giocati.
    """
    
    # Controllo se esiste il modello e lo carico
    if not os.path.exists(model_path):
        print(f"Modello {model_path} non trovato.")
        return

    model = joblib.load(model_path)

    # Carico i vettori binari salvati
    binary_tags = joblib.load(os.path.join(os.path.dirname(model_path), "binary_tags.pkl"))
    binary_genres = joblib.load(os.path.join(os.path.dirname(model_path), "binary_genres.pkl"))
    
    # Prendo i giochi nel catalogo che non sono tra i "giocati"
    not_played = catalog[~catalog["game_id"].isin(played_ids)].copy()
    
    # Converto le stringhe tipo "Action, RPG, Indie" in liste ["Action", "RPG", "Indie"]
    not_played["tag_list"] = not_played["tags"].fillna("").apply(lambda s: s.split(", "))
    not_played["genre_list"] = not_played["genres"].fillna("").apply(lambda s: s.split(", "))

    # Converto le liste di tag e generi in vettori binari
    # es. ["Action", "Multiplayer"] → [1, 1, 0, 0, 0, ...]
    X_tags = binary_tags.transform(not_played["tag_list"])
    X_genres = binary_genres.transform(not_played["genre_list"])
    
    # Unisco i due vettori verticalmente, rendendoli colonne in una matrice
    # dove le righe sono i giochi
    X_unseen = np.hstack([X_tags, X_genres])

    # Effettuo la predizione del modello
    predictions = model.predict(X_unseen)
    not_played["predicted"] = predictions

    # Prendo solo i giochi piaciuti "1" dalla predizione e stampo i primi 10
    liked = not_played[not_played["predicted"] == 1]
    print("\nGiochi raccomandati dal modello supervisionato:")
    print(liked[["game_id", "name"]].head(10).to_string(index=False))