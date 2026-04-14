#!/usr/bin/env python3
import os
import re
import uuid
import tempfile
import subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)

DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "tfp_dldr"
DOWNLOAD_DIR.mkdir(exist_ok=True)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>TFP DLDR</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Inter:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --navy: #07243E;
  --navy-light: #0d3560;
  --navy-dark: #041828;
  --lime: #BEE515;
  --lime-dark: #a0c510;
  --white: #ffffff;
  --muted: rgba(255,255,255,0.4);
  --danger: #ff5a5a;
}

html, body {
  height: 100%;
}

body {
  font-family: 'Inter', sans-serif;
  background: var(--navy-dark);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

/* Background texture */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse at 0% 0%, rgba(190,229,21,0.07) 0%, transparent 55%),
    radial-gradient(ellipse at 100% 100%, rgba(7,36,62,0.9) 0%, transparent 60%);
  pointer-events: none;
}

body::after {
  content: '';
  position: fixed;
  inset: 0;
  background-image: radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
}

.container {
  width: 100%;
  max-width: 560px;
  position: relative;
  z-index: 1;
}

/* Logo */
.logo-wrap {
  margin-bottom: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.logo {
  font-family: 'Montserrat', sans-serif;
  font-weight: 900;
  font-size: 3.2rem;
  letter-spacing: 0.06em;
  color: var(--white);
  line-height: 1;
}

.logo span {
  color: var(--lime);
}

.tagline {
  font-size: 0.8rem;
  font-weight: 300;
  color: var(--muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

/* Card */
.card {
  background: var(--navy);
  border: 1px solid rgba(190,229,21,0.15);
  border-radius: 20px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.04),
    0 24px 64px rgba(0,0,0,0.5);
}

.label {
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--lime);
  margin-bottom: 0.4rem;
}

.input-row {
  display: flex;
  gap: 0.6rem;
}

input[type="text"] {
  flex: 1;
  background: var(--navy-dark);
  border: 1.5px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 0.85rem 1.1rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.88rem;
  color: var(--white);
  outline: none;
  transition: border-color 0.2s;
}
input[type="text"]:focus {
  border-color: var(--lime);
}
input[type="text"]::placeholder {
  color: rgba(255,255,255,0.2);
}

button#goBtn {
  background: var(--lime);
  color: var(--navy-dark);
  border: none;
  border-radius: 12px;
  padding: 0.85rem 1.6rem;
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
  white-space: nowrap;
}
button#goBtn:hover { background: var(--lime-dark); }
button#goBtn:active { transform: scale(0.97); }
button#goBtn:disabled {
  background: rgba(190,229,21,0.3);
  color: rgba(7,36,62,0.5);
  cursor: not-allowed;
}

/* Status */
.status {
  display: none;
  align-items: center;
  gap: 0.8rem;
  font-size: 0.82rem;
  color: var(--muted);
}
.status.visible { display: flex; }

.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.1);
  border-top-color: var(--lime);
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Result */
.result {
  display: none;
  background: var(--lime);
  border-radius: 12px;
  padding: 1.1rem 1.3rem;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.result.visible { display: flex; }

.result-info strong {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--navy-dark);
  margin-bottom: 2px;
  word-break: break-all;
  line-height: 1.3;
}
.result-info small {
  font-size: 0.72rem;
  color: rgba(4,24,40,0.6);
}

.dl-btn {
  background: var(--navy-dark);
  color: var(--lime);
  border: none;
  border-radius: 8px;
  padding: 0.65rem 1.2rem;
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 0.82rem;
  letter-spacing: 0.05em;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background 0.15s;
}
.dl-btn:hover { background: var(--navy); }

/* Error */
.error {
  display: none;
  background: rgba(255,90,90,0.1);
  border: 1px solid rgba(255,90,90,0.3);
  border-radius: 10px;
  padding: 0.9rem 1rem;
  font-size: 0.82rem;
  color: var(--danger);
  line-height: 1.5;
}
.error.visible { display: block; }

/* Divider */
.divider {
  height: 1px;
  background: rgba(255,255,255,0.06);
}

