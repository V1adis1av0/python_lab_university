import os, secrets, hashlib, time, logging, psycopg2, jwt
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ===== CONFIG & LOGGING =====
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("notes_api")

SECRET = os.getenv("SECRET", secrets.token_hex(16))
DB = {"dbname": "lab6_python", "user": "test", "password": "qwe123", "host": "localhost"}
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ===== RATE LIMIT =====
attempts = defaultdict(list)
def rate_limit(user: str) -> bool:
    now = time.time()
    attempts[user] = [t for t in attempts[user] if now - t < 300]
    if len(attempts[user]) >= 5:
        log.warning(f"Rate limit exceeded: {user}")
        return False
    attempts[user].append(now)
    return True

# ===== HELPERS =====
def db(): return psycopg2.connect(**DB)


def get_user(req: Request):

    token = req.cookies.get("token")
    if not token:
        raise HTTPException(401, "Missing token")
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

def csrf(req: Request):
    if req.url.path == "/docs": return True
    if req.headers.get("X-CSRF") != req.cookies.get("csrf"): raise HTTPException(403, "CSRF")
    return True

def h(pw): return hashlib.sha256(pw.encode()).hexdigest()

# ===== MODELS =====
class Auth(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
class Note(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., max_length=5000)

# ===== INIT DB =====
@app.on_event("startup")
def init():
    c = db(); cur = c.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS notes(id SERIAL PRIMARY KEY, owner_id INT, title TEXT, content TEXT)")
    c.commit(); cur.close(); c.close()
    log.info("Database initialized")

# ===== AUTH =====
@app.post("/register")
def register(u: Auth):
    conn = db()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users(username, password) VALUES(%s, %s)", 
            (u.username, h(u.password))
        )
        conn.commit()
        log.info(f"Registered: {u.username}")
        return {"ok": True}
    except psycopg2.errors.UniqueViolation:
        log.warning(f"Register failed: {u.username} (exists)")
        raise HTTPException(400, "Username already exists")
    finally:
        cur.close()
        conn.close()

@app.post("/login")
def login(u: Auth, res: Response):
    if not rate_limit(u.username):
        raise HTTPException(429, "Wait")
    conn = db(); cur = conn.cursor()
    try:
        cur.execute("SELECT id, username FROM users WHERE username=%s AND password=%s", (u.username, h(u.password)))
        row = cur.fetchone()
        if not row:
            log.warning(f"Login failed: {u.username}")
            raise HTTPException(401, "Wrong")
        attempts[u.username] = []
        token = jwt.encode({"id": row[0], "exp": datetime.now(timezone.utc)+timedelta(minutes=60)}, SECRET, algorithm="HS256")
        res.set_cookie("token", token, httponly=True, path="/")
        res.set_cookie("csrf", secrets.token_hex(16), path="/")
        log.info(f"Logged in: {u.username}")
        return {"ok": True}
    finally: 
        cur.close()
        conn.close()

# ===== CRUD =====
@app.post("/notes")
def create(n: Note, user=Depends(get_user), _=Depends(csrf)):
    conn = db(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO notes(owner_id, title, content) VALUES(%s,%s,%s) RETURNING id", (user["id"], n.title, n.content))
        conn.commit()
        log.info(f"Note created: user={user['id']}, title={n.title}")
        return {"id": cur.fetchone()[0]}
    finally:
        cur.close()
        conn.close()

@app.get("/notes/{id}")
def read(id: int, user=Depends(get_user)):
    conn = db(); cur = conn.cursor()
    try:
        cur.execute("SELECT id,title,content FROM notes WHERE id=%s AND owner_id=%s", (id, user["id"]))
        row = cur.fetchone()
        if not row:
            log.warning(f"Note not found: id={id}, user={user['id']}")
            raise HTTPException(404, "Not found")
        return {"id": row[0], "title": row[1], "content": row[2]}
    finally:
        cur.close()
        conn.close()

@app.put("/notes/{id}")
def update(id: int, n: Note, user=Depends(get_user), _=Depends(csrf)):
    conn = db(); cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM notes WHERE id=%s AND owner_id=%s", (id, user["id"]))
        if not cur.fetchone():
            log.warning(f"Update denied: id={id}, user={user['id']}")
            raise HTTPException(404, "Not found")
        cur.execute("UPDATE notes SET title=%s, content=%s WHERE id=%s AND owner_id=%s", (n.title, n.content, id, user["id"]))
        conn.commit()
        log.info(f"Note updated: id={id}")
        return {"ok": True}
    finally:
        cur.close()
        conn.close()

@app.delete("/notes/{id}")
def delete(id: int, user=Depends(get_user), _=Depends(csrf)):
    conn = db(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM notes WHERE id=%s AND owner_id=%s", (id, user["id"]))
        if not cur.rowcount:
            log.warning(f"Delete denied: id={id}, user={user['id']}")
            raise HTTPException(404, "Not found")
        conn.commit()
        log.info(f"Note deleted: id={id}")
        return {"ok": True}
    finally:
        cur.close()
        conn.close()

# ===== GLOBAL ERROR HANDLER =====
@app.exception_handler(Exception)
def handle_err(req: Request, exc: Exception):
    log.error(f"Error at {req.url}: {exc}", exc_info=False)
    return {"detail": "Internal error"}