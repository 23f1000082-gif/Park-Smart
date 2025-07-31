# Vehicle Parking Management System - ParkSmart

A comprehensive web-based parking management system built with Flask, featuring real-time analytics, user management, and automated billing.

## Features

### User Features
-  Secure user registration and authentication
-  Location-based parking lot search
-  Immediate and scheduled spot booking
-  Automated cost calculation
-  Personal booking analytics
-  Responsive mobile-friendly design

### Admin Features
-  Complete parking lot management (CRUD operations)
-  Real-time analytics dashboard with interactive charts
-  User management and behavior analytics
-  Dynamic spot capacity management
-  Parking lot freeze/unfreeze functionality
-  Revenue tracking and performance metrics

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd vehicle-parking-app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python schema_creation.py
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Default admin credentials: `admin` / `admin123`

## Project Structure

```
vehicle-parking-app/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── templates/           # HTML templates
│   │   ├── admin_analytics.html
│   │   ├── admin_dashboard.html
│   │   ├── admin_users.html
│   │   ├── base.html
│   │   ├── book_spot.html
│   │   ├── find_parking.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── user_dashboard_main.html
│   └── static/              # Static assets
│       ├── images/
│       ├── nav.css
│       └── ...
├── app.db                   # SQLite database
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
├── schema_creation.py     # Database initialization

```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `password`: Hashed password
- `is_admin`: Admin privileges flag

### Parking Lots Table
- `id`: Primary key
- `prime_location_name`: Location name
- `price`: Price per hour
- `address`: Physical address
- `pin_code`: Postal code
- `max_spots`: Maximum capacity
- `available_spots`: Current availability
- `status`: Active/Frozen status

### Parking Spots Table
- `id`: Primary key
- `lot_id`: Foreign key to parking_lots
- `status`: Available (A) / Occupied (O)

### Reservations Table
- `id`: Primary key
- `spot_id`: Foreign key to parking_spots
- `user_id`: Foreign key to users
- `lot_id`: Foreign key to parking_lots
- `parking_timestamp`: Booking start time
- `leaving_timestamp`: Booking end time
- `total_cost`: Calculated cost

## Usage Guide

### For Users

1. **Registration/Login**
   - Visit `/register` to create an account
   - Use `/login` to access your account

2. **Find Parking**
   - Go to "Find Parking" in the navigation
   - Search by location and pin code
   - View real-time availability

3. **Book a Spot**
   - Select a parking lot
   - Choose booking type (immediate/scheduled)
   - Confirm booking details

4. **Manage Bookings**
   - Access "My Bookings" from dashboard
   - View active bookings and history
   - Release spots when done

### For Administrators

1. **Access Admin Panel**
   - Login with admin credentials
   - Navigate to "List your space" for lot management
   - Use "Analytics" for performance insights

2. **Manage Parking Lots**
   - Create new parking lots with specified capacity
   - Edit spot counts dynamically
   - Freeze/unfreeze lots as needed

3. **View Analytics**
   - Real-time revenue tracking
   - Occupancy rate analysis
   - User behavior insights
   - Peak hour identification

## Testing


### Test Scenarios

1. **User Registration Flow**
   - Register new user
   - Login with credentials
   - Verify dashboard access

2. **Parking Booking Flow**
   - Search for parking lots
   - Book a spot
   - Verify booking appears in dashboard
   - Release the spot

3. **Admin Management Flow**
   - Create new parking lot
   - Add/edit spots
   - View analytics dashboard
   - Test freeze/unfreeze functionality

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /logout` - Session termination

### User Operations
- `GET /user/dashboard` - User dashboard
- `GET /user/search` - Parking search
- `POST /book` - Spot booking
- `POST /release/<id>` - Spot release

### Admin Operations
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/analytics` - Analytics dashboard
<!-- - `GET /admin/analytics/api/data` - Real-time data API -->
- `POST /admin/lot/<id>/spots` - Spot management
- `POST /admin/lot/<id>/delete` - Lot deletion
- `POST /admin/lot/<id>/freeze` - Status management

## Configuration


### Database Configuration
- SQLite database file: `app.db`
- Auto-created on first run
- Backup recommended for production

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Input validation and sanitization
- Admin-only access controls


