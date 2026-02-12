# Vision X Sentinel — End-to-End Flow

This document explains **what happens from the moment the frontend loads** until alerts appear: which API calls run, what triggers them, and how the backend responds.

---

## 1. When the frontend loads

### 1.1 Entry point

- **`main.jsx`** renders `<App />` and a `<Toaster />` (for toast notifications).
- **`App.jsx`** renders:
  - **Layout** (header, search bar, Logs button, Broadcast button, footer with Active/Inactive counts and Refresh).
  - **Dashboard** (grid of class cards) as the main content.

### 1.2 First API calls (on load)

| Who        | When           | API call                    | Backend route              | Purpose |
|-----------|----------------|-----------------------------|----------------------------|--------|
| **App**   | `useEffect` once on mount | `getClassrooms()`           | `GET /api/classrooms`      | Load all classrooms for **status bar** (Active/Inactive counts) and to pass `searchQuery` filter to Dashboard. |
| **Dashboard** | `useEffect` once on mount | `getClassrooms()` + `getVideos()` in parallel | `GET /api/classrooms` and `GET /api/videos` | Load classrooms and videos to build the list of **ClassCards** and the **video URL map** (`video_id` → `url`). |

So on first load you see **two** `GET /api/classrooms` (one from App, one from Dashboard) and **one** `GET /api/videos`.

### 1.3 Alert polling (starts on load)

- **`useAlerts()`** hook runs inside **Dashboard**.
- It immediately calls **`getAlerts()`** → `GET /api/alerts`.
- Then it runs the same call **every 3 seconds** (`POLL_INTERVAL_MS = 3000`).
- On the **first** poll, it just stores all alert IDs in `seenIdsRef` (no toasts).
- On **later** polls, for any alert whose `id` is **not** in `seenIdsRef`, it:
  - Adds the id to `seenIdsRef`,
  - Shows a **toast**: e.g. `"Empty Class detected in 8A"`.
- So: **new alerts** (created by the backend after load) appear as toasts when the next poll sees them.

---

## 2. How the Dashboard uses the data

- **Classrooms** from `GET /api/classrooms`: list of `{ id, name, current_status, video_id, ... }`.
- **Videos** from `GET /api/videos`: list of `{ id, filename, url, ... }`.
- Dashboard builds **`videoMap`**: `videoMap[video_id] = url` (e.g. `videoMap["video1"] = "/mock-media/video1.mp4"`).
- **Search**: `searchQuery` (from Layout) filters classrooms by `name` or `id`; only **filtered** classrooms are rendered as cards.
- For each filtered classroom it renders a **ClassCard** with:
  - `classroom`
  - `videoUrl = videoMap[classroom.video_id]` (so the card knows which video to play)
  - `onFrameCapture={handleFrameCapture}` (sends frames to backend)
  - `hasNewAlert={recentAlertClassroomIds.includes(classroom.id)}` (for “new alert” indicator on the card).

---

## 3. ClassCard: video, frame capture, and audio

Each **ClassCard** is responsible for one classroom: show video, capture frames, capture audio, and send both to the backend.

### 3.1 Video element and URL

- The card renders a **`<video>`** with `src={finalVideoUrl}`.
- `finalVideoUrl` is either:
  - The **full URL** if `videoUrl` from props already starts with `http` (e.g. backend static URL), or
  - **`origin + videoUrl`** (e.g. `http://localhost:5173` + `/mock-media/video1.mp4`) so the video is loaded from the **frontend dev server** (Vite) from `public/mock-media/`.

So **no backend API call** is used to **stream** the video; the browser loads the file from the frontend’s public folder.

### 3.2 Autoplay (when the card mounts / URL is set)

- **useEffect** depends on `classroom.id` and `videoUrl`.
- When the video element is ready (`readyState >= 2` or after `loadeddata`), it calls **`video.play()`** (autoplay).
- If that succeeds, it **dispatches a synthetic `play` event** so that the same logic that runs on “user play” also runs for autoplay.
- If autoplay is blocked (e.g. no user gesture), the video stays paused until the user clicks play; no extra API call.

### 3.3 When the video **plays** (user or autoplay)

