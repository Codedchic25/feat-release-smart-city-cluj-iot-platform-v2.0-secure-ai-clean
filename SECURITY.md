# 🛡️ Politica de Securitate și Ghidul de Hardening: Smart City Cluj IoT Core

Acest document detaliază straturile defensive implementate în platformă pentru a proteja integritatea datelor IoT din Cluj-Napoca și a bloca atacurile cibernetice la nivel de API.

---

## 1. Straturi Defensive și Modelul Defense-in-Depth

Platforma aplică o arhitectură de securitate pe mai multe niveluri locale:

```text
  Date Senzori (Brut SQLite)
         │
         ▼
[Izolare Interfață Locală] ──► CityRepository preia datele securizat din DATABASE_PATH
         │
         ▼
[Sintaxă Prompt Structurată] ─► Izolează datele în interiorul tag-urilor din prompts.txt
         │
         ▼
[Sincronizare Matrice Limbi] ─► Aliniază răspunsurile cu componenta TranslationProvider
         │
         ▼
[Filtrare Regex Gândire AI] ──► Elimină automat tag-urile <think> returnate de Groq API
```

## 2. Managementul Acreditărilor și Secretelor Urbane

- **Izolarea Cheilor Private**: Toate credențialele sensibile (`GROQ_API_KEY`) și utilizatorii administrativi sunt complet extrași din codul sursă și stocați exclusiv în fișierul securizat local `.env`.
- **Criptare Avansată Locală**: Parola nu este stocată în text clar în `.env`, ci sub formă de hash hexazecimal prin algoritmul modern **SHA-256**. Clasa `AuthenticationService` din `main.py` execută conversia la runtime și folosește funcția `hmac.compare_digest` în timp constant, blocând complet atacurile de tip timing side-channel și eliminând complet parolele fixe (backdoors).
- **Prevenirea Scurgerilor în Producție**: Fișierul `.env` este introdus explicit în `.gitignore` și `.dockerignore`. Nicio cheie de producție sau certificat nu ajunge în sistemul public de control al versiunilor (GitHub).
- **Hardening prin Containerizare**: Execuția platformei în interiorul containerului Docker izolează procesele aplicației de sistemul de operare gazdă (Host OS). Toate porturile neesențiale sunt închise, fiind expus exclusiv portul standard de comunicație 8501, protejat prin directivele de rețea ale Docker.

## 3. Raportarea Vulnerabilităților

Dacă identificați o breșă de securitate în logica de evaluare a datelor sau în expunerea porturilor, vă rugăm **să nu deschideți un Issue public**. Trimiteți un raport detaliat echipei de securitate tehnică la adresa de e-mail dedicată portofoliului personal.

## 4. Protecția împotriva Atacurilor de tip Path Traversal pe Fișierul de Loguri

* **Întrebare de Arhitectură**: De deoarece jurnalul de audit `security_alerts.log` este citit dinamic și afișat în timp real pe interfața dashboard-ului, cum este protejat sistemul împotriva unui atac prin care o componentă malițioasă ar încerca să citească alte fișiere de pe server (ex: `/etc/passwd`)?
* **Barieră implementată**: Calea către fișierul de jurnalizare este definită în mod absolut imutabil la nivel de modul prin structura nativă `Path("security_alerts.log").resolve()`. Codul din `main.py` și `ai_interface.py` nu acceptă parametri sau argumente din exterior (din query string sau input-uri text ale utilizatorului) pentru a schimba locația descriptorului de fișier. Funcția execută o citire nativă directă pe calea pre-alocată pe disc, blocând la nivel de compilare orice tentativă de injectare a caracterelor de salt directoare (de tip `../`), securizând total afișarea datelor în interfața utilizator (UI).
