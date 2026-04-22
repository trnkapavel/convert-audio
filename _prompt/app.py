import os
import json
import tempfile
import streamlit as st
from pathlib import Path
from openai import OpenAI

CONFIG_FILE = Path.home() / ".audio_transcriber_config.json"

TEMPLATES = {
    "Časová razítka [MM:SS]": "timestamps",
    "Prostý text": "plain",
    "Titulky SRT": "srt",
    "Protokol ze schůzky": "meeting",
    "Interview formát": "interview",
}

LANGUAGES = {
    "Čeština": "cs",
    "Slovenština": "sk",
    "Angličtina": "en",
    "Němčina": "de",
    "Automaticky": None,
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(config: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def transcribe(api_key: str, audio_bytes: bytes, filename: str, language: str | None):
    client = OpenAI(api_key=api_key)
    suffix = Path(filename).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with open(tmp_path, "rb") as f:
            kwargs = dict(model="whisper-1", file=f, response_format="verbose_json")
            if language:
                kwargs["language"] = language
            result = client.audio.transcriptions.create(**kwargs)
    finally:
        os.unlink(tmp_path)
    return result


def fmt_time(seconds: float) -> str:
    mm = int(seconds) // 60
    ss = int(seconds) % 60
    return f"{mm:02d}:{ss:02d}"


def fmt_srt_time(seconds: float) -> str:
    h = int(seconds) // 3600
    m = (int(seconds) % 3600) // 60
    s = int(seconds) % 60
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_output(result, template: str, stem: str) -> tuple[str, str]:
    segs = result.segments

    if template == "timestamps":
        lines = [f"[{fmt_time(s.start)}] {s.text.strip()}" for s in segs]
        return "\n".join(lines), f"{stem}_prepis.txt"

    if template == "plain":
        return " ".join(s.text.strip() for s in segs), f"{stem}_prepis.txt"

    if template == "srt":
        blocks = []
        for i, s in enumerate(segs, 1):
            blocks.append(f"{i}\n{fmt_srt_time(s.start)} --> {fmt_srt_time(s.end)}\n{s.text.strip()}")
        return "\n\n".join(blocks), f"{stem}.srt"

    if template == "meeting":
        header = [f"PROTOKOL ZE SCHŮZKY", "=" * 40, f"Soubor: {stem}", ""]
        body = [f"[{fmt_time(s.start)}] {s.text.strip()}" for s in segs]
        return "\n".join(header + body), f"{stem}_protokol.txt"

    if template == "interview":
        lines = []
        for i, s in enumerate(segs):
            prefix = "T:" if i % 2 == 0 else "R:"
            lines.append(f"{prefix} [{fmt_time(s.start)}] {s.text.strip()}")
        return "\n".join(lines), f"{stem}_interview.txt"

    return "", f"{stem}.txt"


# ── UI ──────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Audio Přepis", page_icon="🎤", layout="wide")
st.title("🎤 Audio Přepis")

config = load_config()

with st.sidebar:
    st.header("Nastavení API")
    api_key = st.text_input(
        "OpenAI API klíč",
        value=config.get("api_key", ""),
        type="password",
        placeholder="sk-...",
    )
    if st.button("💾 Uložit API klíč"):
        if api_key.startswith("sk-"):
            config["api_key"] = api_key
            save_config(config)
            st.success("Klíč uložen.")
        else:
            st.error("Klíč musí začínat 'sk-'")

    st.divider()
    st.caption(f"Klíč uložen v: `{CONFIG_FILE}`")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded = st.file_uploader(
        "Nahrát audio soubor",
        type=["m4a", "mp3", "wav", "ogg", "flac", "webm", "mp4"],
        help="Maximální velikost závisí na limitu OpenAI Whisper API (25 MB).",
    )

with col2:
    template_label = st.selectbox("Šablona výstupu", list(TEMPLATES.keys()))
    lang_label = st.selectbox("Jazyk nahrávky", list(LANGUAGES.keys()))

if uploaded:
    st.info(f"Soubor: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

    if st.button("▶ Přepsat", type="primary", disabled=not uploaded):
        key = config.get("api_key", "") or api_key
        if not key:
            st.error("Zadejte a uložte API klíč v postranním panelu.")
        else:
            with st.spinner("Přepisuji… může trvat chvíli."):
                try:
                    result = transcribe(
                        key,
                        uploaded.read(),
                        uploaded.name,
                        LANGUAGES[lang_label],
                    )
                    stem = Path(uploaded.name).stem
                    output_text, output_filename = format_output(
                        result, TEMPLATES[template_label], stem
                    )

                    st.success("Přepis dokončen.")
                    st.text_area("Výsledek", output_text, height=450)
                    st.download_button(
                        "⬇ Stáhnout přepis",
                        data=output_text.encode("utf-8"),
                        file_name=output_filename,
                        mime="text/plain",
                    )
                except Exception as exc:
                    st.error(f"Chyba při přepisu: {exc}")