/* Steps */
.steps {
  display: flex;
  gap: 1.2rem;
}
.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  text-align: center;
}
.step-num {
  width: 28px; height: 28px;
  border-radius: 50%;
  background: rgba(190,229,21,0.12);
  border: 1px solid rgba(190,229,21,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 0.7rem;
  color: var(--lime);
}
.step p {
  font-size: 0.72rem;
  color: var(--muted);
  line-height: 1.4;
}

.arrow {
  color: rgba(190,229,21,0.3);
  font-size: 1rem;
  align-self: center;
  margin-top: -8px;
}

/* Footer */
.footer {
  margin-top: 1.5rem;
  font-size: 0.68rem;
  color: rgba(255,255,255,0.2);
  text-align: center;
  letter-spacing: 0.04em;
}
</style>
</head>
<body>
<div class="container">
  <div class="logo-wrap">
    <div class="logo">TFP <span>DLDR</span></div>
    <div class="tagline">YouTube Shorts &rarr; MP4 &bull; Internal Tool</div>
  </div>

  <div class="card">
    <div>
      <div class="label">Paste your link</div>
      <div class="input-row">
        <input type="text" id="urlInput" placeholder="https://youtube.com/shorts/..." autocomplete="off"/>
        <button id="goBtn" onclick="startDownload()">DOWNLOAD</button>
      </div>
    </div>

    <div class="status" id="status">
      <div class="spinner"></div>
      <span id="statusText">Fetching video — this takes about 15 seconds...</span>
    </div>

    <div class="result" id="result">
      <div class="result-info">
        <strong id="resultTitle"></strong>
        <small id="resultMeta"></small>
      </div>
      <a class="dl-btn" id="dlLink" href="#" download>&#8595; MP4</a>
    </div>

    <div class="error" id="error"></div>

    <div class="divider"></div>

    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <p>Paste a YouTube Shorts link above</p>
      </div>
      <div class="arrow">›</div>
      <div class="step">
        <div class="step-num">2</div>
        <p>Hit Download and wait ~15 sec</p>
      </div>
      <div class="arrow">›</div>
      <div class="step">
        <div class="step-num">3</div>
        <p>Click the MP4 button to save</p>
      </div>
    </div>
  </div>

  <p class="footer">TFP Internal Tool &bull; Personal use only &bull; Respect creator copyrights</p>
</div>

<script>
async function startDownload() {
  const url = document.getElementById('urlInput').value.trim();
  if (!url) { showError('Please paste a YouTube Shorts link first.'); return; }

  setStatus('Fetching video — this takes about 15 seconds...', true);
  hideResult();
  hideError();
  document.getElementById('goBtn').disabled = true;

  try {
    const res = await fetch('/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      showError(data.error || 'Something went wrong. Try again.');
    } else {
      showResult(data);
    }
  } catch (e) {
    showError('Could not connect. Please try refreshing the page.');
  } finally {
    setStatus('', false);
    document.getElementById('goBtn').disabled = false;
  }
}

document.getElementById('urlInput').addEventListener('keydown', e => {
  if (e.key === 'Enter') startDownload();
});

function setStatus(text, visible) {
  document.getElementById('statusText').textContent = text;
  document.getElementById('status').classList.toggle('visible', visible);
}
function showResult(data) {
  document.getElementById('resultTitle').textContent = data.filename;
  document.getElementById('resultMeta').textContent = data.size + ' · 1080p MP4 · Ready to save';
  document.getElementById('dlLink').href = '/file/' + data.token;
  document.getElementById('dlLink').download = data.filename;
  document.getElementById('result').classList.add('visible');
}
function hideResult() { document.getElementById('result').classList.remove('visible'); }
function showError(msg) {
  const el = document.getElementById('error');
  el.textContent = '⚠ ' + msg;
  el.classList.add('visible');
}
function hideError() { document.getElementById('error').classList.remove('visible'); }
</script>
</body>
</html>
"""

_files: dict[str, Path] = {}

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(force=True)
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "No URL provided."}), 400

    if "youtube.com/shorts" not in url and "youtu.be" not in url and "youtube.com/watch" not in url:
        return jsonify({"error": "That doesn't look like a YouTube link. Please copy the link directly from the YouTube app or website."}), 400

    token = uuid.uuid4().hex
    out_dir = DOWNLOAD_DIR / token
    out_dir.mkdir(parents=True, exist_ok=True)

    output_template = str(out_dir / "%(title).60s [%(id)s].%(ext)s")

    cookies_path = Path(__file__).parent / "cookies.txt"
    cmd = [
        "yt-dlp",
        "--format",
        ("bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/"
         "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best"),
        "--merge-output-format", "mp4",
        "--output", output_template,
        "--no-playlist",
        "--quiet",
    ]
    if cookies_path.exists():
        cmd += ["--cookies", str(cookies_path)]
    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        err = result.stderr.strip().splitlines()
        msg = err[-1] if err else "Download failed."
        msg = re.sub(r'\x1b\[[0-9;]*m', '', msg)
        return jsonify({"error": msg}), 500

    files = list(out_dir.glob("*.mp4"))
    if not files:
        return jsonify({"error": "Download finished but no MP4 was found. Try again."}), 500

    filepath = files[0]
    size_bytes = filepath.stat().st_size
    size_str = f"{size_bytes / 1_048_576:.1f} MB" if size_bytes > 1_048_576 else f"{size_bytes // 1024} KB"

    _files[token] = filepath

    return jsonify({"token": token, "filename": filepath.name, "size": size_str})

@app.route("/file/<token>")
def serve_file(token):
    filepath = _files.get(token)
    if not filepath or not filepath.exists():
        return "File not found or expired.", 404
    return send_file(filepath, as_attachment=True, download_name=filepath.name, mimetype="video/mp4")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