- The card has **event listeners**: `play`, `pause`, `ended` on the video element.
- On **play**:
  1. **Frame capture** starts: an interval runs **every 1.5 seconds**.
  2. **Audio capture** starts: Web Audio (AnalyserNode) and an interval runs **every 1 second**.

So:
- **Every 1.5 s** while the video is playing: capture one frame from the video (draw to canvas → `toDataURL('image/jpeg', 0.8)`), then call **`onFrameCapture(classroom.id, frameBase64)`**.
- **Every 1 s** while the video is playing: read audio level from the AnalyserNode (RMS), then call **`sendAudioLevel(classroom.id, level)`**.

### 3.4 Where those calls go

- **`onFrameCapture`** is **Dashboard’s `handleFrameCapture`**, which calls **`analyzeFrame(classroomId, frameBase64)`** in the API client.
- **`analyzeFrame`** → **`POST /api/sentinel/analyze-frame`** with `{ classroom_id, frame }`.
- **`sendAudioLevel`** (called from ClassCard) → **`POST /api/sentinel/audio-level`** with `{ classroom_id, level }`.

So:

| Trigger              | When              | API call                          | Interval / condition   |
|----------------------|-------------------|------------------------------------|------------------------|
| Video starts playing | `play` event      | Start two intervals (see below)   | —                      |
| Every 1.5 s         | While video plays | `POST /api/sentinel/analyze-frame`| Only while not paused  |
| Every 1 s            | While video plays | `POST /api/sentinel/audio-level`  | Only while not paused  |
| Video pauses / ends  | `pause` or `ended`| **Stop** both intervals            | —                      |

### 3.5 Frame capture error handling

- If **3 consecutive** `POST /api/sentinel/analyze-frame` calls **fail** (e.g. backend down):
  - The frame-capture interval is **stopped** (no more frames sent).
  - A **retry interval** runs every 5 s: one test frame is sent; if it succeeds, frame capture is **restarted**.
- So when the server is down, the frontend stops sending frames and resumes automatically when the server is back.

---

## 4. Backend: what each API does

### 4.1 GET /api/classrooms

- **Handler**: `classrooms.list_classrooms()`.
- **Data**: Reads from **MongoDB** (via `get_all_classrooms()`).
- **Response**: JSON array of classroom documents (id, name, current_status, video_id, etc.).

### 4.2 GET /api/videos

- **Handler**: `videos.list_videos()`.
- **Data**: Reads from **MongoDB** (via `get_all_videos()`).
- **Response**: JSON array of video documents (id, filename, url, etc.).

### 4.3 GET /api/alerts

- **Handler**: `alerts.list_alerts()`.
- **Query**: Optional `?classroom_id=...` to filter.
- **Data**: Reads from **MongoDB** (via `get_alerts()`).
- **Response**: JSON array of alerts (id, classroom_id, type, timestamp, metadata, etc.).
- **Used by**: Frontend **useAlerts** (polling) and **LogsPanel** (when user opens Logs).

### 4.4 POST /api/sentinel/analyze-frame

- **Body**: `{ "classroom_id": "...", "frame": "data:image/jpeg;base64,..." }`.
- **Steps**:
  1. Decode base64 → image (BGR numpy array).
  2. Get **per-classroom state** (and lock) for `classroom_id` (prev_frame, first_empty_time, consecutive_motion, etc.).
  3. **YOLOv8** → **person count** in the image.
  4. **Motion**: compute motion score between current frame and `prev_frame` (OpenCV); store current frame as new `prev_frame`.
  5. **Empty-class rule**: if `person_count == 0` for **≥ 2 minutes** → insert **empty_class** alert, update classroom status to `"empty"`, reset timer; else if person_count > 0, reset timer.
  6. **Mischief rule**: if motion score **> threshold** for **3 consecutive** frames (with cooldown) → insert **mischief** alert, update classroom status.
  7. Return JSON: `{ classroom_id, person_count, motion_score, alert_created }`.

So **one** frame request updates state, may create alerts, and returns counts/scores.

### 4.5 POST /api/sentinel/audio-level

- **Body**: `{ "classroom_id": "...", "level": 0.0–1.0 }`.
- **Steps**:
  1. Get per-classroom state (consecutive_high_audio, last_loud_noise_alert_time).
  2. **Loud-noise rule**: if `level > 0.75` for **5 consecutive** requests (with cooldown) → insert **loud_noise** alert, update classroom status.
  3. Return JSON: `{ classroom_id, audio_level, alert_created }`.

