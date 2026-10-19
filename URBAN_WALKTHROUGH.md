# 🏙️ Ghid de Parcurgere și Validare Interactivă (Urban Walkthrough)

Acest document însoțește evaluatorul, comisia de examinare sau recruiterul pas cu pas prin toate modulele platformei **Smart City Cluj-Napoca IoT Core**, demonstrând funcționalitatea end-to-end și deciziile tehnice luate.

---

## 🛠️ Pasul 1: Bootspaces și Inițializarea Deterministă a Datelor

Înainte de a lansa interfața grafică, trebuie să generăm structura relațională locală și să inserăm markerii geospațiali pentru cele 5 stații de monitorizare din Cluj-Napoca (Mărăști, Gheorgheni, Zorilor, Mănăștur, Piața Unirii).

1. Deschideți un terminal în rădăcina proiectului: `cluj-smartcity-iot-core`
2. Executați scriptul de seed tranzacțional utilizând managerul rapid `uv`:
   ```bash
   uv run seed_db.py
   ```
3. Pentru a verifica integritatea structurală a tabelelor SQLite create (`city_stats`, `sensors`, `settings`), puteți rula utilitarul de diagnoză local securizat:
   ```bash
   uv run python check_db.py
   ```

---

## 🔒 Pasul 2: Autentificarea Securizată a Operatorului

1. Porniți serverul local Streamlit utilizând orchestrarea de mare viteză:
   ```bash
   uv run streamlit run main.py
   ```
2. Accesați adresa indicată în browser (`http://localhost:8501`).
3. Interfața va fi blocată instantaneu de ecranul securizat de login. Introduceți acreditările administrative configurate prin hash-ul securizat **SHA-256** în fișierul `.env`. Parola în text clar tastată de operator pentru teste locale este `cluj2026`. Sistemul folosește verificarea în timp constant (`hmac.compare_digest`) pentru a elimina atacurile cibernetice de tip timing side-channel și a anula parolele fixe.

---

## 📡 Pasul 3: Monitorizarea Live și Logica de Alertare (Dashboard)

1. Navigați la pagina **`1_Dashboard.py`**. Veți observa coloanele simetrice de KPI-uri telemetrice live și harta nativă open-source Folium. Calitatea aerului este randată corect în unitatea academică corectă **`µg/m³`**.
2. Schimbați limba platformei din selectorul global din sidebar. Callback-ul global va propaga instantaneu pachetul lingvistic furnizat public de clasa `TranslationProvider` în toate limbile suportate (RO, EN, IT, ES, HU), rulând curat componenta de localizare fără erori de tip `AttributeError`.
3. Pentru a simula o breșă critică de mediu, generatorul de stări va împinge o valoare ce depășește pragurile imutabile (ex: Calitatea Aerului PM2.5 > 80.0 sau Temperatură > 32.0°C).
4. **Validarea Scutului Anti-Flood:** În acel moment, o alertă roșie de tip banner va apărea pe ecran. Sistemul va executa o scriere igienizată împotriva atacurilor de tip log injection în jurnalul `security_alerts.log`, fiind protejat de bariera temporală de 10 secunde cooldown a clasei `AlertManager`.

---

## 🔬 Pasul 4: Evaluarea Predictivă și Inteligența Artificială (Analytics)

1. Navigați la pagina **`3_Analytics.py`**.
2. **Prognoza Clasic ML:** Selectați un parametru urban. Algoritmul de Regresie Liniară sau polinoamele NumPy Polyfit preiau istoricul din SQLite, calculează panta de creștere și generează pe graficul Plotly următoarele intervale predictive de tendință, eliminând blocajele de cache vizual.
3. **Operational Recommendation (Llama Engine):** În subsolul paginii, asistentul AI contextual este pregătit pentru interogare. La trimiterea unei cereri, funcția preia contextul dens din ultimele 5 linii de loguri, îl injectează în promptul din `ai_tests/prompts.txt`, iar modelul de producție stabil `openai/gpt-oss-20b` generează o recomandare administrativă personalizată. Răspunsul curățat regex de tag-urile `<think>` este stocat securizat în `st.session_state` pentru a rezista ciclului de auto-refresh al interfeței.

---

## 🧪 Pasul 5: Validarea DevOps și MLOps (Suita de Teste)

Pentru a demonstra reziliența aplicației în medii de integrare continuă (CI/CD) înainte de deployment-ul final, rulați manual suita de teste automate pentru a compila rapoartele JSON metrice în folderul `ai_tests/`:

1. **Testarea Unitară și de Regresie (Pytest):**
   ```bash
   uv run pytest
   ```
   Această comandă validează izolarea completă a tranzacțiilor, integritatea traducerilor și comportamentul inegalităților stricte matematice, returnând scorul impecabil de **9 passed** și scriind jurnalul structural `ai_tests/pytest_report.json`.
2. **Evaluarea Programatică Python:**
   ```bash
   uv run python ai_tests/run_llm_eval.py
   ```
   Această comandă pornește execuția celor 5 scenarii din Cluj-Napoca, certificând o conformitate semantică de 100% a asistentului AI, stocată pe disc în `llm_eval_report.json`.
