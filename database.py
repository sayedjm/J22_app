import configparser
import sqlite3

from datetime import date, datetime

from mail import send_mail


config = configparser.ConfigParser()
config.read('config.ini')

TABLE_REPAIR = '''
    CREATE TABLE IF NOT EXISTS repairs (
        repair_number TEXT UNIQUE,
        date TEXT,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        email TEXT,
        brand TEXT,
        article TEXT,
        repairman TEXT,
        price INTEGER,
        repair_reason TEXT,
        remark TEXT,
        employee TEXT,
        emailed TEXT,
        status TEXT
    )
'''

TABLE_OLD_REPAIR = '''
    CREATE TABLE IF NOT EXISTS old_repairs (
        repair_number TEXT UNIQUE,
        date TEXT,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        email TEXT,
        brand TEXT,
        article TEXT,
        repairman TEXT,
        price INTEGER,
        repair_reason TEXT,
        remark TEXT,
        employee TEXT,
        emailed TEXT,
        status TEXT
    )
'''

TABLE_ORDERS = '''
    CREATE TABLE IF NOT EXISTS orders (
        order_number TEXT,
        implemented_date TEXT,
        ordered_date TEXT,
        contacted_date TEXT,
        fetched_date TEXT,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        email TEXT,
        brand TEXT,
        article TEXT,
        size TEXT,
        price TEXT,
        paid TEXT,
        remark TEXT,
        employee TEXT,
        status TEXT
    )
'''

TABLE_OLD_ORDERS = '''
    CREATE TABLE IF NOT EXISTS old_orders (
        order_number INTEGER,
        implemented_date TEXT,
        ordered_date TEXT,
        contacted_date TEXT,
        fetched_date TEXT,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        email TEXT,
        brand TEXT,
        article TEXT,
        size TEXT,
        price TEXT,
        paid TEXT,
        remark TEXT,
        employee TEXT,
        status TEXT
    )
'''

TABLE_REPAIR_INSERT = '''
    INSERT INTO repairs (
        repair_number, date, first_name, last_name, phone_number, 
        email, brand, article, repairman, price, repair_reason, 
        remark, employee, emailed, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
'''

TABLE_OLD_REPAIR_INSERT = '''
    INSERT INTO old_repairs (
        repair_number, date, first_name, last_name, phone_number, 
        email, brand, article, repairman, price, repair_reason, 
        remark, employee, emailed, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
'''

TABLE_ORDERS_INSERT = '''
    INSERT INTO orders (
        order_number, implemented_date, ordered_date, contacted_date, fetched_date, first_name, last_name, phone_number, 
        email, brand, article, size, price, paid, remark, employee, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
'''

TABLE_OLD_ORDER_INSERT = '''
    INSERT INTO old_orders (
        order_number, implemented_date, ordered_date, contacted_date, fetched_date, first_name, last_name, phone_number, 
        email, brand, article, size, price, paid, remark, employee, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
'''

def connection():
    """
    Maak een verbinding met de SQLite3-database en
    retourneer een connectie en een cursor.
    :return: Een tuple met de connectie en de cursor.
    """
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    return conn, cursor


def create_table():
    """
    Maak de tabellen in de database wanneer ze
    nog niet bestaan.
    """
    conn, cursor = connection()
    cursor.execute(TABLE_REPAIR)
    cursor.execute(TABLE_OLD_REPAIR)
    cursor.execute(TABLE_ORDERS)
    cursor.execute(TABLE_OLD_ORDERS)
    conn.commit()
    conn.close()


def insert_repair(repair_data):
    """
    Voeg data toe aan de 'repairs' tabel in de database.
    :param repair_data: Een dictionary met de reparatiegegevens.
    """
    conn, cursor = connection()
    cursor.execute(TABLE_REPAIR_INSERT, tuple(repair_data.values()))
    conn.commit()
    conn.close()


def insert_order(order_data):
    conn, cursor = connection()
    cursor.execute(TABLE_ORDERS_INSERT, tuple(order_data.values()))
    conn.commit()
    conn.close()


def get_repair(table, repair_number):
    conn, cursor = connection()
    cursor.execute("SELECT * FROM {} WHERE repair_number=?".format(table),
                   (repair_number,))
    result = list(cursor.fetchone())
    conn.close()
    data = {
        'repair_number': result[0],
        'date': result[1],
        'first_name': result[2],
        'last_name': result[3],
        'phone_number': result[4],
        'email': result[5],
        'brand': result[6],
        'article': result[7],
        'repairman': result[8],
        'price': result[9],
        'repair_reason': result[10],
        'remark': result[11],
        'employee': result[12],
        'emailed': result[13],
        'status': result[14],
    }
    return data

