
import sqlite3
from werkzeug.security import generate_password_hash

def create_tables():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_lots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prime_location_name TEXT NOT NULL,
            price REAL NOT NULL,
            address TEXT,
            pin_code TEXT,
            max_spots INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parking_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lot_id INTEGER,
            status TEXT DEFAULT 'A',
            FOREIGN KEY (lot_id) REFERENCES parking_lots(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id INTEGER,
            user_id INTEGER,
            parking_timestamp TEXT,
            leaving_timestamp TEXT,
            FOREIGN KEY (spot_id) REFERENCES parking_spots(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute("SELECT * FROM users WHERE is_admin = 1")
    if not cursor.fetchone():
        hash=generate_password_hash('admin123')
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ('admin', hash, 1))

    conn.commit()
    conn.close()
    
def check_tables():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("Tables in app.db:")
    for table in tables:
        print("-", table[0])

    conn.close()
    
def updates():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # cursor.execute("ALTER TABLE parking_lots ADD COLUMN available_spots INTEGER DEFAULT 0")
    # cursor.execute("ALTER TABLE reservations ADD COLUMN lot_id INTEGER;")
    # cursor.execute("ALTER TABLE reservations ADD COLUMN total_cost REAL;")
    # cursor.execute("ALTER TABLE parking_lots ADD COLUMN status TEXT DEFAULT 'active';")
    # cursor.execute("SELECT id, status FROM parking_lots;")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)
    cursor.execute("DELETE FROM parking_lots")
    conn.commit()
    conn.close()
    
import sqlite3

def insert_parking_lots():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    parking_lots_data = [
        ('Connaught Place', 40.00, 'Connaught Place, New Delhi', '110001', 50),
        ('MG Road', 35.00, 'MG Road, Bengaluru, Karnataka', '560001', 60),
        ('T. Nagar', 30.00, 'T. Nagar, Chennai, Tamil Nadu', '600017', 45),
        ('Banjara Hills', 50.00, 'Banjara Hills, Hyderabad, Telangana', '500034', 55),
        ('Park Street', 38.00, 'Park Street, Kolkata, West Bengal', '700016', 40),
        ('Sector 17', 25.00, 'Sector 17, Chandigarh', '160017', 35),
        ('Koregaon Park', 45.00, 'Koregaon Park, Pune, Maharashtra', '411001', 60),
        ('Hazratganj', 30.00, 'Hazratganj, Lucknow, Uttar Pradesh', '226001', 50),
        ('Lalbagh', 28.00, 'Lalbagh, Mangaluru, Karnataka', '575003', 30),
        ('C-Scheme', 32.00, 'C-Scheme, Jaipur, Rajasthan', '302001', 48),
        ('VIP Road', 34.00, 'VIP Road, Surat, Gujarat', '395007', 40),
        ('Ashram Road', 36.00, 'Ashram Road, Ahmedabad, Gujarat', '380009', 42),
        ('Abids', 29.00, 'Abids, Hyderabad, Telangana', '500001', 38),
        ('Camp', 33.00, 'Camp Area, Pune, Maharashtra', '411001', 52),
        ('Rajajinagar', 31.00, 'Rajajinagar, Bengaluru, Karnataka', '560010', 39),
        ('Salt Lake', 37.00, 'Salt Lake Sector V, Kolkata', '700091', 44),
        ('Anna Nagar', 34.00, 'Anna Nagar, Chennai, Tamil Nadu', '600040', 50),
        ('Rajpur Road', 28.00, 'Rajpur Road, Dehradun, Uttarakhand', '248001', 36),
        ('Indiranagar', 41.00, 'Indiranagar, Bengaluru, Karnataka', '560038', 60),
        ('Gariahat', 35.00, 'Gariahat, Kolkata, West Bengal', '700019', 42),
        ('Civil Lines', 30.00, 'Civil Lines, Nagpur, Maharashtra', '440001', 50),
        ('Gomti Nagar', 32.00, 'Gomti Nagar, Lucknow, Uttar Pradesh', '226010', 56),
        ('Sector 62', 27.00, 'Sector 62, Noida, Uttar Pradesh', '201309', 48),
        ('Hitech City', 50.00, 'Hitech City, Hyderabad, Telangana', '500081', 70),
        ('Bistupur', 26.00, 'Bistupur, Jamshedpur, Jharkhand', '831001', 40),
        ('Alkapuri', 29.00, 'Alkapuri, Vadodara, Gujarat', '390007', 36),
        ('Ravet', 22.00, 'Ravet, Pune, Maharashtra', '412101', 30),
        ('Jayanagar', 33.00, 'Jayanagar, Bengaluru, Karnataka', '560041', 52),
        ('Kakadeo', 20.00, 'Kakadeo, Kanpur, Uttar Pradesh', '208025', 28),
        ('Gandhipuram', 25.00, 'Gandhipuram, Coimbatore, Tamil Nadu', '641012', 34)
    ]

    # Insert parking lots
    cursor.executemany('''
        INSERT INTO parking_lots (prime_location_name, price, address, pin_code, max_spots)
        VALUES (?, ?, ?, ?, ?)
    ''', parking_lots_data)

    # Get all parking lot IDs to create spots
    cursor.execute('SELECT id, max_spots FROM parking_lots')
    lots = cursor.fetchall()
    
    # Create parking spots for each lot
    for lot_id, max_spots in lots:
        for _ in range(max_spots):
            cursor.execute('INSERT INTO parking_spots (lot_id, status) VALUES (?, ?)', (lot_id, 'A'))
    
    print(f"Created {len(parking_lots_data)} parking lots with their respective spots")
    
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables()
    check_tables()
    # updates()
    insert_parking_lots()
