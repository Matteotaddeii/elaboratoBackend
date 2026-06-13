# Web App negozio online TechStore

**Studente:** Matteo Taddei  
**Corso:** Progettazione e Produzione Multimediale 2026  
**Tipologia Progetto:** Full-Stack Web Application usando Django  
**Link Repository GitHub:** https://github.com/Matteotaddeii/elaboratoBackend  
**Link di Deployment:** https://techstore-taddei.onrender.com

---

## Descrizione dell'Applicazione e Scopo

**TechStore** è una Web Application per la vendita di prodotti tecnologici. Il progetto fornisce un'applicazione completa con tre ruoli distinti:
* **I Clienti** possono esplorare il catalogo prodotti, filtrarlo per categoria, cercare articoli specifici, gestire un carrello personale, effettuare ordini e pubblicare recensioni.
* **I Magazzinieri** possono accedere a una dashboard riservata per gestire le scorte, variare la visibilità dei prodotti e contrassegnare gli ordini come spediti.
* **Gli Store Manager** hanno la supervisione finanziaria degli ordini, e possono gestire gli utenti (incluso il blocco dell'account e il cambio dinamico dei ruoli).

---

## Requisiti d'Esame

Di seguito si evidenziano le corrispondenze tra i requisiti obbligatori e l'implementazione:

*   **Architettura dell'applicazione:** Il progetto è suddiviso in applicazioni Django (`accounts`, `store`, `reviews`).
*   **Interfaccia Frontend:** I template HTML5 estendono un `base.html` comune e utilizzano **Bootstrap 5.3** per il layout responsive e la stilizzazione dei componenti (navbar, card, form, badge, tabelle). Le icone sono fornite da **Bootstrap Icons 1.11**.
*   **Estensione del Modello Utente:** È stato implementato un modello utente personalizzato (`CustomUser`) che estende `AbstractUser` di Django per la gestione dei ruoli tramite un campo dedicato.
*   **Presenza di almeno 3 Ruoli distinti:** Il sistema gestisce i ruoli di **Customer**, **Warehouse Worker** (Magazziniere) e **Store Manager**.
*   **Viste Basate su Classi:** Il progetto si fa largo uso di generic class-based views di Django. Esempi: `ProductListView(ListView)` per il catalogo con paginazione e filtri, `ProductDetailView(DetailView)` per il dettaglio prodotto, `ProductUpdateView(UpdateView)` e `ProductCreateView(CreateView)` per la gestione del catalogo, `ManagerDashboardView(ListView)` per il pannello finanziario. Tutte le viste riservate allo staff ereditano da `LoginRequiredMixin` e `UserPassesTestMixin`.
*   **Form e Validazione:** La raccolta e validazione dei dati utente avviene tramite `ModelForm` di Django: `CustomerRegistrationForm` (registrazione pubblica), `UserProfileForm` (modifica profilo) e `ReviewForm` (scrittura/modifica recensioni). La validazione è gestita interamente lato backend e gli errori vengono mostrati inline nel form.
*   **Autenticazione:** Sono implementati **Login**, **Logout** e **Registrazione pubblica** degli utenti (accessibile all'URL `/registrazione/`). Dopo il login o la registrazione, l'utente viene reindirizzato automaticamente alla pagina richiesta o alla Home.
*   **Controllo degli Accessi e Sicurezza:** I permessi sono gestiti lato backend tramite **Decoratori** (per le viste a funzione, es. `@login_required`) e **Mixins** di Django (per le viste basate su classi, es. `LoginRequiredMixin` e `UserPassesTestMixin`), impedendo accessi non autorizzati e URL injection.
*   **Integrità dei Dati e Database:** Le relazioni tra le tabelle utilizzano chiavi esterne (`ForeignKey`) con vincoli di integrità referenziale. La procedura di checkout è protetta tramite **`transaction.atomic()`** di Django, assicurando transazioni ACID ed evitando incongruenze nel database.

---

## Scelte Architetturali Varie

### Perché NON è stato fatto il CRUD completo su Utenti e Prodotti
1.  **Prodotti:** Se permettessi la cancellazione fisica di un prodotto dal database, tutti gli ordini passati effettuati dagli utenti che contenevano quel prodotto rimarrebbero senza riferimento, violando i vincoli di chiave esterna, o verrebbero cancellati a cascata, distruggendo lo storico contabile dello store. Per questo motivo, per i Prodotti si è optato per una **disattivazione logica** gestibile dallo Store Manager e dal Magazziniere.
2.  **Utenti:** Se permettessi una cancellazione degli utenti provocherebbe la perdita di tracciabilità degli ordini. Lo Store Manager può modificare lo stato dell'utente per impedirgli di accedere alla web app.

### Dove ho applicato il CRUD completo
1.  **Elementi del Carrello:** L'utente deve poter creare una sessione di carrello (**Create**), vederla (**Read**), aggiornare le quantità dei singoli prodotti in base alle sue intenzioni di acquisto (**Update**) o svuotare/rimuovere un elemento se cambia idea (**Delete**).
2.  **Recensioni:** Qualsiasi utente autenticato scrive una nuova recensione (**Create**), chiunque può leggere le recensioni nella pagina del prodotto (**Read**), l'autore può aggiornare il proprio voto e commento (**Update**), l'autore o lo store manager (amministratore) può cancellare la recensione dal database (**Delete**).

### Schema delle Relazioni del Database
Per garantire la coerenza logica, il database fa uso di relazioni strutturate:
*   **CustomUser ↔ Order** (Uno-a-Molti): Traccia quale cliente ha effettuato l'ordine.
*   **Product ↔ Category** (Uno-a-Molti): Associa ciascun prodotto a una singola categoria.
*   **Order ↔ OrderItem ↔ Product** (Molti-a-Molti tramite tabella intermedia): Gestisce il dettaglio dei prodotti acquistati all'interno di un ordine, memorizzando il prezzo storico del prodotto al momento del checkout per evitare che variazioni di prezzo future corrompano gli ordini passati.
*   **Product ↔ Review ↔ CustomUser**: Consente agli utenti autenticati di lasciare recensioni su specifici prodotti.

### Controllo del Carico e Ottimizzazione delle Prestazioni
Per evitare il sovraccarico del database e garantire tempi di risposta rapidi anche in presenza di un grande volume di dati, l'applicazione implementa strategie di **caricamento parziale dei dati (paginazione)**:
*   **Paginazione dei Prodotti (Catalogo):** Nella vista principale del catalogo, i prodotti vengono caricati e suddivisi in pagine da **6 elementi ciascuna**. Ciò evita di caricare in memoria e renderizzare centinaia di prodotti contemporaneamente. Sei prodotti è giusto un limite indicativo per far vedere che funzona, nella realtà sarebbe molto di più.
*   **Paginazione degli Ordini (Dashboard e Storico):** Sia nel pannello finanziario dello Store Manager sia nello storico degli ordini del cliente, gli ordini vengono paginati a gruppi di **20 elementi per pagina**.
*   **Paginazione degli Utenti (Gestione Utenti):** Nella schermata di amministrazione degli utenti riservata allo Store Manager, l'elenco di tutti gli iscritti al portale viene paginato a gruppi di **20 utenti per pagina**, riducendo la quantità di record caricati all'avvio.
*   **Query Ottimizzate (Lazy Querysets):** Le query generate da Django sfruttano la valutazione *lazy*. Questo significa che il database viene interrogato per recuperare solo lo stretto necessario (i record della pagina corrente) e solo nel momento in cui i dati vengono effettivamente renderizzati nel template.

---

## Ruoli e Funzionalità Implementate

L'applicazione si basa sul controllo degli accessi basato sui ruoli. Tutti gli utenti autenticati del sistema condividono le funzionalità di base dedicate all'acquisto e alla consultazione del catalogo.

### Funzionalità Accessibili a Tutti (anche utenti non registrati)
*   Sfogliare il catalogo prodotti, applicare filtri (per categoria e disponibilità) e cercare articoli.
*   Visualizzare i dettagli dei prodotti e leggerne le recensioni pubbliche.
*   Aggiungere prodotti al carrello (il carrello è conservato nella sessione anche senza login).
*   **Registrarsi autonomamente** come nuovo Cliente tramite il form pubblico all'indirizzo `/registrazione/`.

### Funzionalità Comuni (Tutti gli utenti autenticati)
Qualsiasi utente loggato (**Customer**, **Warehouse Worker** o **Store Manager**) può, in aggiunta a quelle sopra:
*   Procedere al checkout e finalizzare un ordine (con decremento atomico delle scorte tramite transazione).
*   Visualizzare lo storico dei propri acquisti personali.
*   Scrivere, modificare o eliminare le proprie recensioni.

### Funzionalità Specializzate per Ruolo

#### 1. Warehouse Worker (Magazziniere)
Oltre alle funzionalità comuni, ha accesso ai poteri di logistica e catalogo:
*   **Gestione Catalogo Globale:** Creazione, modifica e disattivazione logica (visibilità) di prodotti e categorie.
*   **Dashboard Logistica:** Accesso a una dashboard riservata per gestire l'inventario e le spedizioni.
*   **Gestione Spedizioni:** Visualizzazione della coda degli ordini non ancora evasi (senza dettagli sui prezzi) e aggiornamento dello stato dell'ordine in "Spedito".
*   **Gestione Scorte:** Modifica rapida delle quantità disponibili a magazzino e dello stato di attivazione/visibilità del prodotto sul catalogo.

#### 2. Store Manager (Amministratore)
Oltre alle funzionalità comuni, possiede poteri gestionali e di moderazione:
*   **Riepilogo Finanziario:** Visualizzazione dello storico completo e dello stato di tutti gli ordini del sistema, con evidenza del fatturato totale.
*   **Gestione Utenti:** Visualizzazione della lista di tutti gli iscritti, con possibilità di bloccare/sbloccare un account e variare dinamicamente il ruolo.
*   **Moderazione Recensioni:** Possibilità di eliminare dal database le recensioni scritte da qualsiasi altro utente.

---

## Possibili Evoluzioni

Il progetto rappresenta una **base funzionante e completa** per un e-commerce, progettata per coprire i requisiti d'esame e dimostrare conoscenza dei concetti chiave di Django. Sono consapevole, tuttavia, che in un contesto di produzione reale molte funzionalità potrebbero essere ulteriormente affinate e ampliate:

*   **Dashboard del Magazziniere:** La lista degli ordini da evadere e dell'inventario potrebbe beneficiare di filtri aggiuntivi (per stato, per data, per categoria) e di una barra di ricerca dedicata per gestire volumi molto elevati di dati in modo più efficiente.
*   **Pannello del Manager:** Il riepilogo finanziario potrebbe essere arricchito con grafici e statistiche aggregate oppure filtri per selezionare periodi di tempo.
*   **Catalogo Prodotti:** Si potrebbero aggiungere ordinamenti multipli (per prezzo crescente/decrescente, per novità).
*   **Gestione Utenti:** La lista degli iscritti potrebbe includere una barra di ricerca per username o email, utile quando il numero di utenti cresce significativamente.
*   **Carrello Persistente:** L'attuale carrello basato sulla sessione potrebbe essere sostituito con un modello database dedicato, così da preservare gli articoli anche dopo la chiusura del browser e permettere il ripristino del carrello da dispositivi differenti.
*   **Sistemi di Pagamento:** L'aggiunta di sistemi di pagamento reali.
*   **Integrazione Email:** L'aggiunta di sistemi di email per notificare acquisti.

Queste funzionalità non sono state incluse per mantenere il codice semplice e mostrare sopratutto la conoscenza dei requisiti fissati per questo elaborato.

---

## Database e Account di Prova (Pre-popolati)

Il progetto include il file di database SQLite **`db.sqlite3`**. Si conferma che questo database è già **pre-popolato con dati dimostrativi di test** (categorie, prodotti, recensioni ed ordini storici) oltre ai seguenti account di test pronti all'uso suddivisi per ruolo:

*   **Store Manager (Amministratore):** `Username: manager` / `Password: Gestore123!`
*   **Warehouse Worker (Magazziniere):** `Username: magazziniere` / `Password: Ordini123!`
*   **Customer (Cliente):** `Username: cliente` / `Password: Acqu123!`

---

## Installazione e Avvio Locale

Segui questi passaggi per configurare ed eseguire il progetto in locale:

1. **Clona la repository o posizionati nella cartella del progetto:**
   ```bash
   git clone https://github.com/Matteotaddeii/elaboratoBackend.git
   cd elaboratoBackend
   ```

2. **Crea e attiva un ambiente virtuale (consigliato):**
   * **Su macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   *(Nota: come da specifiche, la cartella `venv/` è esclusa dai commit tramite il file `.gitignore` per non committare l'ambiente virtuale).*

3. **Installa le dipendenze richieste:**
   ```bash
      pip install -r requirements.txt
   ```

4. **Esegui le migrazioni per preparare il database (se necessario):**
   ```bash
      python manage.py migrate
   ```

5. **Avvia il server di sviluppo:**
   ```bash
      python manage.py runserver
   ```
   L'applicazione sarà accessibile all'indirizzo: `http://127.0.0.1:8000/`

6. **Crea un Superuser (Opzionale):**
   Se si desidera creare un nuovo amministratore con accesso completo al pannello di amministrazione Django (`/admin`):
   ```bash
      python manage.py createsuperuser
   ```

---

## Scenario di Test
### 1. Flusso di Acquisto da Anonimo, Login e CRUD Recensioni (Ruolo: Cliente)
* **Navigazione da Anonimo:** Senza effettuare il login, accedere alla Home del sito, sfogliare il catalogo prodotti e applicare i filtri di ricerca.
* **Aggiunta al Carrello:** Entrare nella pagina di dettaglio di un prodotto e cliccare su "Aggiungi al carrello". Navigare nel carrello per verificare che l'articolo sia presente anche senza essere autenticati.
* **Autenticazione in Fase di Checkout:** Cliccare sul pulsante "Procedi al checkout". Il sistema, intercettando l'utente anonimo, lo reindirizzerà automaticamente alla pagina di login. Effettuare l'accesso con l'account demo del Cliente.
* **Verifica Persistenza e Creazione Ordine:** Una volta loggati l'acquisto si completa automaticamente. Verificare che l'ordine sia stato inserito correttamente nell'area personale, e che le scorte siano state decrementate correttamente (verificabile ispezionando il database).
* **CRUD Completo (Recensioni):** Tornare sulla pagina dettagli del prodotto appena acquistato per testare il ciclo CRUD sulle recensioni:
    * *Create*: Compilare il form inserendo una valutazione e un commento.
    * *Read*: Verificare che la recensione sia visibile pubblicamente.
    * *Update*: Cliccare su "Modifica", cambiare il testo e salvare.
    * *Delete*: Cliccare su "Elimina" per rimuoverla fisicamente dal database.

### 2. Navigazione e Creazione Ordine (Ruolo: Cliente)
* **Login:** Accedere alla pagina di login ed effettuare l'accesso con l'account dimostrativo del Cliente.
* **Navigare:** Dalla pagina Catalogo, sfogliare i prodotti disponibili, applicare i filtri di ricerca e cliccare su un articolo per accedere alla sua pagina di dettaglio.
* **Creare Dati (Carrello e Ordine):** Aggiungere il prodotto al carrello, modificare la quantità direttamente dall'interfaccia di riepilogo e procedere al checkout. Verificare che l'ordine sia stato inserito correttamente nell'area personale, e che le scorte siano state decrementate correttamente (verificabile ispezionando il database).
* **CRUD Completo (Recensioni):** Tornare sulla pagina del dettaglio del prodotto appena acquistato per testare il ciclo CRUD sulle recensioni:
    * *Create*: Compilare il form inserendo una valutazione a stelle e un commento.
    * *Read*: Verificare che la propria recensione appaia istantaneamente nell'elenco pubblico.
    * *Update*: Cliccare sul pulsante "Modifica", variare il testo del commento e salvare.
    * *Delete*: Cliccare sul pulsante "Elimina" per rimuoverla fisicamente dal database.

### 3. Evasione Spedizioni e Gestione Inventario (Ruolo: Magazziniere)
* **Login:** Effettuare il logout e accedere alla pagina di autenticazione con le credenziali dell'Addetto al Magaziono.
* **Navigare:** Cliccare sul link "Pannello Magazzino" comparso dinamicamente nella barra di navigazione grazie ai controlli condizionali sul ruolo utente.
* **Modificare (Stato Ordine):** Nella colonna sinistra (Ordini da Evadere), individuare l'ordine creato nel precedente scenario dal cliente. Cliccare sul pulsante "Spedisci Pacco": l'ordine cambierà stato in *Spedito* nel database e scomparirà dalla coda logistica.
* **Modificare (Stock):** Nella tabella destra (Inventario), individuare un prodotto, incrementare o decrementare il numero di scorte nel campo numerico (`stock`) e premere "Aggiorna".
* **Verificare:** Effettuare il logout. Navigando nel catalogo anche da utenti non registrati, il prodotto modificato mostrerà la nuova quantità aggiornata in tempo reale, a riprova della corretta persistenza nel database. Viene mostrato come `Disponibile` se le scorte sono maggiori di 5, viene mostrato `Ultimi articoli rimasti` se le scorte sono comprese tra 1 e 5, mentre se le scorte sono 0 viene mostrato come `Esaurito`.

### 4. Controllo Direzione, Catalogo e Modifica Ruoli (Ruolo: Store Manager)
* **Login:** Effettuare l'accesso con le credenziali dello Store Manager.
* **Navigare:** Accedere alla Dashboard Direzionale per ispezionare il riepilogo economico e lo storico di tutti gli ordini complessivi del sistema.
* **Modificare (Catalogo):** Accedere alla sezione di gestione del catalogo prodotti per crearne uno nuovo o per variare la visibilità logica (`is_active = False`) di un prodotto, testando il meccanismo di Soft Delete per la tutela della coerenza del DB.
* **Modificare (Controllo Accessi Utenti):** Navigare nella vista "Gestione Utenti". Individuare l'utente `cliente` utilizzato nello Scenario 1. Attraverso il menu a tendina dinamico, selezionare un nuovo ruolo applicativo o cliccare sul pulsante per sospendere l'account (`is_active = False`).
* **Verificare:** Constatare la comparsa del messaggio di successo del sistema e verificare che i nuovi privilegi applicati all'utente siano immediatamente operativi nel database.

### 5. Sicurezza, Restrizioni di Accesso e Gestione degli Errori (Test dei Permessi)
* **Azione:** Dopo essersi loggati con l'account del cliente, tentare un attacco di tipo URL-injection digitando forzatamente nella barra degli indirizzi del browser i percorsi riservati allo staff, come ad esempio la dashboard di logistica (`/magazzino/`) o la gestione utenti del manager (`/gestione/utenti/`).
* **Verificare il Risultato:** Il backend intercetta la richiesta non autorizzata grazie ai sistemi di protezione e al fatto che l'utente non ha i permessi necessari. L'accesso viene bloccato alla radice: il browser mostrerà una pagina di "Accesso Negato" (errore HTTP 403) o reindirizzerà l'utente mostrando un messaggio di avviso a schermo, provando l'efficacia dei sistemi di sicurezza.