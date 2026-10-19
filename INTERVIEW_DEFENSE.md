# 🛡️ Ghid de Apărare a Proiectului (Interview Defense) — Smart City Cluj-Napoca

Acest ghid concentrează deciziile de design software, compromisurile arhitecturale (trade-offs)
și barierele defensive implementate în platformă. Este structurat pentru a răspunde întrebărilor
de nivel Senior/Architect în timpul fazelor de evaluare tehnică sau de examinare academică.

---

## 🗄️ 1. Persistență & Managementul Conexiunilor

### Întrebare: De ce ai ales SQLite pentru o aplicație de tip Smart City care simulează fluxuri continue de date IoT? SQLite nu are probleme la scrieri concurente?
* **Apărare**: Alegerea a fost dictată de cerințele de determinism, izolare locală și portabilitate
deplină ale unui proiect de portofoliu tehnic (zero-config, zero-infrastructure overhead pentru
utilizatorul sau recruiterul care clonează depozitul de cod în GitHub Codespaces sau local).
* **Justificare Tehnică**: Pentru a combate limitările native SQLite legate de blocarea bazei la
scrieri concurente (erori de tip `EBUSY`), am implementat trei straturi defensive:
  1. Conexiunile sincrone din clasa `CityRepository` folosesc un argument explicit de
  `timeout=5.0` în momentul deschiderii, prevenind crash-urile instantanee ale tranzacțiilor.
  2. Am configurat un mecanism de UPSERT atomic (`INSERT ... ON CONFLICT(sensor_id) DO UPDATE SET`)
  în interiorul `main.py` care execută modificările într-o singură tranzacție securizată.
  3. Suita de teste din `ai_tests/` rulează complet izolat prin `pytest`, validând logica de
  business și pragurile pe bază de simulare înainte de modificarea pe disc.
  4. **Nominal Row Mapping Fix:** Extragerea din SQLite utilizează exclusiv obiecte nominale de
  tip `sqlite3.Row` sau mapări de indecși securizați. Acest lucru decuplează interfața
  de ordinea coloanelor din baza de date, eliminând crash-urile specifice indexării oarbe.

---

## 🚨 2. Izolarea Serviciilor și Logica Anti-Flood Locală

### Întrebare: Ce se întâmplă dacă un senzor rămâne blocat peste pragul critic? Cum ai prevenit blocarea thread-ului principal și flood-ul de loguri?
* **Apărare**: Dependențele cloud externe introduc vulnerabilități de rețea, latențe mari I/O-bound
și costuri operaționale imprevizibile. Din acest motiv, am decuplat complet platforma de servicii
de mesagerie terțe, migrând întregul sistem către o jurnalizare de audit locală rapidă în fișierul
`security_alerts.log`.
* **Justificare Tehnică**: Pentru a preveni degradarea spațiului pe disc prin scrieri masive
repetitive în cazul în care un senzor defect transmite continuu anomalii, aplicația folosește o
barieră temporală stabilă. Atunci când pornesc simulările, scrierea istoricului pe cele 5 coloane de
senzori se execută controlat, fiind protejată de un cooldown strict de 10 secunde anti-spam în
`AlertProcessor`. Execuția interfeței utilizator Streamlit rulează independent de fluxul
tranzacțional de scriere. Serverul citește secvențial starea curentă din tabela SQLite și o
trimite direct către componentele UI, asigurând o latență de randare de zero milisecunde.

---

## 🧠 3. Evaluarea Deterministă a AI-ului Generativ Context-Aware

