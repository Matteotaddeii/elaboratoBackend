# Web App negozio online TechStore

**Studente:** Matteo Taddei  
**Corso:** Progettazione e Produzione Multimediale 2026  
**Tipologia Progetto:** Full-Stack Web Application usando Django 
**Link Repository GitHub:** https://github.com/Matteotaddeii/elaboratoBackend 
**Link di Deployment:**   

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
*   **Estensione del Modello Utente:** È stato implementato un modello utente personalizzato (`CustomUser`) che estende `AbstractUser` di Django per la gestione dei ruoli tramite un campo dedicato.
*   **Presenza di almeno 3 Ruoli distinti:** Il sistema gestisce i ruoli di **Customer**, **Warehouse Worker** (Magazziniere) e **Store Manager**.
*   **Controllo degli Accessi e Sicurezza:** I permessi e le restrizioni sono gestiti lato backend tramite una combinazione di **Decoratori** (per le viste a funzione, es. `@login_required`) e **Mixins** di Django (per le viste basate su classi, es. `LoginRequiredMixin` e `UserPassesTestMixin`), impedendo accessi non autorizzati e URL injection.
*   **Integrità dei Dati e Database:** Le relazioni tra le tabelle utilizzano chiavi esterne (`ForeignKey`) con vincoli di integrità referenziale ben definiti. Inoltre, per garantire la consistenza dei dati, la procedura di checkout e aggiornamento delle scorte del magazzino è stata protetta tramite la direttiva **`transaction.atomic()`** di Django, assicurando transazioni ACID ed evitando incongruenze nel database.

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

### Funzionalità Comuni (Tutti gli utenti autenticati)
Qualsiasi utente loggato (**Customer**, **Warehouse Worker** o **Store Manager**) può:
*   Sfogliare il catalogo prodotti, applicare filtri (per categoria e disponibilità) e cercare articoli.
*   Visualizzare i dettagli dei prodotti e leggerne le recensioni.
*   Gestire il proprio carrello personale (aggiunta, rimozione e modifica quantità degli articoli).
*   Effettuare ordini (con decremento atomico delle scorte tramite transazione) e visualizzare lo storico dei propri acquisti personali.
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

Ecco un breve scenario di test per verificare le funzionalità principali, il CRUD e il sistema di permessi basato sui ruoli:

1. **Login e Creazione Dati (Ruolo: Cliente):**
   * Andare all'indirizzo `http://127.0.0.1:8000/login` ed effettuare l'accesso con l'account dimostrativo (`cliente` / `Acqu123!`).
   * **Navigare:** Dalla Home, sfogliare il catalogo e cliccare su un prodotto per vederne i dettagli.
   * **Creare:** Aggiungere il prodotto al carrello e procedere al checkout per creare un nuovo ordine.
   * **Verificare:** Visitare la pagina del proprio profilo o dello "Storico Ordini" per assicurarsi che l'ordine sia stato registrato con successo.

2. **Test dei Permessi (Sicurezza delle Rotte):**
   * Rimanendo loggato come Cliente, provare a forzare l'accesso inserendo nella barra degli indirizzi l'URL di una pagina riservata allo staff (ad esempio la dashboard del magazziniere o del manager).
   * **Verificare:** Il sistema negherà l'accesso (mostrando un errore 403 o reindirizzando), dimostrando il corretto funzionamento dei blocchi di sicurezza (`UserPassesTestMixin` e decoratori).

3. **Modifica Dati e Cambio Ruolo (Ruolo: Magazziniere):**
   * Effettuare il logout e accedere con le credenziali di logistica (`magazziniere` / `Ordini123!`).
   * **Navigare:** Accedere alla *Dashboard Logistica* riservata al proprio ruolo.
   * **Modifica/Verifica:** Trovare l'ordine effettuato precedentemente dal cliente e modificarne lo stato contrassegnandolo come "Spedito". Andare poi nel catalogo e modificare la disponibilità (scorte) del prodotto appena venduto, verificando che la modifica si rifletta nel database.