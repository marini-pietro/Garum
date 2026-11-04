> Garum non fornisce consigli medici nè ne ha l'intenzione.  
> L' unico scopo di Garum è quello di tracciare dati e calcolare tendenze relative alla nutrizione.  
> L'app, opzionalmente, mostra valori derivati da linee guida e raccomandazioni pubblicate da organizzazioni sanitarie ed esperti.  
> I valori, e da chi prenderli, sono interamente a discrezione dell'utente.   
> Prima di apportare qualsiasi cambiamento significativo allo stile di vita, si prega di consultare un professionista medico qualificato.  
> Il creatore dell'app non si assume alcuna responsabilità per qualsiasi risultato derivante dall'uso improprio o dal mancato rispetto delle linee guida sopra riportate.  

<br>
<h1 align="center">
Garum
</h1>

<br>
<p align="center">
<img src="src/assets/logo_white.svg" alt="App logo">
</p>

## Scopo

Da studente universitario che bilancia lezioni, attività extracurriculari, compiti e progetti personale, ho trovato sempre più difficile tenere traccia della mia nutrizione e delle spese alimentari.  
Una buona nutrizione aiuta immensamente a sostenere uno stile di vita così attivo, ma tracciarla mentalmente o su carta diventava rapidamente impreciso e tedioso.  
Garum è stato costruito per risolvere questo problema.

## Funzionalità

**Catalogo**: base di conoscenza in cui vengono conservati e organizzati i record sui prodotti conosciuti.  
L'utente può creare, visualizzare, aggiornare ed eliminare uno qualsiasi di questi record in qualsiasi momento nella finestra dedicata al catalogo.  
Ogni record ha attributi come prezzo o nome, ma solo gli articoli alimentari avranno informazioni sulla nutrizione.

