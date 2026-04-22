# convert-audio

Nástroj pro přepis audio nahrávek z diktafonu pomocí OpenAI Whisper API.

## Struktura

```
convert-audio/
├── convert-audio.py      # původní jednorázový skript (archiv)
└── _prompt/
    ├── app.py            # hlavní Streamlit aplikace
    └── requirements.txt
```

## Spuštění aplikace

```bash
cd _prompt
pip install -r requirements.txt
streamlit run app.py
```

## Technologie

- **OpenAI Whisper API** (`whisper-1`) — transkripce
- **Streamlit** — UI
- Python 3.10+

## Konfigurace

API klíč se ukládá do `~/.audio_transcriber_config.json` (mimo repozitář).

## Šablony výstupu

| Šablona | Formát | Přípona |
|---------|--------|---------|
| Časová razítka | `[MM:SS] text` | `.txt` |
| Prostý text | kontinuální text | `.txt` |
| Titulky SRT | standardní SRT | `.srt` |
| Protokol ze schůzky | hlavička + razítka | `.txt` |
| Interview formát | střídání T:/R: | `.txt` |

## Podporované formáty

m4a, mp3, wav, ogg, flac, webm, mp4 — limit Whisper API je 25 MB.

## Bezpečnost

API klíč nikdy nepatří do kódu ani do repozitáře. Původní `convert-audio.py`
obsahoval exponovaný klíč — **revokovat na platform.openai.com**.
