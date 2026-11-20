"""All Flask routes: web pages + REST API."""
from functools import wraps

import mysql.connector
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash

from app.db import run_query
from app.validators import validate_employee

main = Blueprint("main", __name__)

DEPARTMENTS = ["Human Resources", "Engineering", "Finance", "Marketing",
               "Sales", "Operations", "IT Support"]


# ---------- Helpers ----------
def login_required(view):
    """Redirect to login page if admin is not logged in (web pages)."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


def api_login_required(view):
    """Return JSON 401 if admin is not logged in (API endpoints)."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return view(*args, **kwargs)
    return wrapped


def serialize(row):
    """Make a DB row safe for JSON (dates and decimals -> strings/numbers)."""
    return {
        **row,
        "joining_date": row["joining_date"].isoformat(),
        "salary": float(row["salary"]),
        "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
    }


def duplicate_message(err):
    msg = str(err)
    if "employee_id" in msg:
        return "This Employee ID already exists."
    if "email" in msg:
        return "This email address is already used by another employee."
    return "A record with the same unique value already exists."


# ---------- Authentication ----------
@main.route("/")
def index():
    return redirect(url_for("main.dashboard" if "admin_id" in session else "main.login"))


@main.route("/login", methods=["GET", "POST"])
def login():
    if "admin_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")

        try:
            admin = run_query("SELECT * FROM admins WHERE username = %s",
                              (username,), fetch="one")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return render_template("login.html")

        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["username"]
            flash("Welcome back, " + admin["username"] + "!", "success")
            return redirect(url_for("main.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@main.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


# ---------- Dashboard ----------
@main.route("/dashboard")
@login_required
def dashboard():
    try:
        stats = run_query(
            "SELECT COUNT(*) AS total, COUNT(DISTINCT department) AS departments, "
            "COALESCE(AVG(salary),0) AS avg_salary, COALESCE(SUM(salary),0) AS payroll "
            "FROM employees", fetch="one")
        by_department = run_query(
            "SELECT department, COUNT(*) AS count FROM employees "
            "GROUP BY department ORDER BY count DESC")
        recent = run_query(
            "SELECT * FROM employees ORDER BY joining_date DESC, id DESC LIMIT 5")
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        stats = {"total": 0, "departments": 0, "avg_salary": 0, "payroll": 0}
        by_department, recent = [], []

    max_count = max([d["count"] for d in by_department], default=1)
    return render_template("dashboard.html", stats=stats,
                           by_department=by_department, recent=recent,
                           max_count=max_count)


# ---------- Employees (web pages) ----------
@main.route("/employees")
@login_required
def employees():
    search = request.args.get("q", "").strip()
    try:
        if search:
            like = f"%{search}%"
            rows = run_query(
                "SELECT * FROM employees WHERE full_name LIKE %s OR employee_id LIKE %s "
                "ORDER BY id DESC", (like, like))
        else:
            rows = run_query("SELECT * FROM employees ORDER BY id DESC")
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        rows = []
    return render_template("employees.html", employees=rows, search=search)


@main.route("/employees/add", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        data, errors = validate_employee(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("employee_form.html", mode="add", emp=data,
                                   departments=DEPARTMENTS)
        try:
            run_query(
                "INSERT INTO employees (employee_id, full_name, email, phone, department, "
                "designation, joining_date, salary) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (data["employee_id"], data["full_name"], data["email"], data["phone"],
                 data["department"], data["designation"], data["joining_date"],
                 data["salary"]), fetch=None, commit=True)
            flash("Employee added successfully.", "success")
            return redirect(url_for("main.employees"))
        except mysql.connector.IntegrityError as err:
            flash(duplicate_message(err), "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
        return render_template("employee_form.html", mode="add", emp=data,
                               departments=DEPARTMENTS)

    return render_template("employee_form.html", mode="add", emp={},
                           departments=DEPARTMENTS)


@main.route("/employees/<int:emp_pk>/edit", methods=["GET", "POST"])
@login_required
def edit_employee(emp_pk):
    existing = run_query("SELECT * FROM employees WHERE id = %s", (emp_pk,), fetch="one")
    if not existing:
        flash("Employee not found.", "danger")
        return redirect(url_for("main.employees"))

    if request.method == "POST":
        data, errors = validate_employee(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            data["id"] = emp_pk
            return render_template("employee_form.html", mode="edit", emp=data,
                                   departments=DEPARTMENTS)
        try:
            run_query(
                "UPDATE employees SET employee_id=%s, full_name=%s, email=%s, phone=%s, "
                "department=%s, designation=%s, joining_date=%s, salary=%s WHERE id=%s",
                (data["employee_id"], data["full_name"], data["email"], data["phone"],
                 data["department"], data["designation"], data["joining_date"],
                 data["salary"], emp_pk), fetch=None, commit=True)
            flash("Employee updated successfully.", "success")
            return redirect(url_for("main.employees"))
        except mysql.connector.IntegrityError as err:
            flash(duplicate_message(err), "danger")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
        data["id"] = emp_pk
        return render_template("employee_form.html", mode="edit", emp=data,
                               departments=DEPARTMENTS)

    existing["joining_date"] = existing["joining_date"].isoformat()
    return render_template("employee_form.html", mode="edit", emp=existing,
                           departments=DEPARTMENTS)


@main.route("/employees/<int:emp_pk>/delete", methods=["POST"])
@login_required
def delete_employee(emp_pk):
    try:
        deleted = run_query("DELETE FROM employees WHERE id = %s", (emp_pk,),
                            fetch=None, commit=True)
        flash("Employee deleted." if deleted else "Employee not found.",
              "success" if deleted else "danger")
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
    return redirect(url_for("main.employees"))


# ---------- REST API ----------
@main.route("/api/employees", methods=["GET"])
@api_login_required
def api_list():
    search = request.args.get("q", "").strip()
    try:
        if search:
            like = f"%{search}%"
            rows = run_query(
                "SELECT * FROM employees WHERE full_name LIKE %s OR employee_id LIKE %s "
                "ORDER BY id DESC", (like, like))
        else:
            rows = run_query("SELECT * FROM employees ORDER BY id DESC")
        return jsonify([serialize(r) for r in rows])
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


@main.route("/api/employees/<int:emp_pk>", methods=["GET"])
@api_login_required
def api_get(emp_pk):
    row = run_query("SELECT * FROM employees WHERE id = %s", (emp_pk,), fetch="one")
    if not row:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify(serialize(row))


@main.route("/api/employees", methods=["POST"])
@api_login_required
def api_create():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Send a JSON body"}), 400
    data, errors = validate_employee(payload)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        conn_rows = run_query(
            "INSERT INTO employees (employee_id, full_name, email, phone, department, "
            "designation, joining_date, salary) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (data["employee_id"], data["full_name"], data["email"], data["phone"],
             data["department"], data["designation"], data["joining_date"],
             data["salary"]), fetch=None, commit=True)
        row = run_query("SELECT * FROM employees WHERE employee_id = %s",
                        (data["employee_id"],), fetch="one")
        return jsonify(serialize(row)), 201
    except mysql.connector.IntegrityError as err:
        return jsonify({"error": duplicate_message(err)}), 409
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


@main.route("/api/employees/<int:emp_pk>", methods=["PUT"])
@api_login_required
def api_update(emp_pk):
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"error": "Send a JSON body"}), 400
    data, errors = validate_employee(payload)
    if errors:
        return jsonify({"errors": errors}), 400
    try:
        if not run_query("SELECT id FROM employees WHERE id = %s", (emp_pk,), fetch="one"):
            return jsonify({"error": "Employee not found"}), 404
        run_query(
            "UPDATE employees SET employee_id=%s, full_name=%s, email=%s, phone=%s, "
            "department=%s, designation=%s, joining_date=%s, salary=%s WHERE id=%s",
            (data["employee_id"], data["full_name"], data["email"], data["phone"],
             data["department"], data["designation"], data["joining_date"],
             data["salary"], emp_pk), fetch=None, commit=True)
        row = run_query("SELECT * FROM employees WHERE id = %s", (emp_pk,), fetch="one")
        return jsonify(serialize(row))
    except mysql.connector.IntegrityError as err:
        return jsonify({"error": duplicate_message(err)}), 409
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500


@main.route("/api/employees/<int:emp_pk>", methods=["DELETE"])
@api_login_required
def api_delete(emp_pk):
    try:
        deleted = run_query("DELETE FROM employees WHERE id = %s", (emp_pk,),
                            fetch=None, commit=True)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    if not deleted:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify({"message": "Employee deleted"})
