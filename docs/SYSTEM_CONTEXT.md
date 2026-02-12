# Vision X Sentinel — System Context & Architecture

This document provides a comprehensive overview of how the Vision X Sentinel system works: API calls, intervals, AI models, detection logic, and data flow.

---

## 1. Frontend API Calls When Video Plays

### 1.1 Frame Capture API (`POST /api/sentinel/analyze-frame`)

**When:** Every **1.5 seconds** while the video is playing

**How it works:**
- Frontend captures the current video frame using HTML5 Canvas (`drawImage` from `<video>` element)
- Converts frame to base64 JPEG (`canvas.toDataURL('image/jpeg', 0.8)`)
- Sends to backend: `POST http://localhost:5000/api/sentinel/analyze-frame`
- Request body: `{ "classroom_id": "1", "frame": "data:image/jpeg;base64,..." }`

**Interval:** `setInterval(..., 1500)` — fires every 1500 milliseconds (1.5 seconds)

**Error handling:**
- If **3 consecutive** API calls fail (e.g. backend down), frame capture **stops**
- Retry check runs every **5 seconds** to test if server is back
- When server responds, frame capture **automatically resumes**

**Code location:** `frontend/src/components/ClassCard.jsx` (lines ~110-155)

---

### 1.2 Audio Level API (`POST /api/sentinel/audio-level`)

**When:** Every **1 second** while the video is playing

**How it works:**
- Frontend uses **Web Audio API** to capture audio from the video element
- Creates `AudioContext` → `createMediaElementSource(video)` → `AnalyserNode`
- Reads audio samples every second: `analyser.getByteTimeDomainData(buffer)`
- Computes **RMS (Root Mean Square)** from the audio buffer
- Normalizes to **0.0–1.0** range (not decibels)
- Sends to backend: `POST http://localhost:5000/api/sentinel/audio-level`
- Request body: `{ "classroom_id": "1", "level": 0.75 }` (0.0 = silence, 1.0 = max)

**Interval:** `setInterval(..., 1000)` — fires every 1000 milliseconds (1 second)

**Audio level calculation:**
```javascript
// Normalize each sample: (sample - 128) / 128
// Square each normalized value
// Sum all squares
// RMS = sqrt(sum / bufferLength)
// Clamp to 0.0-1.0
```

**Units:** **Normalized level (0.0–1.0)**, NOT decibels. This is a relative measure:
- `0.0` = silence (or muted)
- `0.5` = moderate audio
- `0.75` = loud (threshold for alerts)
- `1.0` = maximum audio level

**Code location:** `frontend/src/components/ClassCard.jsx` (lines ~80-97)

---

### 1.3 Alert Polling API (`GET /api/alerts`)

**When:** Every **3 seconds** (continuously, regardless of video state)

**How it works:**
- Frontend polls: `GET http://localhost:5000/api/alerts`
- Compares new alerts with previously seen alert IDs
- Shows **toast notification** for any new alert
- Updates "New alert" badge on classroom cards

**Interval:** `setInterval(..., 3000)` — fires every 3000 milliseconds (3 seconds)

**Code location:** `frontend/src/hooks/useAlerts.js`

---

## 2. Backend Detection Logic

### 2.1 Frame Analysis (`POST /api/sentinel/analyze-frame`)

**Endpoint:** `backend/app/api/sentinel.py` → `analyze_frame()`

**Process:**
1. **Decode frame:** Base64 string → BGR numpy array (OpenCV format)
2. **Person detection:** Run YOLOv8 on image → count persons
3. **Motion detection:** Compare current frame with previous frame → compute motion score
4. **Apply rules:**
   - **Empty Class Rule:** If 0 persons for ≥ 2 minutes → create alert
   - **Mischief Rule:** If high motion for 3 consecutive frames → create alert
5. **Store state:** Update per-classroom state (prev_frame, timers, counters)
6. **Return:** `{ classroom_id, person_count, motion_score, alert_created }`

