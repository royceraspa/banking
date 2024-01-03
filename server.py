from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# SQLite database connection
conn = sqlite3.connect('balances.db')
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        balance REAL,
        first_name TEXT,
        last_name TEXT
    )
''')
conn.commit()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user_data = cursor.fetchone()

    if user_data:
        user_info = {'username': user_data[0], 'balance': user_data[2], 'first_name': user_data[3], 'last_name': user_data[4]}
        return jsonify({'success': True, 'message': 'Login successful', 'user_info': user_info})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/get_balance', methods=['GET'])
def get_balance():
    username = request.args.get('username')

    cursor.execute('SELECT balance FROM users WHERE username = ?', (username,))
    balance = cursor.fetchone()

    if balance is not None:
        return jsonify({'success': True, 'balance': balance[0], 'message': 'Balance retrieved successfully'})
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/transfer_balance', methods=['POST'])
def transfer_balance():
    data = request.get_json()
    sender_username = data.get('sender_username')
    recipient_username = data.get('recipient_username')
    amount = float(data.get('amount'))

    cursor.execute('SELECT balance FROM users WHERE username = ?', (sender_username,))
    sender_balance = cursor.fetchone()

    if sender_balance is not None and sender_balance[0] >= amount >= 0:
        cursor.execute('UPDATE users SET balance = balance - ? WHERE username = ?', (amount, sender_username))
        cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, recipient_username))
        conn.commit()

        return jsonify({'success': True, 'message': 'Balance transfer successful'})
    else:
        return jsonify({'success': False, 'message': 'Insufficient funds or invalid amount'}), 400

@app.route('/add_user_form')
def add_user_form():
    return render_template('add_user_form.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.form.to_dict()
    username = data.get('username')
    password = data.get('password')
    balance = float(data.get('balance', 0))
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')

    try:
        cursor.execute('INSERT INTO users (username, password, balance, first_name, last_name) VALUES (?, ?, ?, ?, ?)',
                       (username, password, balance, first_name, last_name))
        conn.commit()

        return jsonify({'success': True, 'message': 'User added successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding user: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='10.0.0.69')
