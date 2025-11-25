# 🔧 HoloMind Local Run Playbook

This playbook translates the high-level documentation from [README.md](README.md) into an actionable, security-aware checklist for bringing HoloMind online on a single workstation.

---

## 1. Prerequisites & Security Notes

1. **Hardware**
   - HDMI display capable of 1080p or higher.
   - Reflective hologram pyramid/cone (25–50 cm base recommended).
   - Microphone and USB webcam if voice/gesture input are required.
   - NVIDIA/AMD GPU with recent drivers for best rendering performance.
2. **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 20.04+.
3. **Python**: Version 3.8–3.11. Verify via `python --version` before setup.
4. **GPU Drivers**: Ensure CUDA/cuDNN (for NVIDIA) or ROCm (for AMD) is installed if you need acceleration.
5. **API Keys**
   - Treat **OpenAI/Anthropic API keys as secrets**. Never hard-code them in source files or commit them to git.
   - Use environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) or a secrets manager.
   - If a plaintext key is provided for testing (e.g., `sk-proj-...`), store it only in your local `.env` or shell session and rotate it afterwards.
6. **Network Access**: Outbound HTTPS connectivity to OpenAI/Anthropic endpoints.

> ⚠️ **Security Reminder**: Double-check `.gitignore` to ensure `config.json`, `.env`, or `memories/` directories storing customer data are not tracked.

---

## 2. Environment Setup Checklist

| Step | Command | Notes |
|------|---------|-------|
| 1 | `git clone https://github.com/yourusername/holomind.git` | Or copy the workspace into your projects directory. |
| 2 | `cd holomind` | All subsequent commands assume this root. |
| 3 | `python -m venv venv` | Replace `python` with `python3` on macOS/Linux if needed. |
| 4 | `venv\Scripts\activate` *(Windows)* or `source venv/bin/activate` *(Unix)* | The prompt should show `(venv)` afterwards. |
| 5 | `pip install --upgrade pip` | Keeps tooling current. |
| 6 | `pip install -r requirements.txt` | Installs AI/vision/audio dependencies. Expect large downloads (Torch, transformers). |
| 7 | *(Optional GPU)* `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118` | Ensure CUDA 11.8 drivers exist. |
| 8 | `pip install -r requirements-dev.txt` *(optional)* | If you plan to run tests/linting. |

Verification:
```bash
python - <<'PY'
import cv2, numpy, torch, transformers, anthropic
print('✅ Core libraries OK')
print('CUDA available:', torch.cuda.is_available())
PY
```

---

## 3. Configuration & API Key Management

1. **Environment Variables**
   ```bash
   # PowerShell
   setx OPENAI_API_KEY "sk-proj-XXXX"
   setx ANTHROPIC_API_KEY "your-anthropic-key"

   # macOS/Linux (bash/zsh)
   export OPENAI_API_KEY="sk-proj-XXXX"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   ```
   - Restart the terminal (or use `set OPENAI_API_KEY=...` for current session).
2. **config.json Template**
   ```json
   {
     "api_key": "ENV",                // Read from env variables only
     "use_claude": false,              // Set true to prioritize Anthropic
     "agent_name": "Luma",
     "display_settings": {
       "resolution": 1024,
       "fps": 30,
       "fullscreen": false,
       "hdmi_output": true
     },
     "hologram_settings": {
       "projection_type": "pyramid",
       "base_diameter_cm": 30,
       "height_cm": 25
     },
     "features": {
       "voice_enabled": true,
       "gesture_recognition": false
     }
   }
   ```
   - When `api_key` = `"ENV"`, adjust `holomind-core.py` to read `os.getenv("OPENAI_API_KEY")` or `ANTHROPIC_API_KEY`.
3. **Secrets Hygiene**
   - Keep API keys out of logs (`logging` level INFO or lower for sensitive data).
   - Rotate the provided key (`sk-proj-...`) once integration testing concludes.

---

## 4. Calibration & Hardware Setup

1. Connect the HDMI display, extend desktop (Windows `Win+P` → Extend, macOS Display Arrangement, `xrandr` on Linux).
2. Center your holographic reflector on the region where the projection will appear.
3. Launch calibration utility:
   ```bash
   python calibrate.py --profile default
   ```
4. Follow on-screen prompts:
   - Adjust square size/position with arrow keys or gesture controls.
   - Press `S` to save (writes to `calibration_profiles.json`).
5. Verify `calibration_profiles.json` contains entries similar to:
   ```json
   {
     "living_room_tv": {
       "display_width": 1920,
       "display_height": 1080,
       "projection_x": 960,
       "projection_y": 540,
       "projection_size": 800,
       "reflector_type": "pyramid"
     }
   }
   ```
6. Ensure ambient lighting is dimmed and reflective surfaces are clean to maximize contrast.

---

## 5. Launch Workflows

