import configparser
import datetime
import os
import pythoncom

from flask import Flask, render_template, request, redirect, make_response
from flask_login import LoginManager, login_required, login_user, \
    logout_user, current_user, UserMixin

import database
from mail import send_mail

config = configparser.ConfigParser()
config.read('config.ini')

app = Flask(__name__)
app.secret_key = os.urandom(12)

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, id):
        """
        Initialisatiemethode voor het user-object.
        :param id: De naam van de gebruiker.
        """
        self.id = id

    def __str__(self):
        """
        String van het user-object.
        :return: De naam van de gebruiker als een string.
        """
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.route('/', methods=['POST', 'GET'])
def start():
    return redirect("/login")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        staff_code = request.form.get('login_code')
        employed_dict = get_employed()
        if staff_code.isdigit() and int(staff_code) in employed_dict:
            user_name = employed_dict[int(staff_code)]
            user = User(user_name)
            login_user(user)

            response = make_response(redirect("/home"))
            response.set_cookie('username', user_name)

            return response
        else:
            return render_template("login.html", error_messenger=True)
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if request.method == "POST":
        action = request.form.get('button_home')
        if action == "repair":
            return redirect("/new_repair")
        elif action == "order":
            return redirect("/new_order")
        elif action == "get_repair":
            return redirect("/get_repair")
        elif action == "get_order":
            return redirect("/get_order")
    return render_template("home.html")

@app.route('/new_repair', methods=['POST', 'GET'])
@login_required
def new_repair():
    employed_dict = get_employed()
    employed_list = list(employed_dict.values())
    date = datetime.date.today().strftime("%d-%m-%Y")
    return render_template("/repair/new_repair.html", employed_list=employed_list, date=date, current_user=current_user)


@app.route('/new_order', methods=['POST', 'GET'])
@login_required
def new_order():
    brands = get_brands()
    return render_template("/order/new_order.html", current_user=current_user, brands=brands)


@app.route('/get_repair', methods=['POST', 'GET'])
@login_required
def get_repair():
    table = "repairs"
    data = database.get_table_data_repair(table)
    return render_template("/repair/repairs_table.html", data=data, table=table)


@app.route('/get_order', methods=['POST', 'GET'])
@login_required
def get_order():
    table = "orders"
    data = database.get_table_data_order(table)
    brands = get_brands()
    return render_template("/order/orders_table.html", data=data, table=table, brands=brands)


@app.route('/get_old_repair', methods=['POST', 'GET'])
@login_required
def get_old_repair():
    table = "old_repairs"
    data = database.get_table_data_repair(table)
    return render_template("/repair/repairs_table.html", data=data, table=table)


@app.route('/get_old_order', methods=['POST', 'GET'])
@login_required
def get_old_order():
    table = "old_orders"
    data = database.get_table_data_order(table)
    brands = get_brands()
    return render_template("/order/orders_table.html", data=data, table=table,
                           brands=brands)


@app.route('/select', methods=['POST'])
@login_required
def select_row():
    id = request.form['row_id']
    table = request.form['table']
    if table == "repairs" or table == "old_repairs":
        data = database.get_repair(table, id)
    else:
        data = database.get_order(table, id)
    log_data = get_log(id)
    if table == "repairs":
        return render_template("/repair/show_repair.html", data=data, log_data=log_data)
    elif table == "old_repairs":
        return render_template("/repair/show_old_repair.html", data=data, log_data=log_data)
    elif table == "orders":
        return render_template("/order/show_order.html", data=data, log_data=log_data)
    elif table == "old_orders":
        return render_template("/order/show_old_order.html", data=data, log_data=log_data)


@app.route('/insert_repair', methods=['POST'])
@login_required
def insert_repair():
    """
    Verwerk het invoegen van een nieuwe reparatie in de database.

    :return: Een omleiding naar '/get_repair'.
    :return: Een weergave van 'new_repair.html' met een foutmelding als
     het reparatienummer al bestaat.
    """
    if request.method == 'POST':
        date = datetime.date.today().strftime("%d-%m-%Y")
        data = {
            'repair_number': request.form['repair_number'],
            'date': date,
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'phone_number': request.form['phone_number'],
            'email': request.form['email'],
            'brand': request.form['brand'],
            'article': request.form['article'],
            'repairman': request.form['repairman'],
            'price': "",
            'repair_reason': request.form['repair_reason'].replace('\r\n', ' '),
            'remark': request.form['remark'].replace('\r\n', ' '),
            'employee': str(current_user),
            'emailed': "",
            'status': 'ongoing'
        }
        
        if data['repair_number'] != "" and not \
                database.repair_exists(data['repair_number']):
            database.insert_repair(data)
            print_label_repair(data)
            user_log('insert', data['repair_number'], current_user)
            database.export_data_to_txt("repairs")
            database.export_data_to_txt("old_repairs")
            return redirect("/get_repair")
        return render_template("/repair/new_repair.html",
                               data=data,
                               repair_number_exists=True)