---

## 5. How alerts reach the user

1. **Backend** creates an alert (empty_class, mischief, or loud_noise) and inserts it into **MongoDB** (e.g. from analyze-frame or audio-level).
2. **Frontend** is already polling **GET /api/alerts** every 3 seconds.
3. On the **next** poll after the insert, the new alert appears in the list; its `id` is not in `seenIdsRef`.
4. **useAlerts** shows a **toast** and adds the id to `seenIdsRef`.
5. **Dashboard** passes `recentAlertClassroomIds` to ClassCards; if a classroom has any alert in the current list, that card can show a “new alert” indicator (`hasNewAlert`).

So: **no WebSockets**; alerts are “pulled” by the frontend every 3 s.

---

## 6. Other UI actions (no or simple backend)

- **Search**: Only filters the list of classrooms in the frontend; **no** API call.
- **Refresh (footer)**: Calls **App’s `loadClassrooms()`** again → **GET /api/classrooms**; status bar counts and (indirectly) the list in Dashboard are updated when Dashboard re-renders with the same data source. (Dashboard has its own `getClassrooms()` on mount; Refresh does not re-run Dashboard’s `loadData` unless you change design.)
- **Logs button**: Opens **LogsPanel**, which calls **GET /api/alerts** once and shows the last 20 alerts (time, classroom, type).
- **Broadcast**: Only shows a toast “Broadcast sent to all classrooms”; **no** backend call.

---

## 7. Flow summary diagram

```
FRONTEND LOAD
├── App mount
│   └── GET /api/classrooms  →  status bar (Active / Inactive)
├── Dashboard mount
│   ├── GET /api/classrooms  ─┐
│   ├── GET /api/videos      ─┴→  build videoMap, render ClassCards
│   └── useAlerts()
│       └── GET /api/alerts (then every 3 s)  →  toasts for new alerts
│
FOR EACH CLASS CARD (when video is playing)
├── Every 1.5 s:  POST /api/sentinel/analyze-frame  →  person count, motion, empty_class / mischief alerts
└── Every 1 s:    POST /api/sentinel/audio-level    →  loud_noise alerts

BACKEND (on analyze-frame)
├── Decode frame → YOLOv8 (person count) + motion vs prev_frame
├── Update per-classroom state (prev_frame, timers, consecutive counts)
├── If rules fire → insert_alert() + upsert_classroom()
└── Return { person_count, motion_score, alert_created }

BACKEND (on audio-level)
├── Update per-classroom state (consecutive_high_audio, cooldown)
├── If loud for 5 consecutive → insert_alert() + upsert_classroom()
└── Return { audio_level, alert_created }

ALERTS
├── Stored in MongoDB by backend
└── Frontend sees them on next GET /api/alerts poll → toast + card indicator
```

---

## 8. Important conditions (cheat sheet)

| Condition | What happens |
|-----------|----------------|
| Page just loaded | App: GET classrooms. Dashboard: GET classrooms + GET videos. useAlerts: GET alerts, then every 3 s. |
| Video has URL and is ready | Autoplay attempted; synthetic `play` if success. |
| Video `play` event | Start 1.5 s frame interval and 1 s audio interval. |
| Every 1.5 s while playing | POST analyze-frame with current frame. |
| Every 1 s while playing | POST audio-level with current RMS level. |
| Video `pause` or `ended` | Stop both intervals, cleanup AudioContext and refs. |
| 3 consecutive analyze-frame failures | Stop frame interval; start 5 s retry until one success, then resume. |
| Backend: 0 persons for 2 min | Insert empty_class alert, set classroom status empty. |
| Backend: high motion 3 frames in a row | Insert mischief alert (with cooldown). |
| Backend: audio level > 0.75 for 5 requests in a row | Insert loud_noise alert (with cooldown). |
| New alert in DB | Next GET /api/alerts (within 3 s) shows toast and updates card indicator. |
| User clicks Logs | LogsPanel opens, GET /api/alerts once, show last 20. |
| User clicks Refresh | App re-fetches GET /api/classrooms (status bar). |

This is the complete end-to-end picture of how the frontend and backend work together in Vision X Sentinel.
