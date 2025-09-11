from flask import Flask, request, jsonify
from flask_cors import CORS
import os, psycopg

app = Flask(__name__)
# allow requests from your Grafana origin (port 20003)
CORS(app, resources={r"/tag*": {"origins": ["http://192.168.111.93:20003"]}}, supports_credentials=False)

DB_HOST=os.getenv("DB_HOST","TeslaMate-DB")
DB_USER=os.getenv("DB_USER","teslamate")
DB_NAME=os.getenv("DB_NAME","teslamate")
DB_PASS=os.getenv("DB_PASS","")
TOKEN  =os.getenv("TOKEN","")
dsn=f"host={DB_HOST} user={DB_USER} dbname={DB_NAME} password={DB_PASS}"

def upsert(drive_id:int, tag:str):
    tag = {"business":"Business", "personal":"Personal"}.get(tag.lower(), tag)
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO drive_tags (drive_id, tag)
            VALUES (%s, %s)
            ON CONFLICT (drive_id) DO UPDATE SET tag=EXCLUDED.tag, created_at=now();
        """, (drive_id, tag))

def _check_token():
    supplied = request.headers.get("X-Tag-Token") or request.args.get("token")
    return supplied == TOKEN

@app.get("/tag")
def tag_get():
    if not _check_token(): return ("forbidden", 403)
    upsert(int(request.args["drive_id"]), request.args.get("tag",""))
    return jsonify(ok=True)

@app.post("/tag")
def tag_post():
    if not _check_token(): return ("forbidden", 403)
    j = request.get_json(force=True)
    upsert(int(j["drive_id"]), j.get("tag",""))
    return jsonify(ok=True)

@app.get("/health")
def health(): return jsonify(ok=True)
