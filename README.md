# Frostline Esports V4

Kør med Python 3.10+: `pip install -r requirements.txt` og `python app.py`.
Åbn http://127.0.0.1:5000 . Ledelsespanel: http://127.0.0.1:5000/admin .
**Før offentliggørelse:** sæt miljøvariablerne `ADMIN_PASSWORD` (stærkt unikt kodeord) og `SECRET_KEY` (lang tilfældig værdi), brug HTTPS og persistent disk til SQLite databasen. Hosting skal understøtte Python-server; statisk HTML-hosting er ikke nok.

Ansøgninger lagres i SQLite på serveren. Tæller viser antal ansøgninger. Betaling markeres manuelt af ejeren efter kontrol i MobilePay Box 8620JJ; Box har ingen automatisk betalingsbekræftelse i denne løsning. Der opkræves ingen penge automatisk, og kortbetaling er ikke med. Hjemmesiden er ikke offentliggjort.
