
from flask import Flask, request, jsonify
import psycopg2
import os, secrets, datetime
from flask_cors import CORS
import sendgrid
from sendgrid.helpers.mail import Mail

def send_reset_email(to_email, token):
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    html_content = f"""
        <img src='https://YOUR_LOGO_URL_TOP.png' style='width:120px;'><br><br>
        <p>You forgot your password again, didn't ya? Yeah, yeah, we know, we know .. Click the link below. You've got 1 minute.</p>
        <a href="https://www.leosbakery1310.com/pages/recovery?token={token}">Reset Password</a>
        <br><br>
        <img src='https://YOUR_LOGO_URL_BOTTOM.png' style='width:60px;'>
    """
    message = Mail(
        from_email='support@leosbakery1310.com',
        to_emails=to_email,
        subject="Leo's Bakery",
        html_content=html_content
    )
    sg.send(message)

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
        send_reset_email(email, token)
        return jsonify(success=True, message="Check your email for a password reset link!")
    else:
        conn.close()
        # No user found—don't reveal this to end user
        return jsonify(success=True, message="Check your email")
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