**Code location:** `backend/app/api/sentinel.py` (lines ~30-78)

---

### 2.2 Audio Level Processing (`POST /api/sentinel/audio-level`)

**Endpoint:** `backend/app/api/sentinel.py` → `audio_level()`

**Process:**
1. **Receive level:** Get `audio_level` (0.0–1.0) from request body
2. **Apply Loud Noise Rule:** If level > 0.75 for 5 consecutive requests → create alert
3. **Store state:** Update per-classroom state (consecutive_high_audio counter)
4. **Return:** `{ classroom_id, audio_level, alert_created }`

**Code location:** `backend/app/api/sentinel.py` (lines ~83-122)

---

## 3. AI Models & Computer Vision

### 3.1 YOLOv8 (Person Detection)

**Model:** YOLOv8n (nano) — lightweight version for speed

**Library:** Ultralytics (`from ultralytics import YOLO`)

**What it does:**
- **Object detection** — detects objects in images
- **Person counting** — filters detections by class ID `0` (COCO "person" class)
- **Returns:** Number of persons in the frame

**How it works:**
1. Load model: `YOLO("yolov8n.pt")` — downloads automatically on first run (~6MB)
2. Run inference: `model(image, verbose=False)` — processes BGR numpy array
3. Filter results: Count boxes where `cls == 0` (person class)
4. Return count: Integer (0, 1, 2, ...)

**Performance:**
- CPU: ~50–200ms per inference
- GPU: ~10–50ms per inference
- Model size: ~6MB (nano version)

**Code location:** `backend/app/sentinel/vision.py` → `count_persons()`

**Use case:** Empty Class detection — if `person_count == 0` for 2+ minutes, create alert

---

### 3.2 OpenCV (Motion Detection)

**Library:** `cv2` (OpenCV)

**What it does:**
- **Frame differencing** — compares two consecutive frames
- **Motion score** — computes intensity of motion (0.0–1.0)

**How it works:**
1. Convert frames to grayscale: `cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)`
2. Compute absolute difference: `cv2.absdiff(gray_current, gray_prev)`
3. Calculate motion score:
   ```python
   total_diff = sum of all pixel differences
   max_possible_diff = image_size * 255
   motion_score = total_diff / max_possible_diff  # normalized to 0.0-1.0
   ```
4. Return score: Float (0.0 = no motion, 1.0 = maximum motion)

**Code location:** `backend/app/sentinel/vision.py` → `compute_motion_score()`

**Use case:** Mischief detection — if `motion_score > 0.3` for 3 consecutive frames, create alert

---

## 4. Detection Rules & Thresholds

All thresholds are defined in `backend/app/sentinel/rules.py`

### 4.1 Empty Class Detection

**Rule:** If classroom has **0 persons** for **≥ 2 minutes**, create "empty_class" alert

**Thresholds:**
- `EMPTY_CLASS_DURATION_SEC = 120` (2 minutes)

**Logic:**
1. When `person_count == 0`:
   - If `first_empty_time` is None → set it to current time
   - Else check elapsed time: if `(now - first_empty_time) >= 120 seconds` → create alert
2. When `person_count > 0`:
   - Reset `first_empty_time = None` (classroom is not empty)

**State stored:** `first_empty_time` (timestamp) per classroom

**Alert created:** `{ type: "empty_class", classroom_id, metadata: { empty_duration_sec } }`

---

### 4.2 Mischief Detection (High Motion)

**Rule:** If **motion score > 0.3** for **3 consecutive frames**, create "mischief" alert

