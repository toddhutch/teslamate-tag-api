from flask import Flask, request, jsonify
from flask_cors import CORS
import os, psycopg

app = Flask(__name__)

# ✅ Explicit CORS for Grafana (v12 Actions use fetch + preflight)
CORS(
    app,
    resources={r"/tag*": {"origins": ["http://192.168.111.93:20003"]}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Tag-Token"],
    max_age=86400,
    supports_credentials=False,
)

DB_HOST=os.getenv("DB_HOST","TeslaMate-DB")
DB_USER=os.getenv("DB_USER","teslamate")
DB_NAME=os.getenv("DB_NAME","teslamate")
DB_PASS=os.getenv("DB_PASS","")
TOKEN  =os.getenv("TOKEN","")
dsn=f"host={DB_HOST} user={DB_USER} dbname={DB_NAME} password={DB_PASS}"

def upsert(drive_id:int, tag:str):
    tag = {"business":"Business", "personal":"Personal"}.get((tag or "").lower(), tag)
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO drive_tags (drive_id, tag)
            VALUES (%s, %s)
            ON CONFLICT (drive_id) DO UPDATE SET tag=EXCLUDED.tag, created_at=now();
        """, (drive_id, tag))

def _check_token():
    supplied = request.headers.get("X-Tag-Token") or request.args.get("token")
    return supplied == TOKEN

@app.route("/tag", methods=["GET","POST","OPTIONS"])
def tag():
    if request.method == "OPTIONS":
        return ("", 204)
    if not _check_token():
        return ("forbidden", 403)

    # Accept from query string OR JSON
    drive_id = request.values.get("drive_id")
    tag_val  = request.values.get("tag")
    if not drive_id or not tag_val:
        j = request.get_json(silent=True) or {}
        drive_id = drive_id or j.get("drive_id")
        tag_val  = tag_val  or j.get("tag")

    if not drive_id or not tag_val:
        return jsonify(error="drive_id and tag are required"), 400

    upsert(int(drive_id), tag_val)
    return jsonify(ok=True)

@app.get("/tag")
def tag_get():
    if not _check_token(): return ("forbidden", 403)
    drive_id = request.args.get("drive_id")
    tag = request.args.get("tag", "")
    if not drive_id or not tag: return jsonify(error="drive_id and tag are required"), 400
    upsert(int(drive_id), tag)
    return jsonify(ok=True)

@app.post("/tag")
def tag_post():
    if not _check_token(): return ("forbidden", 403)
    j = request.get_json(force=True)  # expects {"drive_id": ..., "tag": "..."}
    if not j or "drive_id" not in j or "tag" not in j:
        return jsonify(error="drive_id and tag are required"), 400
    upsert(int(j["drive_id"]), j["tag"])
    return jsonify(ok=True)

@app.get("/health")
def health(): 
    return jsonify(ok=True)
