from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for simplicity (not suitable for production)
user_credentials = {
    'royceraspa': {'password': 'royce2003', 'balance': 1, 'first_name': 'Royce', 'last_name': 'Raspa'},
    'alexbeck': {'password': 'alex2003', 'balance': 0, 'first_name': 'Alex', 'last_name': 'Beck'}
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in user_credentials and user_credentials[username]['password'] == password:
        user_info = user_credentials[username]
        return jsonify({'success': True, 'message': 'Login successful', 'user_info': user_info})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/get_balance', methods=['GET'])
def get_balance():
    username = request.args.get('username')

    if username in user_credentials:
        balance = user_credentials[username]['balance']
        return jsonify({'success': True, 'balance': balance, 'message': 'Balance retrieved successfully'})
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/transfer_balance', methods=['POST'])
def transfer_balance():
    data = request.get_json()
    sender_username = data.get('sender_username')
    recipient_username = data.get('recipient_username')
    amount = float(data.get('amount'))  # Convert amount to float

    if sender_username in user_credentials and recipient_username in user_credentials:
        sender_balance = user_credentials[sender_username]['balance']

        if sender_balance >= amount >= 0:
            user_credentials[sender_username]['balance'] -= amount
            user_credentials[recipient_username]['balance'] += amount

            return jsonify({'success': True, 'message': 'Balance transfer successful'})
        else:
            return jsonify({'success': False, 'message': 'Insufficient funds or invalid amount'}), 400
    else:
        return jsonify({'success': False, 'message': 'Invalid sender or recipient username'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
