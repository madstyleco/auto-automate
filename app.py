from flask import Flask, request, jsonify

app = Flask(__name__)

# Dummy "database" for testing
valid_emails = ["joe@example.com", "jane@example.com"]

@app.route('/recover', methods=['POST'])
def recover():
    data = request.get_json()
    email = data.get('email', '')
    exists = email.lower() in valid_emails
    return jsonify({'exists': exists})

if __name__ == '__main__':
    app.run()