def get_order(table, repair_number):
    conn, cursor = connection()
    cursor.execute("SELECT * FROM {} WHERE order_number=?".format(table),
                   (repair_number,))
    result = list(cursor.fetchone())
    conn.close()
    data = {
        'order_number': result[0],
        'implemented_date': result[1],
        'ordered_date': result[2],
        'contacted_date': result[3],
        'fetched_date': result[4],
        'first_name': result[5],
        'last_name': result[6],
        'phone_number': result[7],
        'email': result[8],
        'brand': result[9],
        'article': result[10],
        'size': result[11],
        'price': result[12],
        'paid': result[13],
        'remark': result[14],
        'employee': result[15],
        'status': result[16],
    }
    return data


def get_table_data_repair(table):
    """
    Haal gegevens op van de opgegeven tabel voor de table in
    'search.html'.
    :param table: De naam van de tabel waarvan gegevens moeten
    worden opgehaald.
    :return: Een tuple met de gegevens van de tabel en het
    aantal reparaties.
    """
    conn, cursor = connection()
    cursor.execute("SELECT repair_number, date, first_name,"
                   " last_name, brand, article, status FROM {}".format(table))
    data = cursor.fetchall()
    current_date = date.today()
    data2 = []
    for repair in data:
        data = list(repair)
        repair_date = datetime.strptime(data[1], "%d-%m-%Y").date()
        data.append(abs((current_date - repair_date).days))
        data2.append(tuple(data))
    conn.close()
    return data2


def get_table_data_order(table):
    conn, cursor = connection()
    cursor.execute("SELECT order_number, implemented_date, ordered_date,"
                   "contacted_date, first_name, last_name, brand,"
                   " article, status FROM {}".format(table))
    data = cursor.fetchall()
    conn.close()
    return data


def update_repair(repair_number, data):
    """
     Werk een reparatie bij in de 'repairs' tabel in de database.
     :param repair_number: Het reparatienummer van de reparatie
     die moet worden bijgewerkt.
     :param data: Een dictionary met de bij te werken reparatiegegevens.
     """
    conn, cursor = connection()
    cursor.execute('''UPDATE repairs SET
                          repair_number = ?,
                          date = ?,
                          first_name = ?,
                          last_name = ?,
                          phone_number = ?,
                          email = ?,
                          brand = ?,
                          article = ?,
                          repairman = ?,
                          price = ?,
                          repair_reason = ?,
                          remark = ?,
                          employee = ?,
                          emailed = ?,
                          status = ?
                      WHERE repair_number = ?
                  ''', (*data.values(), repair_number))
    conn.commit()
    conn.close()


def update_order(order_number, data):
    conn, cursor = connection()
    cursor.execute('''UPDATE orders SET
                          order_number = ?,
                          implemented_date = ?,
                          ordered_date = ?,
                          contacted_date = ?,
                          fetched_date = ?,
                          first_name = ?,
                          last_name = ?,
                          phone_number = ?,
                          email = ?,
                          brand = ?,
                          article = ?,
                          size = ?,
                          price = ?,
                          paid = ?,
                          remark = ?,
                          employee = ?,
                          status = ?
                      WHERE order_number = ?
                  ''', (*data.values(), order_number))
    conn.commit()
    conn.close()


def mail_status(repair_number, price):
    """
    Werk de status en prijs van een reparatie bij in de 'repairs' tabel.

    :param repair_number: Het reparatienummer van de reparatie die
    moet worden bijgewerkt.
    :param price: De nieuwe prijs van de reparatie.
    """
    c_date = date.today().strftime("%d-%m-%Y")
    conn, cursor = connection()
    cursor.execute('''UPDATE repairs SET status = ?, price = ?, emailed = ? WHERE repair_number = ?''', (*["finish", price, c_date], repair_number))
    conn.commit()
    conn.close()


def call_status(repair_number):
    """
    Werk de status  van een reparatie bij in de 'repairs' tabel.

    :param repair_number: Het reparatienummer van de reparatie die
    moet worden bijgewerkt.
    """
    c_date = date.today().strftime("%d-%m-%Y")
    conn, cursor = connection()
    cursor.execute('''UPDATE repairs SET status = ?, emailed = ? WHERE repair_number = ?''', (*["finish", c_date], repair_number))
    conn.commit()
    conn.close()


def ordered_status(order_number):
    c_date = date.today().strftime("%d-%m-%Y")
    conn, cursor = connection()
    cursor.execute('''UPDATE orders SET status = ?, ordered_date = ? WHERE order_number = ?''', (*["ordered", c_date], order_number))
    conn.commit()
    conn.close()


def contacted_status(order_number):
    c_date = date.today().strftime("%d-%m-%Y")
    conn, cursor = connection()
    cursor.execute('''UPDATE orders SET status = ?, contacted_date = ? WHERE order_number = ? ''', (*["contacted", c_date], order_number))
    conn.commit()
    conn.close()

def reset_status_repair(repair_number):
    conn, cursor = connection()
    cursor.execute('''UPDATE repairs SET status = ?,emailed = ? WHERE repair_number = ? ''', (*["ongoing", ""], repair_number))
    conn.commit()
    conn.close()

def reset_ordered_status(order_number):
    conn, cursor = connection()
    cursor.execute('''UPDATE orders SET status = ?,ordered_date = ? WHERE order_number = ?''', (*["implemented", ""], order_number))
    conn.commit()
    conn.close()

