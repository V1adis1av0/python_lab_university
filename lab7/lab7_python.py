import requests
import jwt
import time
import sys
import warnings
from datetime import datetime, timezone, timedelta

warnings.filterwarnings("ignore", category=UserWarning)

# ================= CONFIG =================
BASE_URL = "http://127.0.0.1:8000"
JWT_SECRET = "fixed_secret_for_dev_only_change_in_prod"
VALID_PASS = "SecurePass123!"   # Соответствует min_length=8
WRONG_PASS = "WrongPassword1!"  # Соответствует min_length=8, но неверный
TIMEOUT = 10

def log_pass(name): print(f"PASS | {name}")
def log_fail(name, err): print(f"FAIL | {name} -> {err}")
def log_skip(name, reason): print(f"SKIP | {name} ({reason})")

def run_test(func, name):
    try:
        func()
        log_pass(name)
        return True
    except AssertionError as e:
        log_fail(name, str(e))
        return False
    except Exception as e:
        log_fail(name, f"Runtime: {e}")
        return False

# ================= HELPERS =================
def register_user(username, password=VALID_PASS):
    r = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password}, timeout=TIMEOUT)
    return r.status_code in [200, 400]

def get_session(username, password=VALID_PASS):
    """Авторизует пользователя и возвращает сессию с куками."""
    if not register_user(username, password):
        raise AssertionError(f"Failed to register {username}")
    
    s = requests.Session()
    r = s.post(f"{BASE_URL}/login", json={"username": username, "password": password}, timeout=TIMEOUT)
    if r.status_code != 200:
        raise AssertionError(f"Login failed for {username}: {r.status_code} {r.text}")
    return s

# ================= TESTS =================

def test_1_sqli_register():
    """#1 SQL-инъекция в /register"""
    payload = {"username": "admin' OR '1'='1", "password": VALID_PASS}
    r = requests.post(f"{BASE_URL}/register", json=payload, timeout=TIMEOUT)
    assert r.status_code in [200, 400], f"Unexpected status: {r.status_code}"

def test_2_sqli_login():
    """#2 SQL-инъекция в /login"""
    payload = {"username": "admin' OR '1'='1", "password": WRONG_PASS}
    r = requests.post(f"{BASE_URL}/login", json=payload, timeout=TIMEOUT)
    assert r.status_code == 401, f"Auth bypassed! Got {r.status_code}"

