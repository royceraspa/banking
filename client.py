import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import requests
import locale

class TransferDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Recipient's Username:").grid(row=0, column=0, padx=10, pady=10)
        tk.Label(master, text="Amount to Transfer:").grid(row=1, column=0, padx=10, pady=10)

        self.username_entry = tk.Entry(master, width=20)  # Reduced width
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        self.amount_entry = tk.Entry(master, width=15)  # Reduced width
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10)

        return self.username_entry  # Initial focus on username entry

    def apply(self):
        recipient_username = self.username_entry.get()
        amount = self.amount_entry.get()

        self.result = (recipient_username, amount)

def login(username, password):
    url = 'http://localhost:5000/login'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    return response.json()

def get_balance(username):
    url = f'http://localhost:5000/get_balance?username={username}'
    response = requests.get(url)
    return response.json()

def transfer_balance(sender_username, recipient_username, amount):
    url = 'http://localhost:5000/transfer_balance'
    data = {'sender_username': sender_username, 'recipient_username': recipient_username, 'amount': amount}

    try:
        response = requests.post(url, json=data)
        response_data = response.json()

        if response_data.get('success'):
            return response_data
        else:
            raise ValueError(response_data.get('message', 'Unknown error'))

    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'Request failed: {str(e)}'}

    except ValueError as ve:
        return {'success': False, 'message': f'Invalid response from server: {str(ve)}'}

def format_currency(amount):
    locale.setlocale(locale.LC_ALL, '')  # Use the default locale
    return locale.currency(amount, grouping=True)

def show_balance(event=None):
    username = username_entry.get()
    password = password_entry.get()
    login_response = login(username, password)

    if login_response.get('success'):
        user_info = login_response.get('user_info', {})
        balance_response = get_balance(username)
        if balance_response.get('success'):
            balance = balance_response.get('balance', 0)
            first_name = user_info.get('first_name', '')
            dashboard_label.config(text=f"Welcome, {first_name}!\n\nYour TrustWallet Balance:\n{format_currency(balance)}", font=('Helvetica', 14))
            notebook.tab(tab_dashboard, state='normal')
            notebook.select(tab_dashboard)
        else:
            notebook.tab(tab_dashboard, state='disabled')
            dashboard_label.config(text="Failed to retrieve balance. Please try again.", font=('Helvetica', 16, 'italic'), fg='#FF0000')
    else:
        notebook.tab(tab_dashboard, state='disabled')
        dashboard_label.config(text="Login failed. Please check your credentials.", font=('Helvetica', 16, 'italic'), fg='#FF0000')

def send_balance():
    transfer_dialog = TransferDialog(root)
    result = transfer_dialog.result

    if result:
        recipient_username, amount = result
        username = username_entry.get()

        transfer_response = transfer_balance(username, recipient_username, amount)
        if transfer_response.get('success'):
            show_balance()
            tk.messagebox.showinfo("Transfer Successful", "Balance transfer successful!")
        else:
            tk.messagebox.showerror("Transfer Failed", f"Failed to transfer balance. {transfer_response.get('message')}")

# GUI Setup
root = tk.Tk()
root.title("TrustWallet 1.0")

# Notebook (Tabs)
notebook = ttk.Notebook(root)

# Tab 1: Login
tab_login = ttk.Frame(notebook)
notebook.add(tab_login, text="Login")
notebook.grid(row=0, column=0)

# Username and Password Entry
tk.Label(tab_login, text="Username:").grid(row=0, column=0, pady=10)
username_entry = tk.Entry(tab_login, width=20)  # Reduced width
username_entry.grid(row=0, column=1, pady=10, padx=10)

tk.Label(tab_login, text="Password:").grid(row=1, column=0, pady=10)
password_entry = tk.Entry(tab_login, show="*", width=20)  # Reduced width
password_entry.grid(row=1, column=1, pady=10, padx=10)

# Bind the Return key to the login function
password_entry.bind('<Return>', show_balance)

# Login Button
login_button = tk.Button(tab_login, text="Login", command=show_balance, width=20)
login_button.grid(row=2, column=0, columnspan=2, pady=20)

# Balance Label (removed from login tab)
balance_label = tk.Label(tab_login, text="", font=('Helvetica', 14))
balance_label.grid(row=3, column=0, columnspan=2)

# Tab 2: User Dashboard
tab_dashboard = ttk.Frame(notebook)
notebook.add(tab_dashboard, text="Dashboard")
notebook.grid(row=0, column=0)

# Elements for User Dashboard
dashboard_label = tk.Label(tab_dashboard, text="", font=('Helvetica', 14), padx=20, pady=20)
dashboard_label.pack()

# Send Button
send_button = tk.Button(tab_dashboard, text="Send", command=send_balance, width=20)
send_button.pack(pady=20)

# Disable the User Dashboard tab initially
notebook.tab(tab_dashboard, state='disabled')

# Run the GUI
root.mainloop()
