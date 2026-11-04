<p align="center">
[🇮🇹 README in italiano](README_IT.md)
</p>

> Garum does not provide medical advice and is not intended to do so.  
> The sole purpose of Garum is to track data and compute trends related to nutrition.   
> The app, optionally, displays values derived from guidelines and recommendations published by health organizations and experts.  
> The values, and from whom to pick them, is entirely at the hands of the user.  
> Before making any significant lifestyle change, please consult a qualified medical professional.  
> The app's creator accept no responsibility for any outcome resulting from the misuse of, or failure to follow, the above guidance.  

<br>
<h1 align="center">
Garum
</h1>

<br>
<p align="center">
<img src="src/assets/logo_white.svg" alt="App logo">
</p>

## Purpose

As a university student balancing lectures, extracurricular activities, homework, and side projects, I found it increasingly difficult to keep track of my nutrition and food expenses.  
Good nutrition immensly helps in sustaining such an active lifestyle, but tracking it mentally or on paper quickly became inaccurate and tedious.  
Garum was built to solve that problem.

## Features

**Catalogue**: knowledge base in which records about known products are kept and organized.  
The user can create, view, update and delete any of these records at any given moment in the dedicated Catalogue window.
Each record has attributes like price or name but only food items will feature information about nutrition.

**Inventory**: current snapshot of the products and quantity of products available.  
When updating the inventory (e.g. after buying groceries) the user can choose a product from the catalogue or manually describe one if it's not in the knowledge base (the user will then have the option to add it to the knowledge base).

**Recipes**: records about recipes and the ingredients necessary to make them.  
By default the recipes will contain nutrient info as the sum of the ingredients but the values are modifiable by the user (e.g. some ingredients lose part of their nutritional values when cooked in some manners).  
It is also possible to see all the recipes the user can make with the items tracked in the inventory.

**Nutrition tracking**: records about the meals consumed by the user.  
The user can describe a meal using either a recipe or individual foods.  
The inventory will be updated accordingly based on the recipe or the quantities of each food entered.  
The app will then generate graphs of the user's nutritional intake over different time periods, such as the past week or month, and report the percentage of each nutrient consumed relative to recommendations from trusted health organizations (e.g. American Heart Association).  
To support accurate nutrition tracking, the user will be asked to provide basic information such as their weight, height, and activity level.  
As mentioned in the notice at the top of the document, the app does not concern itself with BMI, basal metabolic rate calculations or similar values.
Information such as weight is used only to calculate recommended nutrient intake; for example, some health organizations provide recommendations per kilogram of body weight.

**Price records**: records of product prices over time, prices for the same products at different stores, grocery bills, and meal costs.  
The app tracks this price-related data and generates graphs to help the user understand their spending habits and make informed grocery-shopping decisions.  
For example, the user can view the average cost of meals over time, compare
the prices of the same product at different stores, and review grocery bills
to identify opportunities to save money.

**General app behaviour**:

- Notifications: The app features no notifications.

- Data collection: The app does not collect telemetry about the user's behaviour or preferences, all data stays local.

- Import/export: It is possible to import and export (as JSON files) various kinds of data, such as the settings, the catalogue and the history of meals.  

- Cross-platform: built on top of the [Flet](https://flet.dev/) framework, Garum runs natively on multiple platforms without extra effort.

## Name origin

> This section is only a brief introduction to Garum.  
> It will not be kept up to date with the latest discoveries, for accurate information please consult appropriate sources.  

From Wikipedia (paraphrased): [Garum](https://en.wikipedia.org/wiki/Garum) is a fermented fish sauce that was used as a condiment in the cuisines of Phoenicia, ancient Greece, Rome, Carthage, and later Byzantium.  

When mixed with oenogarum (a popular wine-based Byzantine sauce), vinegar, black pepper and oil, garum was used as a flavour enhancer in various dishes such as boiled veal, steamed mussels or even pear-and-honey soufflè. When diluted with water to make hydrogarum it also served as a ration for Roman legions.
Although garum enjoyed its greatest popularity in the Western Mediterranean and the Roman world, it was in earlier use by the Greeks.  
The taste of garum is thought to have been comparable to that of today's Asian fish sauces.

Like modern fermented fish sauce and soy sauce, garum was a rich source of umami flavoring due to the presence of glutamates.  
It was used along with murri in medieval Byzantine and Arab cuisine to give a savory flavor to dishes.

Garum was also used as a medicine to treat conditions such as dog bites, dysentery, ulcers or as a chronic diarrhea relief among many other and as an ingredient in cosmetic preparations to remove unwanted hairs or freckles.

For further information, I highly recommend the dedicated Wikipedia page for [garum](https://en.wikipedia.org/wiki/Garum) and the excellent videos by Max Miller on his YouTube channel *Tasting History with Max Miller*.
Start with this [video](https://www.youtube.com/watch?v=ICZww0DtQKk).

## Running the app

The project uses a `src` layout. [`src/main.py`](src/main.py) is the single
Flet launcher discovered by `flet run`; application code is organized under
the `garum` package:

- `garum/gui` contains Flet views and theme definitions.
- `garum/handlers/models.py` contains immutable row/domain models and their database serialization rules; it does not access SQLite.
- `garum/handlers/storage.py` contains the SQLite connection/transaction boundary and repositories such as `FoodEntryRepository`; it returns models but does not define their shape.
- `garum/handlers/settings_handler.py` contains the independent JSON settings service.
- `src/assets` contains files packaged as Flet assets.
- `data/db.sql` is the SQLite schema used to initialize the local database.

### Theme palettes

Theme colors are exported from [`src/garum/gui/theme.py`](src/garum/gui/theme.py) as `LIGHT_PALETTE`, `DARK_PALETTE`, and `THEME_PALETTES`.  
The `APP_THEME` setting selects one of these palettes at startup.  
The light palette is based on desert sand with brown and clay UI surfaces; the dark palette is based on dark grey with black elevated surfaces and light grey controls.  
Both palettes use red for errors.

### uv

Run as a desktop app:

```bash
uv run flet run
```

Run as a web app:

```bash
uv run flet run --web
```

### flet command

Run as a desktop app (uv not necessary):

```bash
flet run
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/).

## Build the app

### Android

```bash
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```bash
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```bash
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```bash
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```bash
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).

### Web

```bash
flet build web -v
```

For more details on building Web app, refer to the [Web Packaging Guide](https://flet.dev/docs/publish/web/).

## Contributing

Contributions are welcome and much appreciated.  
Please read the [contributing guide](CONTRIBUTING.md) before opening an issue or submitting a pull request.

## License

Garum is distributed under the GNU General Public License v3.0.  
See the [LICENSE](LICENSE.txt) file for details.