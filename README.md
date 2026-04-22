# 🎤 Audio Přepis / Audio Transcription

> **[English below](#english)** · **[Česky níže](#česky)**

![Screenshot](screenshot/screenshot.png)

---

## English

A simple local web app for transcribing voice recorder audio using the OpenAI Whisper API. Upload a file, pick a template, download the result.

### Features

- Secure local API key storage (never touches the repo)
- Drag & drop audio upload
- 5 output templates
- Language selection
- Download result as `.txt` or `.srt`

### Output Templates

| Template | Example output |
|----------|---------------|
| Timestamps | `[01:23] Segment text` |
| Plain text | `Full transcript as one paragraph` |
| SRT subtitles | Standard subtitle format |
| Meeting minutes | Header + timestamps |
| Interview format | `Q: [00:05] Question` / `A: [00:12] Answer` |

### Supported formats

`m4a` `mp3` `wav` `ogg` `flac` `webm` `mp4` — Whisper API limit is **25 MB**.

---

### Getting started

#### 1. Get an OpenAI API key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API keys** → **Create new secret key**
4. Copy the key — it's shown only once

> Whisper API is a paid service. Pricing: ~**$0.006 per minute** of audio.  
> New accounts receive free credits to get started.

#### 2. Install dependencies

```bash
git clone https://github.com/trnkapavel/convert-audio.git
cd convert-audio/_prompt
pip install -r requirements.txt
```

#### 3. Run the app

```bash
streamlit run app.py
```

Opens in your browser at `http://localhost:8501`.

#### 4. Enter your API key

In the left sidebar, paste your OpenAI API key and click **Save API key**.  
It's stored locally in `~/.audio_transcriber_config.json` — never sent anywhere.

---

### Usage

1. Upload an audio file (drag & drop or Browse files)
2. Select an output template
3. Select the recording language
4. Click **Transcribe**
5. Download the result

---

### Requirements

- Python 3.10+
- OpenAI API key
- Internet connection (Whisper runs in the cloud)

---

### Security

The API key is **never stored in the repository** — only locally in `~/.audio_transcriber_config.json`.

---

### License

MIT

---

## Česky

Jednoduchá lokální webová aplikace pro přepis audio nahrávek z diktafonu pomocí OpenAI Whisper API. Nahraješ soubor, vyběreš šablonu, stáhneš textový soubor.

### Funkce

- Bezpečné lokální uložení API klíče (mimo repozitář)
- Nahrávání souborů přes prohlížeč (drag & drop)
- 5 šablon výstupu
- Výběr jazyka nahrávky
- Stažení výsledku jako `.txt` nebo `.srt`

### Šablony výstupu

| Šablona | Ukázka výstupu |
|---------|----------------|
| Časová razítka | `[01:23] Text segmentu` |
| Prostý text | `Celý přepis jako jeden odstavec` |
| Titulky SRT | Standardní formát pro video titulky |
| Protokol ze schůzky | Hlavička + časová razítka |
| Interview formát | `T: [00:05] Otázka` / `R: [00:12] Odpověď` |

### Podporované formáty

`m4a` `mp3` `wav` `ogg` `flac` `webm` `mp4` — limit Whisper API je **25 MB**.

---

### Jak začít

#### 1. Získej OpenAI API klíč

1. Jdi na [platform.openai.com](https://platform.openai.com)
2. Zaregistruj se nebo přihlas
3. V menu vyber **API keys** → **Create new secret key**
4. Klíč si zkopíruj — zobrazí se jen jednou

> Whisper API je placená služba. Cena: přibližně **$0.006 za minutu** nahrávky.  
> Nový účet dostane kredit zdarma na vyzkoušení.

#### 2. Nainstaluj závislosti

```bash
git clone https://github.com/trnkapavel/convert-audio.git
cd convert-audio/_prompt
pip install -r requirements.txt
```

#### 3. Spusť aplikaci

```bash
streamlit run app.py
```

Aplikace se otevře v prohlížeči na `http://localhost:8501`.

#### 4. Zadej API klíč

V levém panelu zadej OpenAI API klíč a klikni **Uložit API klíč**.  
Klíč se uloží do `~/.audio_transcriber_config.json` — zůstane jen u tebe.

---

### Použití

1. Nahraj audio soubor (drag & drop nebo Browse files)
2. Vyber šablonu výstupu
3. Vyber jazyk nahrávky
4. Klikni **Přepsat**
5. Stáhni výsledný soubor

---

### Požadavky

- Python 3.10+
- OpenAI API klíč
- Internetové připojení (Whisper API je cloudová služba)

---

### Bezpečnost

API klíč se **nikdy neukládá do repozitáře** — je uložen pouze lokálně v `~/.audio_transcriber_config.json`.

---

### Licence

MIT
