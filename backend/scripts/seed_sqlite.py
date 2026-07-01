import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
DB = DATA / "studioflix.db"

if DB.exists():
    DB.unlink()

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")

conn.executescript("""
CREATE TABLE videos (
  video_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT,
  duration_sec INTEGER NOT NULL
);

CREATE TABLE viewing_logs (
  event_id INTEGER PRIMARY KEY,
  session_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  video_id TEXT NOT NULL,
  video_duration_sec INTEGER NOT NULL,
  event_type TEXT NOT NULL,
  position_sec INTEGER NOT NULL,
  event_time TEXT NOT NULL,
  FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

CREATE TABLE ground_truth_hotspots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  video_id TEXT NOT NULL,
  hotspot_start INTEGER NOT NULL,
  hotspot_end INTEGER NOT NULL,
  FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

CREATE TABLE users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL
);

CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL
);

CREATE TABLE project_videos (
  project_id TEXT NOT NULL,
  video_id TEXT NOT NULL,
  PRIMARY KEY (project_id, video_id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

CREATE TABLE review_sessions (
  id TEXT PRIMARY KEY,
  video_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

CREATE TABLE review_comments (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  video_id TEXT NOT NULL,
  author_email TEXT NOT NULL,
  timestamp REAL NOT NULL,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (session_id) REFERENCES review_sessions(id),
  FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

CREATE TABLE review_annotations (
  id TEXT PRIMARY KEY,
  comment_id TEXT NOT NULL,
  type TEXT NOT NULL,
  color TEXT NOT NULL,
  points_json TEXT NOT NULL,
  FOREIGN KEY (comment_id) REFERENCES review_comments(id)
);
""")

def load_csv(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

for row in load_csv("videos.csv"):
    conn.execute(
        "INSERT INTO videos VALUES (?, ?, ?, ?)",
        (row["video_id"], row["title"], row["category"], int(row["duration_sec"])),
    )

for row in load_csv("viewing_logs.csv"):
    conn.execute(
        "INSERT INTO viewing_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            int(row["event_id"]),
            row["session_id"],
            row["user_id"],
            row["video_id"],
            int(row["video_duration_sec"]),
            row["event_type"],
            int(row["position_sec"]),
            row["event_time"],
        ),
    )

for row in load_csv("ground_truth_hotspots.csv"):
    conn.execute(
        "INSERT INTO ground_truth_hotspots (video_id, hotspot_start, hotspot_end) VALUES (?, ?, ?)",
        (row["video_id"], int(row["hotspot_start"]), int(row["hotspot_end"])),
    )

conn.execute("INSERT INTO users VALUES (?, ?, ?)", ("u_admin", "alice@studioflix.local", "admin"))
conn.execute("INSERT INTO projects VALUES (?, ?, ?)", ("p_demo", "Projet de revue vidéo", "in_review"))
conn.execute("INSERT INTO project_videos VALUES (?, ?)", ("p_demo", "v01"))
conn.execute("INSERT INTO review_sessions VALUES (?, ?, datetime('now'))", ("review_v01", "v01"))

conn.commit()
conn.close()

print(f"SQLite DB created: {DB}")
