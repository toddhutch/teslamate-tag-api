from flask import Flask, request, jsonify
import os, psycopg

def getenv(name, default=""):
    return os.getenv(name, default)

DB_HOST = getenv("DB_HOST", "TeslaMate-DB")   # your DB container name
DB_USER = getenv("DB_USER", "teslamate")
DB_NAME = getenv("DB_NAME", "teslamate")
DB_PASS = getenv("DB_PASS", "")
TOKEN   = getenv("TOKEN", "")

app = Flask(__name__)
dsn = f"host={DB_HOST} user={DB_USER} dbname={DB_NAME} password={DB_PASS}"

def upsert(drive_id:int, tag:str):
    with psycopg.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO drive_tags (drive_id, tag)
            VALUES (%s, %s)
            ON CONFLICT (drive_id) DO UPDATE SET tag = EXCLUDED.tag, created_at = now();
        """, (drive_id, tag))

@app.get("/health")
def health():
    return jsonify(ok=True)

@app.get("/tag")
def tag_get():
    if request.headers.get("X-Tag-Token") != TOKEN:
        return ("forbidden", 403)
    upsert(int(request.args["drive_id"]), request.args["tag"])
    return jsonify(ok=True)

@app.post("/tag")
def tag_post():
    if request.headers.get("X-Tag-Token") != TOKEN:
        return ("forbidden", 403)
    j = request.get_json(force=True)
    upsert(int(j["drive_id"]), j["tag"])
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