**Inventario**: istantanea attuale dei prodotti e della quantità di prodotti disponibili.  
Quando si aggiorna l'inventario (ad esempio dopo aver fatto la spesa), l'utente può scegliere un prodotto dal catalogo o descriverne uno manualmente se non è presente nella base di conoscenza (l'utente avrà quindi la possibilità di aggiungerlo alla base di conoscenza).

**Ricette**: record sulle ricette e sugli ingredienti necessari per realizzarle.  
Come default le ricette avranno le informazioni nutrizionali definite come la somma degli ingredienti, ma i valori sono modificabili dall'utente (perchè, ad esempio, alcuni ingredienti perdono parte dei loro valori nutrizionali quando cucinati in alcuni modi).

**Monitoraggio dei pasti**: record sui pasti consumati dall'utente.  
L'utente può descrivere un pasto utilizzando una ricetta o alimenti individuali.  
L'inventario verrà aggiornato di conseguenza in base alla ricetta o alle quantità di ciascun alimento inserito.  
L'app genererà quindi grafici dell'assunzione nutrizionale dell'utente in diversi periodi di tempo, come la settimana o il mese precedente, e riporterà la percentuale di ciascun nutriente consumato rispetto alle raccomandazioni di organizzazioni sanitarie affidabili (ad esempio American Heart Association).  
Per supportare un monitoraggio nutrizionale accurato, all'utente verrà chiesto di fornire informazioni di base come peso, altezza e livello di attività.  
Come menzionato nell'avviso in cima al documento, l'app non si occupa di BMI, calcoli del metabolismo basale o simili valori.  
Informazioni come il peso vengono utilizzate solo per calcolare l'assunzione nutrizionale raccomandata; ad esempio, alcune organizzazioni sanitarie forniscono raccomandazioni per chilogrammo di peso corporeo.

**Monitoraggio dei prezzi**: record sui prezzi dei prodotti nel tempo, prezzi per gli stessi prodotti in diversi negozi, scontrini della spesa e costi dei pasti.  
L'app traccia questi dati relativi ai prezzi e genera grafici per aiutare l'utente a comprendere le proprie abitudini di spesa e prendere decisioni informate sugli acquisti alimentari.  
Ad esempio, l'utente può visualizzare il costo medio dei pasti nel tempo, confrontare i prezzi dello stesso prodotto in diversi negozi e rivedere quello che ha acquisto nelle scorse spese.  

**Comportamento generale dell'app**:

- Notifiche: L'app non presenta notifiche.

- Raccolta dati: L'app non raccoglie dati di telemetria sul comportamento o sulle preferenze dell'utente, tutti i dati rimangono locali.

- Import/export: È possibile importare ed esportare (come file JSON) vari tipi di dati, come le impostazioni, il catalogo e la storia dei pasti.

- Cross-platform: poichè costruita sul framework [Flet](https://flet.dev/), Garum è compatibile con piattaforme multiple senza sforzo extra.

## Origini del nome

> Questa sezione è solamente una breve introduzione al Garum.  
> Non verrà tenuta aggiornata con le ultime scoperte, per informazioni accurate consultare fonti appropriate.

Da Wikipedia (parafrasato): [Garum](https://en.wikipedia.org/wiki/Garum) è una salsa di pesce fermentata che veniva utilizzata come condimento nelle cucine di Fenicia, Grecia antica, Roma, Cartagine e successivamente Bisanzio.    

Mescolato con l'oenogarum (una popolare salsa di vino bizantina), aceto, pepe nero e olio, il garum veniva usato come esaltatore di sapidità in diversi piatti, tra cui il vitello bollito, le cozze al vapore e persino il soufflé di pere e miele. Diluito con acqua per ottenere l'idrogarum, veniva utilizzato anche come razione per le legioni romane.  
Sebbene raggiunse la massima popolarità nel Mediterraneo occidentale e nel mondo romano, il garum era già conosciuto e utilizzato dai Greci.  
Si ritiene che il suo sapore fosse simile a quello delle moderne salse di pesce asiatiche.  
Come le odierne salse di pesce fermentate e la salsa di soia, il garum era una ricca fonte di sapidità umami grazie alla presenza di glutammati.  
Veniva inoltre impiegato, insieme al murri, nella cucina bizantina e araba medievale per insaporire i piatti.

Il garum veniva utilizzato anche come medicinale per trattare morsi di cane, dissenteria, ulcere, diarrea cronica e altre malattie, nonché come ingrediente di preparati cosmetici destinati a rimuovere peli indesiderati o lentiggini.   

Per ulteriori informazioni, consiglio vivamente la [pagina di Wikipedia dedicata al garum](https://en.wikipedia.org/wiki/Garum) e gli eccellenti video di Max Miller sul suo canale YouTube *Tasting History with Max Miller*. Per iniziare, guarda questo [video](https://www.youtube.com/watch?v=ICZww0DtQKk).

## Avviare l'app

Il progetto utilizza un layout `src`. [`src/main.py`](src/main.py) è il singolo
launcher Flet scoperto da `flet run`; il codice dell'applicazione è organizzato sotto
il pacchetto `garum`:

- `garum/gui` contiene la GUI di Flet e le definizioni dei temi.
- `garum/handlers/models.py` contiene modelli immutabili delle tuple del database e le relative regole di serializzazione del database; non accede a SQLite.
- `garum/handlers/storage.py` contiene la connessione/transaction boundary di SQLite e i repository come `FoodEntryRepository`; restituisce modelli ma non definisce la loro forma.
- `garum/handlers/settings_handler.py` contiene il servizio indipendente delle impostazioni JSON.
- `src/assets` contiene file impacchettati come asset Flet.
- `data/db.sql` è lo schema SQLite utilizzato per inizializzare il database locale.

### Palette dei temi

I colori del tema sono esportati da [`src/garum/gui/theme.py`](src/garum/gui/theme.py) come `LIGHT_PALETTE`, `DARK_PALETTE`, e `THEME_PALETTES`.  
L'impostazione `APP_THEME` seleziona una di queste palette all'avvio.  
La palette chiara è basata su sabbia del deserto con superfici UI di colore marrone e argilla; la palette scura è basata su grigio scuro con superfici elevate nere e controlli grigi chiari.  
Entrambe le palette utilizzano il rosso per gli errori.

### uv

Eseguire come app desktop:

```bash
uv run flet run
```

Eseguire come app web:

```bash
uv run flet run --web
```

### comando flet

Eseguire come app desktop (uv non necessario):

```bash
flet run
```

Per maggiori dettagli su come avviare l'app, fare riferimento alla [guida introduttiva](https://flet.dev/docs/).  

## Compilare l'app

### Android

```bash
flet build apk -v
```

Per maggiore dettagli su come compilare e firmare `.apk` o `.aab`, fare riferimento alla [guida al packaging Android](https://flet.dev/docs/publish/android/).  

### iOS

```bash
flet build ipa -v
```

Per maggiori dettagli su come compilare e firmare `.ipa`, fare riferimento alla [guida al packaging iOS](https://flet.dev/docs/publish/ios/).  

### macOS

```bash
flet build macos -v
```

Per maggiori dettagli su come compilare il pacchetto macOS, fare riferimento alla [guida al packaging macOS](https://flet.dev/docs/publish/macos/).  

### Linux

```bash
flet build linux -v
```

Per maggiori dettagli su come compilare il pacchetto Linux, fare riferimento alla [guida al packaging Linux](https://flet.dev/docs/publish/linux/).  

### Windows

```bash
flet build windows -v
```

Per maggiori dettagli su come compilare il pacchetto Windows, fare riferimento alla [guida al packaging Windows](https://flet.dev/docs/publish/windows/).  

### Web

```bash
flet build web -v
```

Per maggiori dettagli su come compilare l'app Web, fare riferimento alla [guida al packaging Web](https://flet.dev/docs/publish/web/).  

## Contributi

I contributi sono benvenuti e molto apprezzati.  
Si prega di leggere la [guida ai contributi](CONTRIBUTING.md) prima di aprire un problema o inviare una pull request.  

## Licenza

Garum è distribuito sotto la licenza GNU General Public License v3.0.  
Fare riferimento al file [LICENSE](LICENSE.txt) per i dettagli.  