**Thresholds:**
- `MOTION_THRESHOLD = 0.3` (motion score above this triggers increment)
- `MISCHIEF_CONSECUTIVE_COUNT = 3` (need 3 consecutive high-motion frames)
- `MISCHIEF_COOLDOWN_SEC = 60` (don't alert again for 60 seconds after an alert)

**Logic:**
1. Compute motion score between current frame and previous frame
2. If `motion_score > 0.3`:
   - Increment `consecutive_motion` counter
   - If `consecutive_motion >= 3` → create alert, reset counter, set cooldown
3. Else:
   - Reset `consecutive_motion = 0`

**State stored:** `consecutive_motion` (count), `prev_frame` (numpy array), `last_mischief_alert_time` (timestamp) per classroom

**Alert created:** `{ type: "mischief", classroom_id, metadata: { motion_score } }`

**Timing:** With 1.5s interval, 3 frames = ~4.5 seconds of sustained high motion

---

### 4.3 Loud Noise Detection

**Rule:** If **audio level > 0.75** for **5 consecutive requests**, create "loud_noise" alert

**Thresholds:**
- `LOUD_NOISE_THRESHOLD = 0.75` (audio level above this triggers increment)
- `LOUD_NOISE_CONSECUTIVE_COUNT = 5` (need 5 consecutive high-level requests)
- `LOUD_NOISE_COOLDOWN_SEC = 60` (don't alert again for 60 seconds after an alert)

**Logic:**
1. Receive audio level (0.0–1.0) from frontend
2. If `audio_level > 0.75`:
   - Increment `consecutive_high_audio` counter
   - If `consecutive_high_audio >= 5` → create alert, reset counter, set cooldown
3. Else:
   - Reset `consecutive_high_audio = 0`

**State stored:** `consecutive_high_audio` (count), `last_loud_noise_alert_time` (timestamp) per classroom

**Alert created:** `{ type: "loud_noise", classroom_id, metadata: { audio_level } }`

**Timing:** With 1s interval, 5 requests = 5 seconds of sustained loud noise

**Audio level units:** Normalized 0.0–1.0 (NOT decibels). This is RMS (Root Mean Square) computed from audio samples and normalized.

---

## 5. Per-Classroom State Management

**Storage:** In-memory Python dictionary (`_state`) keyed by `classroom_id`

**Structure:**
```python
_state = {
    "1": {
        "first_empty_time": None,           # timestamp for empty class timer
        "prev_frame": None,                 # numpy array for motion comparison
        "consecutive_motion": 0,            # count for mischief detection
        "last_mischief_alert_time": None,   # cooldown timestamp
        "consecutive_high_audio": 0,        # count for loud noise detection
        "last_loud_noise_alert_time": None, # cooldown timestamp
    },
    "2": { ... },
    ...
}
```

**Thread safety:** Each classroom has a `threading.Lock()` to prevent race conditions when multiple API requests arrive simultaneously for the same classroom.

**Code location:** `backend/app/sentinel/rules.py` → `_get_state()`, `_get_lock()`

---

## 6. API Call Summary Table

| API Endpoint | When | Interval | Request Body | Response |
|--------------|------|----------|--------------|----------|
| **POST /api/sentinel/analyze-frame** | Video playing | **1.5 seconds** | `{ classroom_id, frame (base64) }` | `{ person_count, motion_score, alert_created }` |
| **POST /api/sentinel/audio-level** | Video playing | **1 second** | `{ classroom_id, level (0.0-1.0) }` | `{ audio_level, alert_created }` |
| **GET /api/alerts** | Always (polling) | **3 seconds** | None (query: `?classroom_id=X`) | `[{ id, classroom_id, type, timestamp, ... }]` |
| **GET /api/classrooms** | On page load | Once | None | `[{ id, name, current_status, video_id, ... }]` |
| **GET /api/videos** | On page load | Once | None | `[{ id, filename, url, classroom_id, ... }]` |

---

## 7. Detection Flow Examples

### Example 1: Empty Class Detection

**Timeline:**
- `t=0s`: Frame arrives, YOLOv8 detects 0 persons → `first_empty_time = now`
- `t=1.5s`: Frame arrives, 0 persons → elapsed = 1.5s (< 120s) → no alert
- `t=3.0s`: Frame arrives, 0 persons → elapsed = 3.0s (< 120s) → no alert
- ...
- `t=120s`: Frame arrives, 0 persons → elapsed = 120s (≥ 120s) → **create "empty_class" alert**
- `t=121.5s`: Frame arrives, 1 person detected → reset `first_empty_time = None`

---

### Example 2: Mischief Detection

**Timeline:**
- `t=0s`: Frame arrives, motion_score = 0.4 (> 0.3) → `consecutive_motion = 1`
- `t=1.5s`: Frame arrives, motion_score = 0.5 (> 0.3) → `consecutive_motion = 2`
- `t=3.0s`: Frame arrives, motion_score = 0.45 (> 0.3) → `consecutive_motion = 3` → **create "mischief" alert**
- `t=4.5s`: Frame arrives, motion_score = 0.2 (< 0.3) → reset `consecutive_motion = 0`
- `t=63.0s`: (60s cooldown passed) Frame arrives, motion_score = 0.4 → can alert again

---

### Example 3: Loud Noise Detection

**Timeline:**
- `t=0s`: Audio level = 0.8 (> 0.75) → `consecutive_high_audio = 1`
- `t=1s`: Audio level = 0.82 (> 0.75) → `consecutive_high_audio = 2`
- `t=2s`: Audio level = 0.78 (> 0.75) → `consecutive_high_audio = 3`
- `t=3s`: Audio level = 0.85 (> 0.75) → `consecutive_high_audio = 4`
- `t=4s`: Audio level = 0.79 (> 0.75) → `consecutive_high_audio = 5` → **create "loud_noise" alert**
- `t=5s`: Audio level = 0.3 (< 0.75) → reset `consecutive_high_audio = 0`
- `t=65s`: (60s cooldown passed) Audio level = 0.8 → can alert again

---

## 8. Key Technical Details

### 8.1 Audio Level Units

**NOT decibels** — it's a **normalized RMS level (0.0–1.0)**

- **Decibels (dB)** would be: `20 * log10(amplitude)` — absolute measure
- **Normalized RMS** is: `sqrt(sum(samples²) / length)` normalized to 0–1 — relative measure

**Why normalized?**
- Easier to work with (0–1 range)
- Device-independent (works across different microphones/audio sources)
- Matches Web Audio API's output format

**Conversion:** If you need approximate decibels: `dB ≈ 20 * log10(level)` (but level=0 would be -∞ dB, so not practical)

---

### 8.2 Frame Capture Details

**Canvas size:** 640×360 pixels (fixed)

**Image format:** JPEG, quality 0.8 (80% compression)

**Base64 encoding:** `data:image/jpeg;base64,...` format

**CORS:** Video element has `crossOrigin="anonymous"` to allow canvas drawing

---

### 8.3 State Persistence

**Storage:** In-memory Python dictionaries (`_state`, `_locks`)

**Persistence:** State is **NOT persisted** — if backend restarts, all counters/timers reset

**Alerts:** Stored in **MongoDB** (`alerts` collection) — these persist across restarts

**Classroom status:** Stored in **MongoDB** (`classrooms` collection) — persists across restarts

---

## 9. Summary

**Frontend (per video playing):**
- Frame capture: **Every 1.5 seconds** → `POST /api/sentinel/analyze-frame`
- Audio capture: **Every 1 second** → `POST /api/sentinel/audio-level`
- Alert polling: **Every 3 seconds** → `GET /api/alerts` (global, not per video)

**Backend:**
- **YOLOv8:** Person detection (counts persons in frame)
- **OpenCV:** Motion detection (compares consecutive frames)
- **Rules engine:** Applies thresholds and creates alerts
- **State:** Per-classroom counters/timers (in-memory)
- **Alerts:** Stored in MongoDB (persistent)

**Detection thresholds:**
- Empty Class: 0 persons for **2 minutes**
- Mischief: Motion > **0.3** for **3 frames** (~4.5 seconds)
- Loud Noise: Audio level > **0.75** for **5 requests** (5 seconds)

**Audio level:** Normalized **0.0–1.0** (RMS), NOT decibels

---

This is the complete technical context of how Vision X Sentinel works end-to-end.