### 5.1 Basic Conversation Mode
```bash
source venv/bin/activate
python holomind-core.py --config config.json --profile living_room_tv
```
Expected output:
```
[HoloMind] Initializing consciousness...
[Luma] Hello! I'm Luma...
```
The OpenCV projection window (`HoloMind Projection`) should mirror the 4-view hologram layout.

### 5.2 Mode Variants
| Mode | Command | Notes |
|------|---------|-------|
| Gesture | `python holomind-core.py --mode gesture` | Requires webcam; verify MediaPipe access. |
| Data Viz | `python holomind-core.py --mode data_viz --data datasets/portfolio.json` | Provide valid JSON payload. |
| Learning | `python holomind-core.py --mode learning --curriculum configs/courses/banking.json` | Aligns with educational content. |
| Meditation | `python holomind-core.py --mode meditation --theme aurora` | Minimal input, focuses on visuals. |
| Kiosk | `python holomind-core.py --kiosk-mode --fullscreen` | Hides cursor, ideal for installations. |

### 5.3 Voice Output
Uncomment `self._speak_response(...)` inside [`holomind-core.py`](holomind-core.py:702-708) to enable TTS once drivers are confirmed.

---

## 6. Troubleshooting & Validation

| Symptom | Checks | Fix |
|---------|--------|-----|
| `ImportError: No module named 'cv2'` | `pip show opencv-python` | Reinstall `opencv-python`; ensure only one OpenCV package. |
| `torch.cuda.is_available() == False` | `nvidia-smi` output | Reinstall CUDA-compatible Torch wheel, update drivers. |
| Blank projection window | Confirm calibration profile, HDMI position, `projection_size`. | Re-run `calibrate.py`, lower resolution to 720p for testing. |
| No voice input/output | Check OS microphone permissions, `SpeechRecognition` installation. | On Linux add user to `audio` group, on macOS grant mic access. |
| API 401/429 errors | Validate `OPENAI_API_KEY`, rate limits. | Rotate key, slow request cadence, verify billing. |
| Crashes after several minutes | Monitor memory via `psutil`, check logs. | Reduce particle count (`max_particles`: 500), enable `--monitor-performance`. |

Validation script:
```bash
python test_setup.py
```
Confirms core imports, GPU availability, display pipeline, and API key presence.

---

## 7. Handoff Plan for Implementation Mode

1. **Confirm Requirements**: Ensure steps 1–3 above are complete (prereqs, environment, config). Document outcomes in `RUN_LOCAL.md`.
2. **Prepare Assets**: Collect calibration profiles, data files, and optional audio/gesture inputs.
3. **Switch to Code/Debug Mode**: Execute the commands in Section 5, capturing console logs and screenshots for verification.
4. **Log Issues**: Populate a troubleshooting checklist if any symptoms arise and loop back through Section 6.
5. **Finalize**: Once the hologram renders and the agent responds with audio/text, note the environment details (OS, GPU, driver versions, API endpoints) for future reproducibility.

Let me know once you’re ready, and I can guide the next mode through the exact commands and validation steps.


---

## 8. Fresh Machine Quickstart (Copy/Paste Friendly)

> Use this when nothing is installed yet. Replace `<your-openai-key>` with the real secret (e.g., the provided `sk-proj-...`). On Windows run in PowerShell; on macOS/Linux use a bash shell.

```bash
# 1. Clone repo and enter workspace
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/yourusername/holomind.git
cd holomind

# 2. Create & activate virtual environment
python -m venv venv
# Windows PowerShell
./venv/Scripts/Activate.ps1
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies (base + optional GPU)
pip install --upgrade pip
pip install -r requirements.txt
# (Optional NVIDIA GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. Provide API keys for this terminal session
# PowerShell
$env:OPENAI_API_KEY="<your-openai-key>"
$env:ANTHROPIC_API_KEY="<your-anthropic-key>"
# bash/zsh
export OPENAI_API_KEY="<your-openai-key>"
export ANTHROPIC_API_KEY="<your-anthropic-key>"

# 5. Generate default config if missing
python - <<'PY'
import json, pathlib
cfg = pathlib.Path('config.json')
if not cfg.exists():
    cfg.write_text(json.dumps({
        "api_key": "ENV",
        "use_claude": False,
        "agent_name": "Luma",
        "display_settings": {"resolution": 1024, "fps": 30,
                                "fullscreen": False, "hdmi_output": True},
        "hologram_settings": {"projection_type": "pyramid",
                               "base_diameter_cm": 30, "height_cm": 25}
    }, indent=4))
    print("Created config.json (reads keys from env)")
else:
    print("config.json already exists")
PY

# 6. (Optional) Run calibration once display is ready
python calibrate.py --profile living_room_tv

# 7. Launch HoloMind
python holomind-core.py --config config.json --profile living_room_tv
```

**Next actions:**
1. Run each block sequentially on your machine.
2. Capture console output (especially errors) so we can debug quickly.
3. Once the OpenCV window appears and Luma speaks, proceed with specialized modes as needed.