### Întrebare: Output-ul LLM-urilor este nedeterminist. Cum garantezi că recomandările asistentului AI sunt sigure, poliglote și corelate cu istoricul operațional?
* **Apărare**: În această platformă, componenta de Inteligență Artificială este tratată ca un
modul software clasic ce trebuie testat continuu prin metrici riguroase, nu ca o cutie neagră
probabilistică. Am transformat asistentul într-un analist urban Context-Aware capabil să
intercepteze atacurile cibernetice (Prompt Injection Defense).
* **Justificare Tehnică**:
  1. În `app/ai/ai_interface.py`, am configurat funcția asistentului să preia contextul dinamic
  al limbilor, accesând direct dicționarele compilate prin metoda publică `get_all_translations()`
  din `translations.py` (RO, EN, IT, ES, HU).
  2. Enunțul din `app/ai/groq_provider.py` integrează modelul stabil de producție `gpt-oss-20b`
  prin intermediul API-ului cloud Groq, configurat cu o temperatură joasă (0.2), forțând
  răspunsuri deterministe, axate pe acțiune tehnică.
  3. **Mitigarea Groq Rate Limit (429):** Am implementat un algoritm defensiv bazat pe
  Exponential Backoff cu Jitter. În cazul în care serverul Groq raportează o limitare de tokeni,
  scriptul utilizează o expresie regulată pentru a extrage din payload numărul exact de secunde
  cerut pentru răcire, aplicând o întârziere inteligentă înainte de reîncercare.
  4. Scriptul de evaluare programatică nativ în Python (`ai_tests/run_llm_eval.py`) rulează direct
  în consolă aserțiuni rapide de tip ancoră lingvistică pe profilele critice din Cluj-Napoca,
  garantând un scor perfect de **5/5 scenarii trecute (`PASSED`)** și un control total (QA Pipeline).
  5. S-a implementat filtrarea prin expresii regulate (regex) a tag-urilor interne de gândire
  (`<think>`), asigurând curățarea completă a textului generat înainte de afișare în Streamlit.
## 🔐 4. Strategia Securității Stratificate (Defense in Depth)

### Întrebare: Cum ai securizat cheile de API și cum ai protejat aplicația la runtime împotriva atacurilor cibernetice?
* **Apărare**: Proiectul aplică un model de securitate pe mai multe niveluri (Defense in Depth) pentru
a reduce suprafața de atac locală și în cloud.
* **Justificare Tehnică**:
  1. **Layer-ul 1 (Secret Isolation):** Toate acreditările private și cheile API (`GROQ_API_KEY`)
  sunt extrase complet din codul sursă și găzduite în fișierul local `.env` sau în panoul protejat
  de secrete, exclus structural din Git prin reguli stricte în `.gitignore`.
  2. **Layer-ul 2 (Criptare în Timp Constant):** Pentru a elimina riscul expunerii parolei în text
  clar, configurările încapsulează un hash hexazecimal stabil SHA-256 (amprenta unică pe 64 de caractere
  pentru parola `cluj2026`). Verificarea se face prin funcția `hmac.compare_digest`, eliminând complet
  atacurile de tip timing side-channel și oferind toleranță defensivă la runtime.
  3. **Layer-ul 3 (Access Control & State Isolation):** Componentele multipage din directorul
  `pages/` sunt protejate global prin starea de sesiune Streamlit
  (`st.session_state["authenticated"]`). Rezultatele generării AI sunt izolate în memorie pentru a
  rezista buclei automate de reîmprospătare a Streamlit, eliminând riscul widget-urilor duplicate.

---

## 🛠️ 5. Modernizarea Ecosistemului (uv vs requirements.txt)

### Întrebare: Am observat că ai utilizat managerul uv și ai definit dependențele în pyproject.toml. Care a fost motivul tehnic?
* **Apărare**: Menținerea fișierelor clasice `requirements.txt` introduse manual introduce un risc
major de *Environment Drift* (desincronizarea versiunilor de pachete în echipă sau între mediul
local și cel de producție).
* **Justificare Tehnică**: Sursa unică de adevăr pentru dependențe este definită strict prin
standardul modern PEP 621 în `pyproject.toml`, iar rezoluția deterministă a arborelui de pachete
este blocată prin `uv.lock`. Utilizarea managerului `uv` (scris în Rust) aduce instalări rapide
datorită mecanismului avansat de caching global, garantând instalări identice de fiecare dată prin
comanda `uv run`. Analiza statică și formatarea automată a codului sunt intermediate ultra-rapid prin
suita `ruff` (0 erori / 0 avertismente), conform standardelor stabilite în fișierul de configurare.
* **Static Method Optimization (N805):** Am eliminat utilizarea incorectă a decoratorului hibrid
`st.staticmethod` în favoarea decoratorului nativ Python `@staticmethod`. Acest lucru asigură
conformitatea deplină cu standardul PEP 8 / Ruff privind denumirea argumentelor primare de metodă
fără a forța introducerea artificială a obiectului `self`.

