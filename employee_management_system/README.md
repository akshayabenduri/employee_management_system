# Employee Management System

A web-based portal where an administrator can log in and manage employee records (add, view, search, update, delete) through a clean dashboard.

## Technologies
- **Backend:** Python 3, Flask
- **Database:** MySQL (`mysql-connector-python`)
- **Frontend:** HTML, CSS, Bootstrap 5
- **Tools:** Git, GitHub, Visual Studio Code

## Features
- Admin login/logout with **hashed passwords** (Werkzeug)
- Dashboard: total employees, departments, average salary, payroll, employees by department, recent joiners
- Add, view, edit and delete employees (delete asks for confirmation)
- Search by employee name or ID
- Input validation and friendly error messages
- Parameterized SQL queries (protects against SQL injection)
- REST API endpoints (JSON)
- Database constraints (primary key, unique, not null, check) and indexes

## Screenshots
| Login | Dashboard |
|---|---|
| ![Login](screenshots/login.png) | ![Dashboard](screenshots/dashboard.png) |

| Employees | Add Employee |
|---|---|
| ![Employees](screenshots/employees.png) | ![Add](screenshots/add-employee.png) |

## Project Structure
```
employee_management_system/
├── run.py                 # Starts the Flask app
├── config.py              # Reads settings from .env
├── create_admin.py        # Creates admin user with hashed password
├── requirements.txt       # Python dependencies
├── .env.example           # Template for your .env file
├── app/
│   ├── routes.py          # All pages and API endpoints
│   ├── db.py              # MySQL connection + safe query helper
│   ├── validators.py      # Input validation
│   ├── templates/         # HTML pages (Jinja2)
│   └── static/            # CSS and JavaScript
├── database/
│   ├── schema.sql         # Creates database and tables
│   └── sample_data.sql    # Optional test employees
└── screenshots/
```

## Setup Instructions
1. **Install** Python 3.9+, MySQL Server and VS Code.
2. **Create a virtual environment** (in the VS Code terminal):
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac/Linux
   ```
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Create the database:** run `database/schema.sql` in MySQL Workbench, or
   `mysql -u root -p < database/schema.sql`
   (Optional sample data: `mysql -u root -p < database/sample_data.sql`)
5. **Configure:** copy `.env.example` to `.env` and enter your MySQL password.
6. **Create the admin account:** `python create_admin.py`
7. **Run:** `python run.py` and open http://127.0.0.1:5000

## API Endpoints
All endpoints require an active admin session (log in first). They return JSON.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/employees` | List all employees (`?q=` to search) |
| GET | `/api/employees/<id>` | Get one employee |
| POST | `/api/employees` | Create employee (JSON body) |
| PUT | `/api/employees/<id>` | Update employee (JSON body) |
| DELETE | `/api/employees/<id>` | Delete employee |

Example body:
```json
{"employee_id":"EMP010","full_name":"Asha Rao","email":"asha@example.com",
 "phone":"9876543210","department":"Finance","designation":"Analyst",
 "joining_date":"2024-05-01","salary":50000}
```

## Possible Future Improvements
CSRF protection, pagination, role-based access, CSV export, unit tests.