@app.route('/insert_order', methods=['POST'])
@login_required
def insert_order():
    if request.method == 'POST':
        data = {
            'order_number': datetime.datetime.now().strftime("%d-%m-%Y_%H:%M:%S"),
            'implemented_date': datetime.date.today().strftime("%d-%m-%Y"),
            'ordered_date': "",
            'contacted_date': "",
            'fetched_date': "",
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'phone_number': request.form['phone_number'],
            'email': request.form['email'],
            'brand': request.form['brand'],
            'article': request.form['article'],
            'size': request.form['size'],
            'price': request.form['price'],
            'paid': request.form['paid'],
            'remark': request.form['remark'].replace('\r\n', ' \ '),
            'employee': str(current_user),
            'status': 'implemented'
        }
        database.insert_order(data)
        user_log('insert', data['order_number'], current_user)
        database.export_data_to_txt("orders")
        database.export_data_to_txt("old_orders")
    return redirect("/get_order")


def print_label_repair(data):
    repair_number = data["repair_number"]
    date = data["date"]
    article = data["brand"] + " " + data["article"]

    repair_reason = data["repair_reason"]

    repair_reason1 = repair_reason
    repair_reason2 = ""
    repair_reason3 = ""

    if len(repair_reason) > 45:
        repair_reason1, x = split_text(repair_reason, 45)
        repair_reason2, x = split_text(x, 45)
    if len(repair_reason) > 90:
        repair_reason3, _ = split_text(x, 45)

    name = data["first_name"] + " " + data["last_name"]
    phone_number = data["phone_number"]
    data2 = [repair_number, date, article, repair_reason1, repair_reason2, repair_reason3, name, phone_number]
    with open("label/label_repair.txt", "w") as file:
        file.write("\t".join(["Nummer", "Datum", "Artikel", "Defect1", "Defect2", "Defect3" "naam", "Telefoonnummer"]) + "\n")
        file.write("\t".join(data2))

def split_text(text, length):
    if len(text) <= length:
        return text, ""
    else:
        last_space_index = text.rfind(' ', 0, length)
        if last_space_index != -1:
            return text[:last_space_index], text[last_space_index+1:]
        else:
            return text[:length], text[length:]


def print_label_order(data):
    date = data["contacted_date"]
    name = data["first_name"] + " " + data["last_name"]
    article = data["brand"] + " " + data["article"] + " " + data["size"]
    paid = data["paid"]
    data2 = [name, date, article, paid]
    with open("label/label_order.txt", "w") as file:
        file.write("\t".join(["naam", "Datum", "Artikel", "paid1"]) + "\n")
        file.write("\t".join(data2))


