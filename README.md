# Garum

> **Notice:** Garum does not provide medical advice and is not intended to do so.  
> The app displays numbers derived from guidelines and recommendations published by health experts.  
> Before making any significant lifestyle change, please consult a qualified medical professional.  
> The app and its creators accept no responsibility for any outcome resulting from the misuse of, or failure to follow, the above guidance.  
> The sole purpose of this app is to track data and compute trends related to nutrition.

## Purpose

As a university student juggling lectures, associations, homework, side projects, etc... I found it increasingly difficult to keep track of my nutrition and food spending.  
Good nutrition is essential for sustaining that level of activity, yet tracking it mentally or on paper quickly becomes inaccurate and tedious.  
Garum was built to solve that problem, it simplifies data entry and, among other features, provides a rough (non-medical) evaluation of macronutrient intake based on guidelines from recognised health authorities such as the [World Health Organization (WHO)](https://www.who.int/) and the [American Heart Association (AHA)](https://www.heart.org/).

## Features

- **Cross-platform by design**: built on top of the [Flet](https://flet.dev/) framework, Garum runs natively on multiple platforms without extra effort.
- **Encrypted backups & sync**: your data is backed up and synchronised securely via Google Drive cloud storage.
- **Interactive graphs**: visualise your data by time span, individual macronutrient, or money spent.
- **Macronutrient evaluations**: see what percentage of a recommended limit you have consumed (e.g. 40% of the suggested 25g of sugar). Limits and their sources are fully customisable, set them manually or choose from built-in presets such as [WHO](https://www.who.int/) or [AHA](https://www.heart.org/) guidelines.

## Origin of the name

From Wikipedia (paraphrased): [Garum](https://en.wikipedia.org/wiki/Garum) is a fermented fish sauce that was used as a condiment in the cuisines of Phoenicia, ancient Greece, Rome, Carthage, and later Byzantium.  

When mixed with oenogarum, vinegar, black pepper and oil garum was used as a flavour enhancer in various dishes such as boiled veal, steamed mussels or even pear-and-honey soufflè. When diluted with water to make hydrogarum it also served as a ration for Roman legions.
Although garum enjoyed its greatest popularity in the Western Mediterranean and the Roman world, it was in earlier use by the Greeks.  
The taste of garum is thought to have been comparable to that of today's Asian fish sauces.

Like modern fermented fish sauce and soy sauce, garum was a rich source of umami flavoring due to the presence of glutamates.  
It was used along with murri in medieval Byzantine and Arab cuisine to give a savory flavor to dishes.

Garum was also used as a medicine to treat conditions such as dog bites, dysentery, ulcers or as a chronic diarrhea relief among many other and as an ingredient for cosmetic preparations to tread unwanted hairs or freckles.

For further information, I highly recommend the excellent videos by Max Miller on his YouTube channel *Tasting History with Max Miller*.
Start with this [video](https://www.youtube.com/watch?v=ICZww0DtQKk).

## Contributing

Contributions are welcome and much appreciated.  
Please read the [contributing guide](CONTRIBUTING.md) before opening an issue or submitting a pull request.

## License

Garum is distributed under the GNU General Public License v3.0. See the [LICENSE](LICENSE.txt) file for details.

## Running the app

### Theme palettes

Theme colors are exported from [`src/theme.py`](src/theme.py) as
`LIGHT_PALETTE`, `DARK_PALETTE`, and `THEME_PALETTES`. The `APP_THEME` setting
selects one of these palettes at startup. The light palette is based on desert
sand with brown and clay UI surfaces; the dark palette is based on dark grey
with black elevated surfaces and light grey controls. Both palettes use red
for errors.

### uv

Run as a desktop app:

```bash
uv run flet run
```

Run as a web app:

```bash
uv run flet run --web
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
