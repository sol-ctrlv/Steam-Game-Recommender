# 🎮 Steam Game Recommender

Steam Game Recommender è un sistema ibrido per la raccomandazione personalizzata di videogiochi a partire dal profilo di un utente Steam.

Il progetto combina tecniche simboliche, basate su una base di conoscenza RDF interrogata tramite SPARQL, e tecniche di apprendimento supervisionato mediante modelli di classificazione, allo scopo di individuare giochi potenzialmente apprezzati ma non ancora giocati dall’utente.

---

## 🎯 Obiettivo

Fornire raccomandazioni personalizzate di giochi per un utente Steam, integrando approcci simbolici e supervisionati.

---

## ⚙️ Funzionalità

- 🔍 Estrazione automatica dei giochi giocati da un utente tramite Steam Web API (con fallback su cache locale)
- 🧾 Costruzione del profilo utente: tag, generi, publisher e anni più frequenti
- 📚 Raccomandazione simbolica: generazione dinamica di query SPARQL su una knowledge base RDF
- 🤖 Raccomandazione supervisionata: addestramento e applicazione di modelli ML (Random Forest, Logistic Regression, ecc.)
- 📈 Valutazione automatica dei modelli e predizione su giochi non giocati
- 💾 Salvataggio e riutilizzo di modelli e binarizzatori per garantire coerenza e modularità

---

## 📁 Struttura del progetto

```
Steam-Game-Recommender/
├── main.py                      # Script principale
├── data/
│   ├── steam_game_catalog.csv   # Catalogo dei giochi
|   └── steam_user_backup.csv    # Cache dei giochi dell’utente
├── kb/
│   └── steam_kb.ttl             # Base di conoscenza RDF
├── output/
│   └── models/                  # Modelli ML e encoder salvati
├── src/
│   ├── extract_user_profile.py  # Estrazione profilo utente
│   ├── recommend_games.py       # Raccomandazioni SPARQL
│   ├── models_trainer.py        # Addestramento modelli ML
│   ├── evaluation.py            # Valutazione e predizione supervisionata
```

---

## 🚀 Esecuzione

1. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

2. Imposta il tuo `STEAM_ID` nel file `main.py`

3. Avvia l'esecuzione:
```bash
python main.py
```

---

## 👤 Autore
Progetto sviluppato individualmente per il corso di **Ingegneria della Conoscenza**

**Nome:** Antonio Graziani  
**Matricola:** 738723  
**Email:** a.graziani2@studenti.uniba.it