@app.route('/repair_buttons', methods=['POST'])
@login_required
def button_checker_repair():
    action = request.form.get('button_repairs')
    data = {
        'repair_number': request.form['repair_number'],
        'date': request.form['date'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'phone_number': request.form['phone_number'],
        'email': request.form['email'],
        'brand': request.form['brand'],
        'article': request.form['article'],
        'repairman': request.form['repairman'],
        'price': request.form['price'],
        'repair_reason': request.form['repair_reason'].replace('\r\n', ' '),
        'remark': request.form['remark'].replace('\r\n', ' '),
        'employee': request.form['employee'],
        'emailed': request.form['emailed'],
        'status': request.form['status']
    }
    if action == 'update':
        database.update_repair(data['repair_number'], data)
        user_log('update', data['repair_number'], current_user)
    elif action == 'mail':
        error_message = mail(data)
        if error_message:
            return render_template('/repair/show_repair.html',
                                   data=data,
                                   error_message=error_message)
    elif action == 'call':
        database.call_status(data['repair_number'])
        user_log('call', data['repair_number'], current_user)
    elif action == 'fetched':
        database.move_repair(data['repair_number'])
        user_log('fetched', data['repair_number'], current_user)
    elif action == 'label':
        print_label_repair(data)
    elif action == 'reset':
        database.reset_status_repair(data['repair_number'])
        user_log('reset_contacted', data['repair_number'], current_user)
    database.export_data_to_txt("repairs")
    database.export_data_to_txt("old_repairs")
    return redirect('/get_repair')


@app.route('/order_buttons', methods=['POST'])
@login_required
def button_checker_orders():
    action = request.form.get('order_buttons')
    data = {
        'order_number': request.form['order_number'],
        'implemented_date': request.form['implemented_date'],
        'ordered_date': request.form['ordered_date'],
        'contacted_date': request.form['contacted_date'],
        'fetched_date': request.form['fetched_date'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'phone_number': request.form['phone_number'],
        'email': request.form['email'],
        'brand': request.form['brand'],
        'article': request.form['article'],
        'size': request.form['size'],
        'price': request.form['price'],
        'paid': request.form['paid'],
        'remark': request.form['remark'].replace('\r\n', ' / '),
        'employee': request.form['employee'],
        'status': request.form['status']
    }
    if action == 'update':
        database.update_order(data['order_number'], data)
        user_log('update', data['order_number'], current_user)
    elif action == 'ordered':
        database.ordered_status(data['order_number'])
        user_log('ordered', data['order_number'], current_user)
    elif action == 'contacted':
        database.contacted_status(data['order_number'])
        user_log('contacted', data['order_number'], current_user)
    elif action == 'print':
        print_label_order(data)
    elif action == 'fetched':
        database.move_order(data['order_number'])
        user_log('fetched', data['order_number'], current_user)
    elif action == 'reset_ordered':
        database.reset_ordered_status(data['order_number'])
        user_log('reset_fetched', data['order_number'], current_user)
    elif action == 'reset_contacted':
        database.reset_contacted_status(data['order_number'])
        user_log('reset_contacted', data['order_number'], current_user)
    database.export_data_to_txt("orders")
    database.export_data_to_txt("old_orders")
    return redirect('/get_order')

@app.route('/button_checker_old_repair', methods=['POST'])
@login_required
def button_checker_old_repair():
    action = request.form.get('button_old_repair')
    repair_number = request.form['repair_number']
    if action == 'move_repair_back':
        database.move_repair_back(repair_number)
        user_log('repair_back', repair_number, current_user)
    return redirect("/get_repair")

@app.route('/button_checker_old_order', methods=['POST'])
@login_required
def button_checker_old_order():
    action = request.form.get('button_old_order')
    order_number = request.form['order_number']
    if action == 'move_order_back':
        database.move_order_back(order_number)
        user_log('order_back', order_number, current_user)
    return redirect("/get_order")

@app.route('/import', methods=['POST'])
@login_required
def import_file():
    file_name = request.form['file_import']
    table = "repairs"
    if "old" in file_name:
        table = "old_repairs"
    import_directory = config.get("paths", "export_directory")
    error = database.import_file_to_db(file_name, table, import_directory)
    if error:
        pass
    return redirect("/new_repair.html")


@app.route('/export', methods=['POST'])
@login_required
def export_file():
    table = request.form.get('file_export')
    export_directory = config.get("paths", "export_directory")
    database.export_data_to_txt(table, export_directory)
    return redirect("/new_repair.html")


def user_log(route, ref_number, employee):
    log_file_path = config.get("paths", "user_log_file")
    date = datetime.datetime.today().strftime("%d-%m-%Y %H:%M")
    log_message = f"{date}\t{route}\t{ref_number}\t{employee}"
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_message + '\n')


def get_employed():
    directory = config.get("paths", "staff")
    with open(directory, "r") as file:
        employed_dict = {}
        for line in file:
            employe = line.strip().split(" ")
            employed_dict[int(employe[1])] = employe[0]
    return employed_dict


def get_log(repair_number):
    log_file_path = config.get("paths", "user_log_file")
    repair_log = []
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            s_line = line.strip().split("\t")
            if s_line[2] == repair_number:
                repair_log.append(s_line)
    return repair_log


def get_brands():
    directory = config.get("paths", "brands")
    with open(directory, "r") as file:
        brands = []
        for line in file:
            brands.append(line.strip())
    return brands


@app.route('/', methods=['POST'])
@login_required
def mail(data):
    pythoncom.CoInitialize()
    repair_number = data['repair_number']
    email = data['email']
    last_name = data['last_name']
    price = data['price']
    if repair_number and email and last_name and price:
        database.mail_status(repair_number, price)
        send_mail(email, repair_number, last_name, price)
        user_log('mail', repair_number, current_user)
        redirect("/new_repair")
    else:
        empty = [f for f, v in [('email', email),
                                ('achternaam', last_name),
                                ('prijs', price)] if not v]
        error_message = "Volgende gegevens zijn leeg: {}. Vul " \
                        "dit aan om te mailen!".format(", ".join(empty))
        return error_message


@app.errorhandler(401)
def internal_server_error(error):
    """
    Tijdens een 401 error wordt deze functie aangeroepen.
    :param error: de error van HTML
    :return: render_template met error.html template en de error van HTML.
    """
    # error_log(erroSr)
    return render_template('error.html', error=error), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