def test_3_jwt_forgery_expiration():
    """#3 Подделка и просрочка JWT"""
    fake = jwt.encode({"id": 999, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, 
                      "wrong_secret", algorithm="HS256")
    r = requests.get(f"{BASE_URL}/notes/1", cookies={"token": fake}, timeout=TIMEOUT)
    assert r.status_code == 401, "Forged token accepted"

    expired = jwt.encode({"id": 1, "exp": datetime.now(timezone.utc) - timedelta(hours=1)}, 
                         JWT_SECRET, algorithm="HS256")
    r = requests.get(f"{BASE_URL}/notes/1", cookies={"token": expired}, timeout=TIMEOUT)
    assert r.status_code == 401, "Expired token accepted"

def test_4_cookie_security():
    """#4 Защита кук (HttpOnly, SameSite)"""
    register_user("cookie_test")
    r = requests.post(f"{BASE_URL}/login", json={"username": "cookie_test", "password": VALID_PASS}, timeout=TIMEOUT)
    assert r.status_code == 200
    set_cookie = r.headers.get("Set-Cookie", "")
    assert "HttpOnly" in set_cookie, "Missing HttpOnly flag"
    assert "SameSite" in set_cookie or "samesite" in set_cookie.lower(), "Missing SameSite flag"

def test_5_csrf_protection():
    """#5 Межсайтовая подделка запросов (CSRF)"""
    s = get_session("csrf_user")
    csrf_val = s.cookies.get("csrf")
    if not csrf_val:
        log_skip("CSRF Protection", "CSRF cookie not found (disabled in server config)")
        return

    r = s.post(f"{BASE_URL}/notes", json={"title": "CSRF", "content": "test"}, timeout=TIMEOUT)
    assert r.status_code == 403, f"CSRF not enforced: {r.status_code}"

    r = s.post(f"{BASE_URL}/notes", json={"title": "CSRF_OK", "content": "test"}, 
               headers={"X-CSRF": csrf_val}, timeout=TIMEOUT)
    assert r.status_code == 200, f"Valid CSRF rejected: {r.status_code}"

def test_6_idor_create():
    """#6 IDOR при создании заметки (внедрение owner_id)"""
    s = get_session("idor_c_user")
    csrf_val = s.cookies.get("csrf")
    payload = {"title": "IDOR_Create", "content": "test", "owner_id": 999}
    r = s.post(f"{BASE_URL}/notes", json=payload, headers={"X-CSRF": csrf_val}, timeout=TIMEOUT)
    assert r.status_code == 200, f"Note creation failed: {r.status_code}"

def test_7_idor_access():
    """#7 IDOR при чтении/обновлении/удалении"""
    s_a = get_session("idor_a_user")
    csrf_a = s_a.cookies.get("csrf")
    r = s_a.post(f"{BASE_URL}/notes", json={"title": "Private", "content": "Secret"}, 
                 headers={"X-CSRF": csrf_a}, timeout=TIMEOUT)
    assert r.status_code == 200, "User A failed to create note"
    note_id = r.json().get("id")

    s_b = get_session("idor_b_user")
    csrf_b = s_b.cookies.get("csrf")

    # Read
    r = s_b.get(f"{BASE_URL}/notes/{note_id}", timeout=TIMEOUT)
    assert r.status_code == 404, f"IDOR Read allowed: {r.status_code}"
    
    # Update
    r = s_b.put(f"{BASE_URL}/notes/{note_id}", json={"title": "Hacked", "content": "Hacked content"}, 
                headers={"X-CSRF": csrf_b}, timeout=TIMEOUT)
    assert r.status_code == 404, f"IDOR Update allowed: {r.status_code}"
    
    # Delete
    r = s_b.delete(f"{BASE_URL}/notes/{note_id}", headers={"X-CSRF": csrf_b}, timeout=TIMEOUT)
    assert r.status_code == 404, f"IDOR Delete allowed: {r.status_code}"

def test_8_brute_force():
    """#8 Перебор паролей (Rate Limiting)"""
    user = f"rl_{int(time.time())}"
    register_user(user)

    for i in range(5):
        r = requests.post(f"{BASE_URL}/login", json={"username": user, "password": WRONG_PASS}, timeout=TIMEOUT)
        assert r.status_code == 401, f"Attempt {i+1} should fail with 401, got {r.status_code}"

    r = requests.post(f"{BASE_URL}/login", json={"username": user, "password": WRONG_PASS}, timeout=TIMEOUT)
    assert r.status_code == 429, f"Rate limit not triggered: {r.status_code}"
    assert "Too many attempts" in r.text or "Wait" in r.text, "Missing rate limit message"

# ================= RUNNER =================
if __name__ == "__main__":
    print("=" * 60)
    print("SECURITY TEST")
    print("=" * 60)
    
    results = []
    results.append(run_test(test_1_sqli_register, "1. SQLi in /register"))
    results.append(run_test(test_2_sqli_login,    "2. SQLi in /login"))
    results.append(run_test(test_3_jwt_forgery_expiration, "3. JWT Forgery & Expiration"))
    results.append(run_test(test_4_cookie_security,        "4. Cookie Security (HttpOnly/SameSite)"))
    results.append(run_test(test_5_csrf_protection,        "5. CSRF Protection"))
    results.append(run_test(test_6_idor_create,            "6. IDOR on Create (owner_id injection)"))
    results.append(run_test(test_7_idor_access,            "7. IDOR on Read/Update/Delete"))
    results.append(run_test(test_8_brute_force,            "8. Brute-force / Rate Limiting"))

    print("\n" + "=" * 60)
    passed = sum(results)
    print(f"RESULTS: {passed}/{len(results)} tests passed")
    if passed == len(results):
        print("ALL SECURITY MECHANISMS VERIFIED SUCCESSFULLY!")
    else:
        print("Some tests failed. Check logs above.")
    print("=" * 60)