def reset_contacted_status(order_number):
    conn, cursor = connection()
    cursor.execute('''UPDATE orders SET status = ?, contacted_date = ? WHERE order_number = ?''',(*["ordered", ""], order_number))
    conn.commit()
    conn.close()

def move_repair(repair_number):
    """
    Verplaats een reparatie van de 'repairs' tabel naar de 'old_repairs'
    tabel in de database.
    :param repair_number: Het reparatienummer van de reparatie die
    moet worden verplaatst.
    """

    conn, cursor = connection()
    cursor.execute('INSERT INTO old_repairs SELECT * FROM repairs WHERE repair_number = ?', (repair_number,))
    cursor.execute('UPDATE repairs SET status = ?, emailed = ? WHERE repair_number = ?', (*["finish", ""], repair_number))
    cursor.execute('DELETE FROM repairs WHERE repair_number = ?', (repair_number,))
    conn.commit()
    conn.close()


def move_order(order_number):
    conn, cursor = connection()
    cursor.execute('INSERT INTO old_orders SELECT * FROM orders WHERE order_number = ?', (order_number,))
    cursor.execute('DELETE FROM orders WHERE order_number = ?', (order_number,))
    conn.commit()
    conn.close()


def repair_exists(repair_number):
    """
    Controleer of een reparatie bestaat in de 'repairs' tabel op basis van
     het reparatienummer.
    :param repair_number: Het reparatienummer van de te controleren reparatie.
    :return: True als de reparatie bestaat, False anders.
    """
    conn, cursor = connection()
    cursor.execute('SELECT repair_number FROM repairs WHERE repair_number = ?', (repair_number,))
    result = cursor.fetchone()
    result1 = result
    cursor.execute('SELECT repair_number FROM old_repairs WHERE repair_number = ?', (repair_number,))
    result2 = cursor.fetchone()
    conn.close()
    return result1 is not None or result2 is not None


def move_repair_back(repair_number):
    conn, cursor = connection()
    cursor.execute('INSERT INTO repairs SELECT * FROM old_repairs WHERE repair_number = ?', (repair_number,))
    cursor.execute('DELETE FROM old_repairs WHERE repair_number = ?', (repair_number,))
    conn.commit()
    conn.close()

def move_order_back(order_number):
    conn, cursor = connection()
    cursor.execute('INSERT INTO orders SELECT * FROM old_orders WHERE order_number = ?', (order_number,))
    cursor.execute('DELETE FROM old_orders WHERE order_number = ?', (order_number,))
    conn.commit()
    conn.close()


def export_data_to_txt(table):
    export_directory = config.get("paths", "export_directory")
    conn, cursor = connection()
    cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()
    conn.close()
    current_datetime = datetime.now()
    filename = f'{table}_{current_datetime.strftime("%Y-%m-%d_%H-%M")}.txt'
    with open(export_directory + filename, 'w') as file:
        header = [description[0] for description in cursor.description]
        file.write('\t'.join(header) + '\n')
        for row in rows:
            file.write('\t'.join(str(value) for value in row) + '\n')


def import_file_to_db(file_name, table, import_directory):

    conn, cursor = connection()
    with open(import_directory + file_name, "r") as file:
        header_file = file.readline().strip().split("\t")
        cursor.execute(f'SELECT * FROM {table}')
        header_table = [description[0] for description in cursor.description]
        if len(header_file) == len(header_table):
            cursor.execute(f'''DROP TABLE IF EXISTS  {table}''')
            create_table()
            for line in file:
                split_Line = line.strip().split("\t")
                if table == "repairs":
                    cursor.execute(TABLE_REPAIR_INSERT, tuple(split_Line))
                elif table == "old_repairs":
                    cursor.execute(TABLE_OLD_REPAIR_INSERT, tuple(split_Line))
                conn.commit()
            conn.close()
        else:
            conn.close()
            return True

def een():
    create_table()

    conn = sqlite3.connect('database/oud.db')
    cursor = conn.cursor()

    conn2 = sqlite3.connect('database/database.db')
    cursor2 = conn2.cursor()

    cursor.execute(f'SELECT * FROM repairs')
    rows = cursor.fetchall()
    for r in rows:
        cursor2.execute(TABLE_REPAIR_INSERT, r)

    cursor.execute(f'SELECT * FROM old_repairs')
    rows = cursor.fetchall()
    for r in rows:
        cursor2.execute(TABLE_OLD_REPAIR_INSERT, r[:15])

    cursor.execute(f'SELECT * FROM orders')
    rows = cursor.fetchall()
    for r in rows:
        cursor2.execute(TABLE_ORDERS_INSERT, (r[:14] + r[19:]))

    cursor.execute(f'SELECT * FROM old_orders')
    rows = cursor.fetchall()
    for r in rows:
        cursor2.execute(TABLE_OLD_ORDER_INSERT, (r[:14] + r[19:]))

    conn2.commit()
    conn2.close()

if __name__ == '__main__':
    een()
