# 🎤 Audio Přepis

Jednoduchá webová aplikace pro přepis audio nahrávek z diktafonu pomocí OpenAI Whisper API. Spustíš lokálně, nahraješ soubor, vyběreš šablonu — dostaneš textový soubor.

![Screenshot aplikace](screenshot/screenshot.png)

---

## Funkce

- Uložení API klíče (bezpečně lokálně, mimo repozitář)
- Upload audio souboru přes prohlížeč
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

## Jak začít

### 1. Získej OpenAI API klíč

1. Jdi na [platform.openai.com](https://platform.openai.com)
2. Zaregistruj se nebo přihlas
3. V menu vyber **API keys** → **Create new secret key**
4. Klíč si zkopíruj — zobrazí se jen jednou

> Whisper API je placená služba. Cena je přibližně **$0.006 za minutu** nahrávky.  
> Nový účet dostane kredit zdarma na vyzkoušení.

### 2. Nainstaluj závislosti

```bash
git clone https://github.com/trnkapavel/convert-audio.git
cd convert-audio/_prompt
pip install -r requirements.txt
```

### 3. Spusť aplikaci

```bash
streamlit run app.py
```

Aplikace se otevře v prohlížeči na `http://localhost:8501`.

### 4. Zadej API klíč

V levém panelu zadej svůj OpenAI API klíč a klikni **Uložit API klíč**.  
Klíč se uloží do `~/.audio_transcriber_config.json` — zůstane jen u tebe, nikam se neodesílá.

---

## Použití

1. Nahraj audio soubor (drag & drop nebo Browse files)
2. Vyber šablonu výstupu
3. Vyber jazyk nahrávky
4. Klikni **Přepsat**
5. Stáhni výsledný soubor

---

## Požadavky

- Python 3.10+
- OpenAI API klíč
- Internetové připojení (Whisper API je cloudová služba)

---

## Bezpečnost

API klíč se **nikdy neukládá do repozitáře** — je uložen pouze lokálně v `~/.audio_transcriber_config.json`.

---

## Licence

MIT
