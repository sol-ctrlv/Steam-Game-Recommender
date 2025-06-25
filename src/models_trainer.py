# Script per addestrare e salvare modelli supervisionati 
# per classificare i giochi come "Piace" o "Non Piace"

import pandas as pd
import numpy as np
import os
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import MultiLabelBinarizer

def train_models(user_data_path, catalog_path, models_dir):
    """
    Addestra i modelli supervisionati solo se non già presenti,
    o se il numero di feature non corrisponde ai dati attuali.
    """

    print("Addestro i modelli supervisionati...")

    # Creo la cartella dei modelli se non esiste
    os.makedirs(models_dir, exist_ok=True) 

    # Carico i dati dai rispettivi csv
    catalog_df = pd.read_csv(catalog_path)
    user_df = pd.read_csv(user_data_path)

    # Creo la nuova colonna "label" ed effettuo 
    # una etichettatura binaria dei giochi in:
    # - "Piace" (1) se il tempo di gioco è >= 8 ore;
    # - "Non Piace" (0) se il tempo di gioco è < 1 ora.
    # I giochi tra 1h e 8h vengono esclusi per evitare ambiguità
    user_df["label"] = user_df["playtime_hours"].apply(lambda h: 1 if h >= 8 else (0 if h < 1 else None))

    # Rimuovo i giochi senza etichetta definita
    user_df = user_df.dropna(subset=["label"])

    # Faccio il join con il catalogo per ottenere tag e generi
    data = user_df.merge(catalog_df, on="game_id", how="left")

    # Estraggo i tag e i generi, trasformandoli da stringa unica a lista di parole
    data["tag_list"] = data["tags"].fillna("").apply(lambda s: s.split(", "))
    data["genre_list"] = data["genres"].fillna("").apply(lambda s: s.split(", "))

    # Creo i vettori numerici binari per tag e generi
    binary_tags = MultiLabelBinarizer()
    binary_genres = MultiLabelBinarizer()

    # Trasformo le liste di tag e generi in vettori binari
    X_tags = binary_tags.fit_transform(data["tag_list"])
    X_genres = binary_genres.fit_transform(data["genre_list"])

    # Costruisco la matrice delle feature e del vettore target
    # Unisco orizzontalmente le due liste (tag e generi) in un unico array
    X = np.hstack([X_tags, X_genres])

    # Target binario di ciascun gioco (1 'Piace', 0 'Non piace')
    y = data["label"].astype(int)
    
    # Definisco i modelli supervisionati
    models = [
        ("DecisionTree", DecisionTreeClassifier(max_depth=5, class_weight='balanced', random_state=42)),
        ("RandomForest", RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)),
        ("LogisticRegression", LogisticRegression(max_iter=1000, class_weight='balanced')),
        ("NaiveBayes", BernoulliNB())
    ]

    # Addestramento, valutazione e salvataggio dei modelli
    for name, classifier in models:
        
        # Addestra il modello sul dataset
        classifier.fit(X, y)
        
        # Salvo il modello in formato .pkl
        joblib.dump(classifier, os.path.join(models_dir, f"{name}.pkl"))

    joblib.dump(binary_tags, os.path.join(models_dir, f"binary_tags.pkl"))
    joblib.dump(binary_genres, os.path.join(models_dir, f"binary_genres.pkl"))
    print("\n Tutti i modelli sono stati salvati in output/models/")