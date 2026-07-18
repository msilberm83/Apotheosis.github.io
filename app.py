from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import smtplib
from email.message import EmailMessage
from pathlib import Path
from flask import Flask, jsonify, request, send_file
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("MEMBERS_DB_PATH", ROOT / "members.db"))
app = Flask(__name__, static_folder=".", static_url_path="")


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            plan TEXT NOT NULL,
            card_last4 TEXT,
            payment_status TEXT NOT NULL DEFAULT 'pending',
            email_verified INTEGER NOT NULL DEFAULT 0,
            phone_verified INTEGER NOT NULL DEFAULT 0,
            email_code TEXT,
            phone_code TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


init_db()


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def make_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def valid_plus_access_code(submitted_code: str) -> bool:
    configured_code = os.getenv("MEMBERSHIP_ACCESS_CODE", "").strip()
    configured_hash = os.getenv("MEMBERSHIP_ACCESS_CODE_SHA256", "").strip().lower()

    if configured_code:
        return secrets.compare_digest(submitted_code, configured_code)

    if configured_hash:
        submitted_hash = hashlib.sha256(submitted_code.encode("utf-8")).hexdigest()
        return secrets.compare_digest(submitted_hash, configured_hash)

    return False


def send_verification(email: str, phone: str, email_code: str, phone_code: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", "noreply@apotheosischurch.org")

    if smtp_host and smtp_user and smtp_pass:
        msg = EmailMessage()
        msg["Subject"] = "Apotheosis membership verification"
        msg["From"] = smtp_from
        msg["To"] = email
        msg.set_content(
            f"Your verification code is {email_code}.\n"
            f"Your phone verification code is {phone_code}."
        )
        with smtplib.SMTP(smtp_host, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
        return

    print("Email delivery skipped. Configure SMTP vars to send real emails.")
    print(f"Email code for {email}: {email_code}")
    print(f"Phone code for {phone}: {phone_code}")


def process_payment(plan: str) -> dict:
    if plan == "basic":
        return {"status": "free", "message": "Basic membership is free."}

    checkout_variables = {
        "plus": "GODADDY_PLUS_CHECKOUT_URL",
        "plusplus": "GODADDY_PLUSPLUS_CHECKOUT_URL",
        "donation": "GODADDY_DONATION_CHECKOUT_URL",
    }
    checkout_url = os.getenv(checkout_variables.get(plan, ""), "").strip()
    if checkout_url.startswith("https://"):
        return {
            "status": "redirect",
            "checkout_url": checkout_url,
            "message": "Continue to GoDaddy's secure checkout to complete payment.",
        }

    return {
        "status": "unavailable",
        "message": "Secure checkout has not been configured for this option yet.",
    }


@app.route("/")
def index():
    return send_file(ROOT / "index.html")


@app.route("/members")
@app.route("/members.html")
def members_page():
    return send_file(ROOT / "members.html")


@app.route("/api/register", methods=["POST"])
def register_member():
    data = request.form
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = (data.get("password") or "")
    confirm_password = (data.get("confirm_password") or "")
    plan = (data.get("plan") or "basic").strip().lower()
    access_code = (data.get("access_code") or "").strip()

    if not username or not email or not phone or not password:
        return jsonify({"ok": False, "message": "Please fill out all required fields."}), 400
    if password != confirm_password:
        return jsonify({"ok": False, "message": "Passwords do not match."}), 400
    if plan not in {"basic", "plus", "plusplus"}:
        return jsonify({"ok": False, "message": "Please choose a valid membership plan."}), 400

    if access_code and plan == "basic":
        return jsonify({"ok": False, "message": "Private access codes apply to paid memberships."}), 400

    if access_code:
        if not valid_plus_access_code(access_code):
            return jsonify({"ok": False, "message": "That access code is not valid."}), 400
        payment_result = {
            "status": "access-code",
            "message": "Access code accepted. Your membership fee has been waived.",
        }
    else:
        payment_result = process_payment(plan)

    if payment_result["status"] == "unavailable":
        return jsonify({"ok": False, "message": payment_result["message"]}), 503

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO members (username, password_hash, email, phone, plan, card_last4, payment_status, email_code, phone_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                username,
                hash_password(password),
                email,
                phone,
                plan,
                None,
                payment_result["status"],
                make_code(),
                make_code(),
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"ok": False, "message": "That username or email already exists."}), 409

    row = conn.execute(
        "SELECT email_code, phone_code FROM members WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    email_code, phone_code = row
    send_verification(email, phone, email_code, phone_code)

    success_message = "Account created. Please verify your email and phone."
    if payment_result["status"] == "access-code":
        success_message = f"Access code accepted. Your free {plan.replace('plusplus', 'Plus Plus').replace('plus', 'Plus')} account has been created. Please verify your email and phone."
    elif payment_result["status"] == "redirect":
        success_message = "Account created with payment pending. Continue to GoDaddy's secure checkout."

    return jsonify(
        {
            "ok": True,
            "message": success_message,
            "plan": plan,
            "payment": payment_result,
        }
    )


@app.route("/api/verify", methods=["POST"])
def verify_member():
    data = request.form
    username = (data.get("username") or "").strip()
    code = (data.get("code") or "").strip()
    if not username or not code:
        return jsonify({"ok": False, "message": "Username and verification code are required."}), 400

    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT email_code, phone_code, email_verified, phone_verified FROM members WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    if not row:
        return jsonify({"ok": False, "message": "Account not found."}), 404

    email_code, phone_code, email_verified, phone_verified = row
    if code in {email_code, phone_code}:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE members SET email_verified = 1, phone_verified = 1 WHERE username = ?",
            (username,),
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "message": "Your account has been verified."})

    return jsonify({"ok": False, "message": "That verification code is not valid."}), 400


@app.route("/api/donate", methods=["POST"])
def donate():
    data = request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    amount = (data.get("amount") or "0").strip()

    try:
        amount_value = float(amount)
    except ValueError:
        return jsonify({"ok": False, "message": "Please enter a valid donation amount."}), 400

    if not name or not email or not phone or amount_value <= 0:
        return jsonify({"ok": False, "message": "Please complete the donation form."}), 400

    payment_result = process_payment("donation")
    if payment_result["status"] == "unavailable":
        return jsonify({"ok": False, "message": payment_result["message"]}), 503
    reward_message = ""
    if amount_value >= 1000:
        reward_message = " You also receive a free one-year Plus Plus membership."

    return jsonify(
        {
            "ok": True,
            "message": f"Continue to GoDaddy's secure checkout to submit your ${amount_value:.2f} donation." + reward_message,
            "payment": payment_result,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