---

## 🧹 6. Controlul Calității Local și Gestiunea Cache-ului pe Windows

### Întrebare: Cum asiguri consistența codului la nivel local înainte ca acesta să fie trimis în pipeline-ul central de CI/CD?
* **Apărare**: Pentru a preveni acumularea fișierelor cache reziduale de compilare și blocarea
analizei statice prin structuri geometrice invalide, am dezvoltat un instrument nativ de control.
* **Justificare Tehnică**: Scriptul de automatizare dedicat Windows `scripts/lint.ps1` lansează un Job
PowerShell asincron în fundal (`Start-Job`) care evacuează rapid folderele cache reziduale
(`__pycache__`, `.pytest_cache`, `.ruff_cache`). Ulterior, firul principal execută secvențial
formatarea estetică (`ruff format .`) și analiza stilistică avansată cu fix-uri automate
(`ruff check . --fix`), asigurând un repository cu **0 erori detectate** înainte de executarea
testelor unificate din GitHub Actions (`ci.yml`).

---

## 🌐 7. Arhitectură Cloud, Optimizarea Costurilor și Disponibilitate

### Întrebare: Inițial ai configurat deployment-ul live pe platforma comercială Railway, dar ulterior ai migrat aplicația pe infrastructura nativă Streamlit Community Cloud. Care a fost raționamentul tehnic și arhitectural din spatele acestei decizii?
* **Apărare**: Decizia a fost guvernată de două principii fundamentale din Ingineria Software: **Cost
Optimization** și **Continuous High Availability**. Platformele comerciale generaliste prezintă un
risc major de suspendare a serviciilor odată ce limitele financiare sau creditele volatile sunt atinse.
Pentru un proiect de portofoliu accesat asincron de evaluatori academici și recrutori, un astfel de
blocaj reprezintă un punct critic de vulnerabilitate (*Single Point of Failure*).
* **Justificare Tehnică**: Prin migrarea completă către **Streamlit Community Cloud**, am eliminat
dependența de un buget runtime volatil, beneficiind de găzduire nativă gratuită și nelimitată,
optimizată pentru thread-urile de execuție Python. Din punct de vedere DevOps, noul pipeline realizează
un Continuous Deployment (CD) automat bazat pe webhook-uri securizate conectate la ramura `main` din
GitHub. Găzduirea dedicată asigură un uptime de 100%, curăță resursele blocate în memorie și garantează
recrutorilor un canal de testare stabil, performant și imun la constrângeri de tarifare comercială.

---

## 🔒 8. Managementul Secretelor în Cloud (Security Constraints)

### Întrebare: Dacă fișierul `.env` este izolat local prin `.gitignore` și nu este urcat pe GitHub, cum reușește aplicația ta să ruleze live în Streamlit Community Cloud fără să expună cheia `GROQ_API_KEY` sau parola administrativă?
* **Apărare**: Proiectul respectă cu strictețe recomandările **OWASP Top 10** și metodologia
*Twelve-Factor App* privind izolarea secretelor. Soluția a fost eliminarea completă a fișierelor de
configurare de pe serverul public de Git și injectarea lor securizată la runtime prin containerul
securizat al platformei de găzduire.
* **Justificare Tehnică**: În loc să stocăm date sensibile în repository, am utilizat panoul securizat
**Streamlit Secrets Management**. Configurările din `.env` sunt injectate criptat în consola cloud sub
formă de variabile TOML. La rulare, Streamlit le mapează nativ în obiectul protejat `st.secrets`, pe care
codul nostru din `main.py` și `groq_provider.py` îl accesează automat ca fallback dacă variabilele
`os.environ` nu sunt găsite. Acest mecanism de *Layered Security* guarantees că modelul local
`openai/gpt-oss-20b` primește cheile necesare, în timp ce codul sursă rămâne complet curat și protejat
împotriva scurgerilor de date în spațiul public.

