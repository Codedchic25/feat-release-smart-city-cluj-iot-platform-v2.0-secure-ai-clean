# 🤝 Ghid de Contribuire la Proiectul Smart City Cluj IoT

Vă mulțumim că ați ales să contribuiți la dezvoltarea platformei urbane! Pentru a menține integritatea arhitecturală și un istoric curat al codului, vă rugăm să respectați următorul set de reguli administrative și tehnice.

---

## 🚀 Workflow de Dezvoltare și Deployment Local

Toate operațiunile din mediu se realizează utilizând exclusiv managerul de pachete de mare viteză `uv`. Nu adăugați dependențe manual fără a le înregistra în structura proiectului.

1. **Clonarea și pornirea mediului:**
   ```bash
   git clone <repository-url>
   cd cluj-smartcity-iot-core
   uv sync
   ```

2. **Verificarea Pipeline-ului înainte de Commit/Push:**
   Înainte de a împinge modificările pe ramura `main` (care declanșează automat pipeline-ul de CI/CD), asigurați-vă că toate testele unitare, linterele și evaluările de securitate trec cu succes:
   ```bash
   # Comenzi pentru validarea barierelor calitative și generarea rapoartelor JSON
   uv run ruff check .
   uv run pytest
   uv run python ai_tests/run_llm_eval.py
   npx promptfoo eval
   ```

---

## 🛠️ Reguli de Calitate a Codului (Ruff-Style)

Proiectul folosește un sistem strict de analiză statică. Orice cod care încalcă regulile va fi respins la integrare de către pipeline-ul de CI/CD:
* Toate fișierele de cod Python trebuie verificate și formatate folosind `ruff`. Rularea `uv run ruff format .` și `uv run ruff check . --fix` trebuie să returneze statusul curat, fără erori de tip redefiniri (`F811`) sau câmpuri duplicate (`PIE794`).
* Nu lăsați instrucțiuni `print()` reziduale în straturile de backend; folosiți sistemul nativ de logging integrat în `main.py` (`LOGGER.info`).
* Păstrați inegalitățile stricte pentru evaluarea limitelor telemetrice pentru a preveni oscilația alertelor în dashboard.

---

## 🧪 Integrarea Suitei de Teste, Securitate și MLOps

* **Backend Regression Tests:** Dacă adăugați funcționalități noi sau modificări lingvistice în dicționare, rulați suita completă din folderul dedicat utilizând `uv run pytest`. Aceasta va executa cele **9 teste parametrizate** și va genera automat raportul metric structurat `ai_tests/pytest_report.json`.
* **Validare Semantică:** Modificările aduse prompturilor din `ai_tests/prompts.txt` necesită re-rularea matricei de evaluare Python (`run_llm_eval.py`) pentru a demonstra un scor stabil de **100% passed** pe profilele critice urbane direct prin modelul de producție activ `openai/gpt-oss-20b`, generând raportul `ai_tests/llm_eval_report.json`.
* **AI Red-Teaming Matrix:** Rulați evaluarea declarativă `npx promptfoo eval` pentru a valida rezistența platformei în fața atacurilor de tip Prompt Injection. Toate cele **7 scenarii critice** trebuie să returneze statusul `Success` și să compileze jurnalul de conformitate `ai_tests/promptfoo_report.json`.

---

## 🔐 Securitate și Izolare

* **Fără Secrete în Git:** Nu introduceți niciodată chei private API sau parole în text clar în cod. Toate variabilele de mediu sensibile trebuie să rămână izolate pe disc în fișierul local `.env`.
* **Criptare în Timp Constant:** Autentificarea administrativă verifică hash-ul **SHA-256** din `.env` folosind metoda `hmac.compare_digest` pentru a preveni atacurile bazate sursă pe analiză de timp (side-channel timing attacks) și elimină complet parolele fixe (backdoors).
* **Sistem Local:** Toate sistemele de alertare trebuie să utilizeze scrierea protejată prin cooldown-ul de 10 secunde în `security_alerts.log`, curățând explicit caracterele `\n` și `\r` pentru a bloca atacurile de tip Log Injection / Log Forgery.
