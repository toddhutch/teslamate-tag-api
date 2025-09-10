from flask import Flask, request, jsonify
import os, psycopg

app = Flask(__name__)
dsn = f"host={os.getenv('DB_HOST')} user={os.getenv('DB_USER')} dbname={os.getenv('DB_NAME')} password={os.getenv('DB_PASS')}"
TOKEN = os.getenv("TOKEN", "")

def upsert(drive_id:int, tag:str):
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO drive_tags (drive_id, tag)
            VALUES (%s, %s)
            ON CONFLICT (drive_id) DO UPDATE SET tag=EXCLUDED.tag, created_at=now();
        """, (drive_id, tag))

@app.post("/tag")
def tag_post():
    if request.headers.get("X-Tag-Token") != TOKEN:
        return ("forbidden", 403)
    j = request.get_json(force=True)
    upsert(int(j["drive_id"]), j["tag"])
    return jsonify(ok=True)

@app.get("/health")
def health():
    return jsonify(ok=True)