---

## 🗂️ 9. Parsarea Securizată a Payload-urilor din SDK-urile AI (Librării Terțe)

### Întrebare: Am observat că în groq_provider.py extragi textul folosind indecși ficși. De ce ai ales această abordare și ce erori de tip runtime ai prevenit?
* **Apărare**: Obiectele returnate de API-urile LLM moderne (precum structura `ChatCompletion`)
sunt agregate asincron sub formă de liste în interiorul proprietății `.choices`. O eroare clasică
de începător este accesarea oarbă a proprietății ca obiect singular (`choices.message`), fapt ce
generează instantaneu un crash de tipul `TypeError` la execuție în producție.
* **Justificare Tehnică**: Pentru a garanta rezistența la runtime, am forțat o extragere explicită a
primului element Choice prin indexare fixă de tablou:
  ```python
  if completion_payload.choices:
      choice_item = completion_payload.choices[0]
      if hasattr(choice_item, "message") and choice_item.message:
          output_content = choice_item.message.content
  ```
  Acesta structură validează defensiv prezența datelor în colecție înainte de a consuma string-ul,
  asigurând randarea impecabilă a componentelor vizuale fără riscul de a bloca interfața.

---

## 🎨 10. Despachetarea Obiectelor Streamlit Columns ca Manageri de Context

### Întrebare: De ce ai refuzat să transmiți colecția st.columns(2) direct într-un bloc cu manager de context de tip 'with'?
* **Apărare**: Apelul funcției `st.columns(n)` returnează o listă nativă Python ce conține `n` obiecte
independente de tip coloană. Transmiterea listei agregate direct într-un manager de context
(de exemplu, `with ctrl_cols:`) generează o excepție fatală de tipul:
`TypeError: 'list' object does not support the context manager protocol`.
* **Justificare Tehnică**: Pentru a menține randarea multi-panel fluidă și conformă pe paginile de
Analytics și Dashboard, am aplicat un mecanism curat de despachetare a tuplurilor la nivel de asignare:
  ```python
  col_x, col_y = st.columns(2)
  with col_x:
      # Randare selector axă independentă
  ```
  Această decizie corectează logica fluxului Streamlit, permițând fiecărei coloane să acționeze ca un
  manager de context izolat, eliminând complet blocajele de afișare la runtime.

---

## 🗄️ 11. Rezoluția și Despachetarea Rezultatelor Scalare în SQLite3

### Întrebare: Pe pagina Analytics, de ce a eșuat conversia directă int(row) pe rezultatul fetchone() și cum ai asigurat corectitudinea tipurilor?
* **Apărare**: Driverul nativ `sqlite3` returnează întotdeauna un obiect de tip tuplu sau rând SQL
atunci când se apelează `.fetchone()`, chiar dacă interogarea selectează o singură coloană scalară
(de exemplu, `SELECT id FROM sensors`). Încercarea de a face `int(row)` direct pe un obiect de tip tuplu
provoacă o excepție critică de tipul `TypeError: int() argument must be a string... not 'tuple'`.
* **Justificare Tehnică**: Pentru a debloca încărcarea tranzacțională a istoricului fără a introduce
comentarii reziduale, am implementat extragerea explicită a primului element prin indexare structurală
înainte de conversia de tip:
  ```python
  row = conn.execute("SELECT id FROM sensors...").fetchone()
  sensor_id = int(row[0]) if row else 1
  ```
  Această barieră defensivă garantează că valoarea transmisă către interogarea subsecventă de `city_stats`
  este un număr întreg valid, prevenind blocarea execuției paginii statistice.

---

## 🎨 12. Controlul Preciziei Geometrice pe Axe în Plotly Dark Templates

