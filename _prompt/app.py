import os
import json
import subprocess
import tempfile
import streamlit as st
from pathlib import Path
from openai import OpenAI

WHISPER_LIMIT_BYTES = 25 * 1024 * 1024  # 26,214,400 B

CONFIG_FILE = Path.home() / ".audio_transcriber_config.json"
IS_CLOUD = Path.home() == Path("/home/appuser")  # Streamlit Cloud home dir

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

def load_saved_key() -> str:
    if IS_CLOUD:
        return ""  # never load from file on shared cloud container
    try:
        if CONFIG_FILE.exists():
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return data.get("api_key", "")
    except Exception:
        pass
    return ""


def save_key(key: str) -> bool:
    if IS_CLOUD:
        return False  # session_state only on cloud
    try:
        CONFIG_FILE.write_text(
            json.dumps({"api_key": key}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return True
    except Exception:
        return False


def get_duration_seconds(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def compress_audio(src_path: str) -> str:
    """Převede audio na mono MP3 s bitrate voleným tak, aby se vešel pod limit Whisper API."""
    duration = get_duration_seconds(src_path)
    target_bits = WHISPER_LIMIT_BYTES * 8 * 0.9  # 10% rezerva
    bitrate_kbps = max(16, min(64, int(target_bits / duration / 1000)))
    dst_path = src_path + f"_compressed_{bitrate_kbps}k.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-i", src_path, "-ac", "1", "-b:a", f"{bitrate_kbps}k", dst_path],
        capture_output=True, check=True,
    )
    return dst_path


def transcribe(api_key: str, audio_bytes: bytes, filename: str, language: str | None):
    client = OpenAI(api_key=api_key)
    suffix = Path(filename).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    compressed_path = None
    try:
        upload_path = tmp_path
        if os.path.getsize(tmp_path) > WHISPER_LIMIT_BYTES:
            compressed_path = compress_audio(tmp_path)
            upload_path = compressed_path
        with open(upload_path, "rb") as f:
            kwargs = dict(model="whisper-1", file=f, response_format="verbose_json")
            if language:
                kwargs["language"] = language
            return client.audio.transcriptions.create(**kwargs)
    finally:
        os.unlink(tmp_path)
        if compressed_path and os.path.exists(compressed_path):
            os.unlink(compressed_path)


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


# ── session state init ───────────────────────────────────────────────────────

if "api_key" not in st.session_state:
    st.session_state.api_key = load_saved_key()

# ── UI ───────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Audio Přepis", page_icon="🎤", layout="wide")
st.title("🎤 Audio Přepis")

with st.sidebar:
    st.header("Nastavení API")
    key_input = st.text_input(
        "OpenAI API klíč",
        value=st.session_state.api_key,
        type="password",
        placeholder="sk-...",
    )

    if st.button("💾 Uložit API klíč"):
        if key_input.startswith("sk-"):
            st.session_state.api_key = key_input
            saved = save_key(key_input)
            if saved:
                st.success("Klíč uložen lokálně.")
            else:
                st.success("Klíč uložen pro tuto relaci.")
        else:
            st.error("Klíč musí začínat 'sk-'")

    st.divider()
    if IS_CLOUD:
        st.caption("🔒 Online verze: klíč platí jen pro tuto relaci — po zavření záložky zmizí.")
    else:
        st.caption("🔒 Klíč uložen lokálně. Odesílá se pouze na OpenAI API.")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded = st.file_uploader(
        "Nahrát audio soubor",
        type=["m4a", "mp3", "wav", "ogg", "flac", "webm", "mp4"],
        help="Limit OpenAI Whisper API: 25 MB. Větší soubory se automaticky zkomprimují.",
    )

with col2:
    template_label = st.selectbox("Šablona výstupu", list(TEMPLATES.keys()))
    lang_label = st.selectbox("Jazyk nahrávky", list(LANGUAGES.keys()))

if uploaded:
    st.info(f"Soubor: **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

    if st.button("▶ Přepsat", type="primary"):
        key = st.session_state.api_key
        if not key:
            st.error("Zadejte a uložte API klíč v postranním panelu.")
        else:
            with st.spinner("Přepisuji… může trvat chvíli."):
                try:
                    result = transcribe(key, uploaded.read(), uploaded.name, LANGUAGES[lang_label])
                    stem = Path(uploaded.name).stem
                    output_text, output_filename = format_output(result, TEMPLATES[template_label], stem)

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
