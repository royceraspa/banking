from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///balances.db'
db = SQLAlchemy(app)

class User(db.Model):
    username = db.Column(db.String(80), primary_key=True)
    password = db.Column(db.String(80))
    balance = db.Column(db.Float)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))

with app.app_context():
    db.create_all()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user_data = User.query.filter_by(username=username, password=password).first()

    if user_data:
        user_info = {'username': user_data.username, 'balance': user_data.balance, 'first_name': user_data.first_name, 'last_name': user_data.last_name}
        return jsonify({'success': True, 'message': 'Login successful', 'user_info': user_info})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/get_balance', methods=['GET'])
def get_balance():
    username = request.args.get('username')

    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify({'success': True, 'balance': user.balance, 'message': 'Balance retrieved successfully'})
    else:
        return jsonify({'success': False, 'message': 'User not found'}), 404

@app.route('/transfer_balance', methods=['POST'])
def transfer_balance():
    data = request.get_json()
    sender_username = data.get('sender_username')
    recipient_username = data.get('recipient_username')
    amount = float(data.get('amount'))

    sender = User.query.filter_by(username=sender_username).first()

    if sender and sender.balance >= amount >= 0:
        sender.balance -= amount

        recipient = User.query.filter_by(username=recipient_username).first()
        recipient.balance += amount

        db.session.commit()

        return jsonify({'success': True, 'message': 'Balance transfer successful'})
    else:
        return jsonify({'success': False, 'message': 'Insufficient funds or invalid amount'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='10.0.0.69')
