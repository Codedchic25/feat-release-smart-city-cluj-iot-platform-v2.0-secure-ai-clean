# 📁 Galerie Operațională și Ingestii Vizuale (UI/UX)

Acest document listează structura modulelor și a capturilor de ecran verificate din producție care validează funcționalitatea platformei Smart City Cluj-Napoca.

### 🔒 Securitate Operațională și Panou Central

* **01. Autentificare Securizată Operator:** Punct de control bazat pe hashing **SHA-256** și verificare în timp constant (`hmac.compare_digest`) care protejează interfața din `main.py` utilizând credențialele izolate din fișierul `.env`.
* **02. Panou de Control Centralizat:** Afișarea KPI-urilor simetrice pentru parametrii monitorizați (Temperatură, Calitate Aer, Umiditate Sol, Zgomot, Trafic) în Dashboard.
* **03. Jurnal de Audit Industrial:** Jurnalizarea în timp real a datelor tranzacționale direct în tabela SQLite `city_stats` și logarea alertelor cu cooldown de 10 secunde în `security_alerts.log`.
* **04. Sincronizare Multi-Limbă:** Suport dinamic prin callback-uri legate de `st.session_state["lang"]` care utilizează serviciile publice furnizate de clasa `TranslationProvider` (RO, EN, IT, ES, HU).
* **05. Motor Geospațial Open-Source:** Maparea geospațială nativă a celor 5 stații IoT unice din Cluj-Napoca pe hărți interactive utilizând componenta **Folium**.
* **06. Panou de Administrare Sistem:** Zona din `Settings` cu slidere atomice pentru configurarea și actualizarea dinamică a pragurilor de alertare pe noduri în baza de date.

### 🔬 AI Aplicat și Prognoze Machine Learning (Llama Engine)

* **07. Urmărire Raționament LLM:** Recomandări administrative operaționale generate prin intermediul instanței active `openai/gpt-oss-20b` via `GroqProvider`.
* **08. Matrice de Corelație Statistică Pearson:** Heatmap-ul analitic din pagina `3_Analytics.py` identificând dependențele liniare dintre indicatorii urbani.
* **09. Grafice de Tendință în Serie Temporală:** Subplot-urile predictive Plotly din Dashboard randate complet cu formatarea stabilă modernă.
* **10. Predicție Liniară Temperatură:** Extrapolarea viitoare pe 5 intervale de timp calculată automat prin modelul `LinearRegression` sau polinoame NumPy.
* **11. Deviație Predictivă Trafic Rutier:** Prognoza indicilor de aglomerare auto utilizând calcule numerice prin NumPy polyfit.
* **12. Bariere AI Contextuale (Guardrails):** Securizarea completă a asistentului prin instrucțiunile imutabile din `prompts.txt`, asistată de eliminarea prin expresii regulate a tag-urilor de gândire internă `<think>...</think>`.
