from flask import Flask, jsonify,render_template,request,flash,redirect
from flask import session # for state management, agar user logged in hai tw he/she doesn't have to login again
# from flask import Blueprint, url_for
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime, timedelta

def create_app():
    app = Flask(__name__) 
    
    # This is used or required for session, flash messages, login tokens, etc.
    app.secret_key = 'my-secret-key-123'
    
    @app.route('/')
    def home():
        return render_template('home.html',hero_image='./static/uploads/one.jpg',hero_page=True)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            hashed_password = generate_password_hash(password)

            # Save to DB - remaining 
            try:
                conn = sqlite3.connect('app.db')
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                               (username, hashed_password))
                conn.commit()
                conn.close()
                flash('Registration successful!', 'success')
                return redirect('/login')
            
            except sqlite3.IntegrityError:
                flash('Username already exists!', 'danger')
                return redirect('/register')

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            # # Abhi ke liye login work ho gya hai ye pretend hai 
            # flash(f'Logged in as {username} (verification is left)', 'success')
            # return redirect('/')
            
            
            # Implement try & catch here too
            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, password, is_admin FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()

            if user:
                user_id,hashed_password,is_admin = user
                if check_password_hash(hashed_password, password):
                    session['user_id'] = user_id
                    session['username'] = username
                    session['is_admin'] = is_admin
                    flash(f'Welcome back, {username}!', 'success')
                    return redirect('/')
                else:
                    flash('Incorrect password.', 'danger')
            else:
                flash('User not found.', 'danger')
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info') 
        return redirect('/')
    
    
    # Some admin dashboard ke routes
    @app.route('/admin/dashboard', methods=['GET', 'POST'])
    def admin_dashboard():
        if not session.get('is_admin'):
            flash('Access denied. Admins only.', 'danger')
            return redirect('/')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

        if request.method == 'POST':
            location = request.form['location']
            price = request.form['price']
            address = request.form['address']
            pin = request.form['pin']
            max_spots = int(request.form['max_spots'])

         
            cursor.execute('''
                INSERT INTO parking_lots (prime_location_name, price, address, pin_code, max_spots, available_spots, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (location, price, address, pin, max_spots, max_spots, 'active'))
            lot_id = cursor.lastrowid

        
            for _ in range(max_spots):
                cursor.execute('INSERT INTO parking_spots (lot_id, status) VALUES (?, ?)', (lot_id, 'A'))

            conn.commit()
            flash('Parking lot created with spots!', 'success')

        #all parking lots with their respective status
        cursor.execute('SELECT * FROM parking_lots')
        lots = cursor.fetchall()
        conn.close()

        return render_template('admin_dashboard.html', lots=lots)
    
    @app.route('/admin/lot/<int:lot_id>/spots')
    def view_spots(lot_id):
        if not session.get('is_admin'):
            flash('Access denied.', 'danger')
            return redirect('/')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

      
        cursor.execute('SELECT * FROM parking_lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()

      
        cursor.execute('SELECT id, status FROM parking_spots WHERE lot_id = ?', (lot_id,))
        spots = cursor.fetchall()
        conn.close()

        return render_template('admin_view_spots.html', lot=lot, spots=spots)
    
    @app.route('/admin/lot/<int:lot_id>/delete', methods=['POST'])
    def delete_lot(lot_id):
        if not session.get('is_admin'):
            flash('Access denied.', 'danger')
            return redirect('/')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', (lot_id,))
        occupied_count = cursor.fetchone()[0]

        if occupied_count > 0:
            conn.close()
            flash('Cannot delete: Some spots in this lot are still occupied.', 'warning')
            return redirect('/admin/dashboard')


        cursor.execute('DELETE FROM parking_spots WHERE lot_id = ?', (lot_id,))
        cursor.execute('DELETE FROM parking_lots WHERE id = ?', (lot_id,))
        conn.commit()
        conn.close()

        flash('Parking lot and all its spots deleted.', 'success')
        return redirect('/admin/dashboard')
    
    @app.route('/admin/lot/<int:lot_id>/freeze', methods=['POST'])
    def freeze_lot(lot_id):
        if not session.get('is_admin'):
            flash('Access denied.', 'danger')
            return redirect('/')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

   
        cursor.execute('SELECT status FROM parking_lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()
        if not lot:
            flash('Parking lot not found.', 'danger')
            conn.close()
            return redirect('/admin/dashboard')

        current_status = lot[0] or 'active'
        new_status = 'frozen' if current_status == 'active' else 'active'

      
        cursor.execute('UPDATE parking_lots SET status = ? WHERE id = ?', (new_status, lot_id))
        conn.commit()
        conn.close()

        action = 'frozen' if new_status == 'frozen' else 'unfrozen'
        flash(f'Parking lot {action} successfully!', 'success')
        return redirect('/admin/dashboard')
    
    @app.route('/admin/users')
    def admin_users():
        if not session.get('is_admin'):
            flash('Access denied. Admins only.', 'danger')
            return redirect('/')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE is_admin = 0')
        users = cursor.fetchall()
        user_data = []
        for user in users:
            user_id, username = user
            cursor.execute('''
                SELECT DISTINCT l.prime_location_name
                FROM reservations r
                JOIN parking_lots l ON r.lot_id = l.id
                WHERE r.user_id = ?
            ''', (user_id,))
            lots = [row[0] for row in cursor.fetchall()]

            cursor.execute('SELECT SUM(total_cost) FROM reservations WHERE user_id = ?', (user_id,))
            total_spent = cursor.fetchone()[0] or 0
            user_data.append({
                'username': username,
                'lots': lots,
                'total_spent': total_spent
            })
        conn.close()
        return render_template('admin_users.html', users=user_data)
    
    @app.route('/admin/analytics')
    def admin_analytics():
        if not session.get('is_admin'):
            flash('Access denied. Admins only.', 'danger')
            return redirect('/')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        

        cursor.execute('''
            SELECT 
                l.id,
                l.prime_location_name,
                l.max_spots,
                COUNT(s.id) as total_spots,
                SUM(CASE WHEN s.status = 'A' THEN 1 ELSE 0 END) as available_spots,
                SUM(CASE WHEN s.status = 'O' THEN 1 ELSE 0 END) as occupied_spots,
                l.price,
                l.status
            FROM parking_lots l
            LEFT JOIN parking_spots s ON l.id = s.lot_id
            GROUP BY l.id
        ''')
        lot_stats = cursor.fetchall()
        
        #revenue data by month
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', parking_timestamp) as month,
                SUM(total_cost) as revenue
            FROM reservations
            WHERE total_cost IS NOT NULL
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        ''')
        monthly_revenue = cursor.fetchall()
        
       
        #booking trends (last 30 days)
        cursor.execute('''
            SELECT 
                DATE(parking_timestamp) as date,
                COUNT(*) as bookings
            FROM reservations
            WHERE parking_timestamp >= date('now', '-30 days')
            GROUP BY DATE(parking_timestamp)
            ORDER BY date
        ''')
        booking_trends = cursor.fetchall()
        
        #revenue by location
        cursor.execute('''
            SELECT 
                l.prime_location_name,
                SUM(r.total_cost) as revenue
            FROM reservations r
            JOIN parking_lots l ON r.lot_id = l.id
            WHERE r.total_cost IS NOT NULL
            GROUP BY l.id
            ORDER BY revenue DESC
        ''')
        revenue_by_location = cursor.fetchall()
        
       
        
        #peak hours (hour of day with most bookings)
        cursor.execute('''
            SELECT 
                strftime('%H', parking_timestamp) as hour,
                COUNT(*) as bookings
            FROM reservations
            GROUP BY strftime('%H', parking_timestamp)
            ORDER BY bookings DESC
            LIMIT 5
        ''')
        peak_hours = cursor.fetchall()
        
        #total revenue
        cursor.execute('SELECT SUM(total_cost) FROM reservations WHERE total_cost IS NOT NULL')
        total_revenue = cursor.fetchone()[0] or 0
        
        #total bookings
        cursor.execute('SELECT COUNT(*) FROM reservations')
        total_bookings = cursor.fetchone()[0] or 0
        
        # active users (last 30 days)
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) 
            FROM reservations 
            WHERE parking_timestamp >= date('now', '-30 days')
        ''')
        active_users = cursor.fetchone()[0] or 0
        
        #total spots 
        cursor.execute('SELECT COUNT(*) FROM parking_spots')
        total_spots = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return render_template('admin_analytics.html', 
                             lot_stats=lot_stats,
                             monthly_revenue=monthly_revenue,
                             
                             booking_trends=booking_trends,
                             revenue_by_location=revenue_by_location,
                             
                             peak_hours=peak_hours,
                             total_revenue=total_revenue,
                             total_bookings=total_bookings,
                             active_users=active_users,
                             total_spots=total_spots)
    
    # working api to view data in json Format 
    # @app.route('/admin/analytics/api/data')
    # # def analytics_api():
    #     if not session.get('is_admin'):
    #         return jsonify({'error': 'Access denied'}), 403

    #     conn = sqlite3.connect('app.db')
    #     cursor = conn.cursor()
        
    #     #real-time parking lot statistics
    #     cursor.execute('''
    #         SELECT 
    #             l.prime_location_name,
    #             COUNT(s.id) as total_spots,
    #             SUM(CASE WHEN s.status = 'A' THEN 1 ELSE 0 END) as available_spots,
    #             SUM(CASE WHEN s.status = 'O' THEN 1 ELSE 0 END) as occupied_spots
    #         FROM parking_lots l
    #         LEFT JOIN parking_spots s ON l.id = s.lot_id
    #         GROUP BY l.id
    #     ''')
    #     lot_stats = cursor.fetchall()
        
    #     # current revenue
    #     cursor.execute('SELECT SUM(total_cost) FROM reservations WHERE total_cost IS NOT NULL')
    #     total_revenue = cursor.fetchone()[0] or 0
        
    #     # current bookings
    #     cursor.execute('SELECT COUNT(*) FROM reservations')
    #     total_bookings = cursor.fetchone()[0] or 0
        
    #     conn.close()
        
    #     return jsonify({
    #         'lot_stats': [{
    #             'location': row[0],
    #             'total_spots': row[1],
    #             'available_spots': row[2],
    #             'occupied_spots': row[3],
    #             'occupancy_rate': round((row[3] / row[1] * 100) if row[1] > 0 else 0, 2)
    #         } for row in lot_stats],
    #         'total_revenue': total_revenue,
    #         'total_bookings': total_bookings
    #     })
    
    
    
    @app.route('/user/dashboard')
    def user_dashboard():
        if 'user_id' not in session:
            flash("Please login first", "warning")
            return redirect('/login')

        tab = request.args.get('tab', 'my_bookings')
        bookings = []
        history_bookings = []
        graph_data = {}
        monthly_expenses = []
        total_spent = 0
        if tab == 'my_bookings':
            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, l.prime_location_name, l.address, l.pin_code, r.parking_timestamp, r.leaving_timestamp, r.spot_id
                FROM reservations r
                JOIN parking_spots s ON r.spot_id = s.id
                JOIN parking_lots l ON s.lot_id = l.id
                WHERE r.user_id = ? AND s.status = 'O' AND r.leaving_timestamp > datetime('now')
                ORDER BY r.parking_timestamp DESC
            ''', (session['user_id'],))
            bookings = cursor.fetchall()
            conn.close()
        elif tab == 'history':
            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.id, l.prime_location_name, l.address, l.pin_code, r.parking_timestamp, r.leaving_timestamp, r.total_cost,
                       CASE WHEN s.status = 'O' AND r.leaving_timestamp > datetime('now') THEN 'Active' ELSE 'Released' END as status
                FROM reservations r
                JOIN parking_spots s ON r.spot_id = s.id
                JOIN parking_lots l ON s.lot_id = l.id
                WHERE r.user_id = ?
                ORDER BY r.parking_timestamp DESC
            ''', (session['user_id'],))
            history_bookings = cursor.fetchall()
            
            cursor.execute('''
                SELECT strftime('%Y-%m', parking_timestamp) as month, SUM(total_cost)
                FROM reservations
                WHERE user_id = ?
                GROUP BY month
                ORDER BY month
            ''', (session['user_id'],))
            monthly_expenses = cursor.fetchall()
         
            cursor.execute('''
                SELECT SUM(total_cost) FROM reservations WHERE user_id = ?
            ''', (session['user_id'],))
            total_spent = cursor.fetchone()[0] or 0
            conn.close()
        elif tab == 'graph':
            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT strftime('%Y-%m', parking_timestamp) as month, COUNT(*)
                FROM reservations
                WHERE user_id = ?
                GROUP BY month
                ORDER BY month
            ''', (session['user_id'],))
            graph_data = cursor.fetchall()
            conn.close()
        return render_template('user_dashboard_main.html', tab=tab, bookings=bookings, history_bookings=history_bookings, graph_data=graph_data, monthly_expenses=monthly_expenses, total_spent=total_spent)

    @app.route('/user/search', methods=['GET', 'POST'])
    def user_search():
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

        parking_lots = []
        locations = []

        if request.method == 'POST':
            location = request.form.get('location')
            pin_code = request.form.get('pin_code')
            cursor.execute('''
                SELECT 
                    l.id, l.prime_location_name, l.address, l.pin_code, l.price, 
                    COUNT(s.id) as max_spots,
                    SUM(CASE WHEN s.status = 'A' THEN 1 ELSE 0 END) as available_spots
                FROM parking_lots l
                JOIN parking_spots s ON l.id = s.lot_id
                WHERE l.prime_location_name = ? AND l.pin_code = ?
                GROUP BY l.id
            ''', (location, pin_code))
            parking_lots = cursor.fetchall()
        else:
            cursor.execute('''
                SELECT 
                    l.id, l.prime_location_name, l.address, l.pin_code, l.price, 
                    COUNT(s.id) as max_spots,
                    SUM(CASE WHEN s.status = 'A' THEN 1 ELSE 0 END) as available_spots
                FROM parking_lots l
                JOIN parking_spots s ON l.id = s.lot_id
                GROUP BY l.id
            ''')
            parking_lots = cursor.fetchall()

        cursor.execute('SELECT DISTINCT prime_location_name FROM parking_lots')
        locations = [row[0] for row in cursor.fetchall()]
        conn.close()

        return render_template('find_parking.html', lots=parking_lots, locations=locations)



    @app.route('/get_locations/<pin_code>') # 
    def get_locations(pin_code):
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT prime_location_name FROM parking_lots WHERE pin_code = ?', (pin_code,))
        locations = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({'locations': locations})
    #{'locations': ['Behru Ji', 'Udaipur']}



    @app.route('/release/<int:reservation_id>', methods=['POST'])
    def release(reservation_id):
        if not session.get('user_id'):
            flash('Login required', 'danger')
            return redirect('/login')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT spot_id, parking_timestamp, lot_id FROM reservations WHERE id = ?', (reservation_id,))
        row = cursor.fetchone()
        spot_id = row[0]
        parking_timestamp = row[1]
        lot_id = row[2]

      
        cursor.execute('SELECT price FROM parking_lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()
        price_per_hour = lot[0] if lot else 0

        
        leaving_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        
        start_time = datetime.strptime(parking_timestamp, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(leaving_time, '%Y-%m-%d %H:%M:%S')
        if end_time < start_time:
            total_cost = 0
            message = 'You released before your booking started. No charge.'
        else:
            total_hours = (end_time - start_time).total_seconds() / 3600
            total_cost = round(total_hours * price_per_hour, 2)
            message = f'Spot released. Total cost: ₹{total_cost}'

        
        cursor.execute('''
            UPDATE reservations
            SET leaving_timestamp = ?, total_cost = ?
            WHERE id = ?
        ''', (leaving_time, total_cost, reservation_id))

        # Free the spot
        cursor.execute('UPDATE parking_spots SET status = "A" WHERE id = ?', (spot_id,))
        conn.commit()
        conn.close()

        flash(message, 'info')
        return redirect('/user/dashboard')
    
    
    
    @app.route('/book', methods=['POST'])
    def book_slot():
        if 'username' not in session:
            flash('Please log in to book a slot.', 'warning')
            return redirect('/login')

        lot_id = request.form.get('lot_id')
        booking_type = request.form.get('booking_type')
        duration = request.form.get('duration')
        parking_time = request.form.get('parking_time')
        leaving_time = request.form.get('leaving_time')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

        
        cursor.execute('SELECT status FROM parking_lots WHERE id = ?', (lot_id,))
        lot_status = cursor.fetchone()
        if lot_status and lot_status[0] == 'frozen':
            flash('Parking lot is currently frozen. Cannot book a slot.', 'warning')
            conn.close()
            return redirect('/user/search')

        
        cursor.execute('SELECT id FROM parking_spots WHERE lot_id = ? AND status = "A" LIMIT 1', (lot_id,))
        spot = cursor.fetchone()
        if not spot:
            flash("No available spots in selected parking lot.", "danger")
            conn.close()
            return redirect('/user/dashboard')
        spot_id = spot[0]

      
        cursor.execute('SELECT price FROM parking_lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()
        if not lot:
            flash("Parking lot not found.", "danger")
            conn.close()
            return redirect('/user/dashboard')
        price_per_hour = lot[0]

      
        if booking_type == 'now':
            start_time = datetime.now()
            end_time = start_time + timedelta(hours=int(duration))
        else:
            start_time = datetime.fromisoformat(parking_time)
            end_time = datetime.fromisoformat(leaving_time)

        
        total_hours = (end_time - start_time).total_seconds() / 3600
        total_cost = round(total_hours * price_per_hour, 2)

       
        cursor.execute('''
            INSERT INTO reservations (spot_id, user_id, lot_id, parking_timestamp, leaving_timestamp, total_cost)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            spot_id,
            session['user_id'],
            lot_id,
            start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time.strftime('%Y-%m-%d %H:%M:%S'),
            total_cost
        ))

        
        cursor.execute('UPDATE parking_spots SET status = "O" WHERE id = ?', (spot_id,))

        conn.commit()
        conn.close()

        flash('Parking slot booked successfully!', 'success')
        return redirect('/user/dashboard')

    @app.route('/admin/lot/<int:lot_id>/edit_spots', methods=['POST'])
    def edit_spots(lot_id):
        if not session.get('is_admin'):
            flash('Access denied. Admins only.', 'danger')
            return redirect('/')

        new_max_spots = request.form.get('max_spots')
        if not new_max_spots:
            flash('Please provide the new number of spots.', 'danger')
            return redirect('/admin/dashboard')

        try:
            new_max_spots = int(new_max_spots)
            if new_max_spots <= 0:
                flash('Number of spots must be greater than 0.', 'danger')
                return redirect('/admin/dashboard')
        except ValueError:
            flash('Please enter a valid number.', 'danger')
            return redirect('/admin/dashboard')

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()

        
        cursor.execute('SELECT max_spots FROM parking_lots WHERE id = ?', (lot_id,))
        lot = cursor.fetchone()
        if not lot:
            flash('Parking lot not found.', 'danger')
            conn.close()
            return redirect('/admin/dashboard')

        current_max_spots = lot[0]

       
        cursor.execute('SELECT COUNT(*) FROM parking_spots WHERE lot_id = ? AND status = "O"', (lot_id,))
        occupied_spots = cursor.fetchone()[0]

        
        if new_max_spots < occupied_spots:
            flash(f'Cannot reduce spots to {new_max_spots}. There are currently {occupied_spots} occupied spots.', 'danger')
            conn.close()
            return redirect('/admin/dashboard')

      
        cursor.execute('UPDATE parking_lots SET max_spots = ? WHERE id = ?', (new_max_spots, lot_id))

      
        if new_max_spots > current_max_spots:
            
            spots_to_add = new_max_spots - current_max_spots
            for _ in range(spots_to_add):
                cursor.execute('INSERT INTO parking_spots (lot_id, status) VALUES (?, ?)', (lot_id, 'A'))
        elif new_max_spots < current_max_spots:
           
            spots_to_remove = current_max_spots - new_max_spots
           
            cursor.execute('''
                SELECT id FROM parking_spots 
                WHERE lot_id = ? AND status = 'A' 
                LIMIT ?
            ''', (lot_id, spots_to_remove))
            spots_to_delete = cursor.fetchall()
            
            for spot in spots_to_delete:
                cursor.execute('DELETE FROM parking_spots WHERE id = ?', (spot[0],))

        conn.commit()
        conn.close()

        flash(f'Parking lot updated successfully! New capacity: {new_max_spots} spots.', 'success')
        return redirect('/admin/dashboard')

    return app
