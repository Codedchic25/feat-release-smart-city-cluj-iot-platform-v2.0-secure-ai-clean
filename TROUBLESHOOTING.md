# 🛠️ Ghid de Depanare Tehnică (Troubleshooting): Smart City Cluj IoT Core

Acest document centralizează erorile operaționale comune, blocajele de infrastructură și procedurile formale de recuperare a platformei în medii locale și containerizate.

---

## 1. Blocaje la Nivelul Stratului de Persistență (SQLite Engine)

### 🚨 Eroare: `sqlite3.OperationalError: database is locked` sau blocaj `EBUSY` pe Windows
* **Cauza:** Procese Python fantomă rulând în fundal rețin descriptorul de fișier deschis asupra bazei de date `app.db`, împiedicând execuția scriptului `seed_db.py` sau aplicarea migrărilor Alembic.
* **Rezolvare (PowerShell sub Windows):** Pentru a elibera forțat resursa blocată de sistemul de operare, executați în terminal:
  ```powershell
  Stop-Process -Name "python" -Force
  ```
  Ulterior, re-inițializați contextul relațional prin:
  ```bash
  uv run python seed_db.py
  ```

### 🚨 Eroare: `No sensors registered inside the local relational database ledger schema`
* **Cauza:** Platformele efemere de tip Streamlit Cloud pornesc adesea cu o instanță nouă și complet goală a bazei de date `app.db`, generând avertismente portocalii în interfață din cauza lipsei nodurilor.
* **Rezolvare în cod (Automatizată):** Platforma include acum un mecanism de **Auto-Seeding programatic** în faza de bootstrap (`CityRepository.initialize_database`). Dacă interogarea bazei de date returnează `0` noduri active, aplicația invocă în mod automat subprocesul `seed_db.py`. Nu este necesară nicio intervenție manuală în cloud.

---

## 2. Eșecuri de Autentificare și Conflicte Criptografice

### 🚨 Problemă: Operatorul primește `Invalid credentials token` deși parola este corectă
* **Cauza:** Fișierul local `.env` conține o parolă stocată în text clar sau sub forma unui algoritm învechit (ex. hash MD5), în timp ce motorul securizat din `main.py` solicită o semnătură digitală hexazecimală modernă.
* **Rezolvare:**
  1. Generați hash-ul corect pentru parola dumneavoastră utilizând algoritmul **SHA-256**.
  2. Deschideți fișierul `.env` și asigurați-vă că variabila `PLATFORM_ADMIN_PASS` este populată exclusiv cu amprenta hexazecimală rezultată pe 64 de caractere.
  3. Sistemul validează acreditările prin `hmac.compare_digest` în timp constant pentru a anula atacurile cibernetice de tip timing side-channel.

---

## 3. Degradarea Serviciilor AI și Întreruperi de Rețea (Groq Cloud API)

### 🚨 Problemă: Bara laterală sau ferestrele de chat afișează mesaje de eroare text sau rate-limit
* **Cauza:** API-ul extern Groq Cloud suferă o întrerupere temporară de rețea, timeout sau cheia `GROQ_API_KEY` furnizată în `.env` a expirat.
* **Mecanismul Fail-Safe (Comportament Garantat):** Aplicația încapsulează toate interogările către modelul generativ `openai/gpt-oss-20b` în blocuri defensive `try/except`. În cazul unei căderi externe, sistemul loghează eroarea asincron prin `LOGGER.error` și afișează un avertisment controlat în UI.
* **Impact:** Restul platformei rămâne **100% funcțional și izolat local**. Colectarea telemetriei în SQLite, randarea matricilor Pearson cu NumPy, randarea graficelor Plotly și scrierea alertelor cu cooldown în `security_alerts.log` continuă să ruleze neîntrerupt și complet offline.

---

## 4. Desincronizări în Testarea Automată și Rapoarte

### 🚨 Problemă: Fișierele JSON metrice din folderul `ai_tests/` nu apar sau sunt incomplete
* **Cauza:** Testele au fost rulate prin apeluri de fișiere izolate în loc să utilizeze configurarea globală centralizată a proiectului.
* **Rezolvare:** Rulați suita completă utilizând comanda simplă unificată:
  ```bash
  uv run pytest
  ```
  Această instrucțiune citește automat flag-urile din `pyproject.toml` și generează corect pe disc raportul unificat `ai_tests/pytest_report.json`, care va fi preluat fluid de panoul de control al calității din pagina `4_About.py`.
