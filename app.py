from flask import Flask, request, jsonify
import psycopg2
import os, secrets, datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.route('/recover', methods=['POST'])
def recover():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return jsonify(success=False, error="Invalid email.")

    conn = get_db()
    cur = conn.cursor()
    # Only look up existing user
    cur.execute("SELECT id FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    if user:
        user_id = user[0]
        token = secrets.token_urlsafe(32)
        expiry = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()
        cur.execute("UPDATE users SET reset_token=%s, token_expiry=%s WHERE id=%s", (token, expiry, user_id))
        conn.commit()
        conn.close()
        # Send reset link here (placeholder for actual email logic)
        print(f"[SEND EMAIL] Password reset for {email}: https://leosbakery1310.com/pages/reset-password?token={token}")
        return jsonify(success=True, message="Check your email for a password reset link!")
    else:
        conn.close()
        # No user found—don't reveal this to end user
        return jsonify(success=True, message="Check your email for a password reset link!")
        # PLACEHOLDER: Here is where NEW USER logic would eventually go

# -- Database initialization for reference --
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            reset_token TEXT,
            token_expiry TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