### Întrebare: Cum ai eliminat randările distorsionate ale etichetelor float extinse de pe axele graficelor de monitorizare?
* **Apărare**: Calculele predictive bazate pe regresie liniară sau driftul valorilor simulate pot
genera numere float cu o precizie zecimală reziduală infinită (de exemplu, `32.19999999999574`), care
extind și distorsionează interfața grafică, scăzând lizibilitatea tabloului de bord.
* **Justificare Tehnică**: Am configurat o mască explicită de formatare a etichetelor direct în straturile
de layout ale vizualizărilor multi-panel din Plotly:
  ```python
  fig.update_yaxes(tickformat=".1f", showgrid=True, gridcolor="#2d3748")
  fig_ml.update_xaxes(tickformat=".1f")
  ```
  Folosind directiva industrială `.1f`, am forțat motorul grafic să rotunjească și să afișeze etichetele
  cu o singură cifră fixă după virgulă (ex: `32.2`), păstrând design-ul curat, compact și axat pe
  indicatori operaționali clari pentru utilizator.

## 🚀 13. Automatizarea Pipeline-ului de CI (Continuous Integration) & Validarea LLMOps

### Întrebare: Cum garantezi că o modificare adusă codului nu corupe formatarea PEP 8, testele asincrone sau logica asistentului AI înainte de merge?
* **Apărare**: În arhitectura Smart City, am tratat infrastructura DevOps ca pe un activ de prim rang.
Am eliminat complet verificările manuale prin implementarea unui pipeline automatizat de Integrare
Continuă (CI) declanșat prin GitHub Actions (`.github/workflows/ci.yml`).
* **Justificare Tehnică**: La fiecare comandă de `git push`, serverul de CI izolează mediul și
execută secvențial trei bariere defensive stricte, ghidate de regulile din `pyproject.toml`:
  1. **Alerte de Stil și Calitate (Ruff Gate):** Se verifică geometric limita de 100 de caractere
  pe linie (`E501`), sortarea alfabetică a importurilor (`I001`) și obligativitatea docstring-urilor
  publice conforme cu Google Style Guide (`D102`). Orice abatere oprește instantaneu build-ul.
  2. **Validarea Logicii de Business (Pytest Gate):** Se rulează suita de 9 teste unitare asincrone
  prin `uv run pytest -v`, asigurându-se că motorul tranzacțional, cooldown-ul alertelor și stările
  bazei de date sunt imune la regresii software.
  3. **Evaluarea Semantică AI (LLMOps Gate):** Se execută automat scriptul `run_llm_eval.py`.
  Acesta testează cele 5 scenarii critice împotriva modelului `gpt-oss-20b`, verificând prin ancore
  lingvistice poliglote (RO/EN) dacă răspunsurile asistentului rămân sigure și corelate cu contextul urban.

## 🌐 14. Livrarea Continuă (CD) și Managementul Git Webhooks în Cloud

### Întrebare: Cum se realizează trecerea codului aprobat din mediul local în producția live din cloud și cum sunt protejate secretele în acest pipeline?
* **Apărare**: Procesul de deployment este complet automatizat și urmează principiul de Continuous
Deployment (CD), eliminând complet riscul de *Environment Drift* sau suspendarea serverului din
cauza limitărilor comerciale volatile.
* **Justificare Tehnică**:
  1. **Continuous Deployment Nativ:** Odată ce faza de CI raportează succes total, platforma
  Streamlit Community Cloud (conectată prin Webhooks securizați la ramura `main` din GitHub)
  interceptează modificările. Serverul cloud reîmprospătează runtime-ul automat, instalând
  dependențele blocate determinist în `uv.lock`.
  2. **Zero Trust Secrete:** Pentru a nu expune cheile API (`GROQ_API_KEY`) sau credențialele în
  spațiul public de Git, acestea sunt stocate criptat în panoul de management cloud. La runtime,
  platforma le injectează direct în memoria RAM protejată a procesului sub formă de variabile TOML.
  Aplicația le consumă nativ prin obiectul izolat `st.secrets`, asigurând disponibilitate de 100%,
  uptime continuu pentru evaluatori și securitate absolută conform standardelor OWASP Top 10.
