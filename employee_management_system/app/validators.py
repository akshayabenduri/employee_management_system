"""Input validation for employee data."""
import re
from datetime import datetime

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^\+?[0-9]{7,15}$")
EMP_ID_RE = re.compile(r"^[A-Za-z0-9-]{2,20}$")


def validate_employee(data):
    """Return (cleaned_data, errors). errors is a list of messages."""
    errors = []
    cleaned = {
        "employee_id": str(data.get("employee_id", "")).strip(),
        "full_name": str(data.get("full_name", "")).strip(),
        "email": str(data.get("email", "")).strip().lower(),
        "phone": str(data.get("phone", "")).strip().replace(" ", ""),
        "department": str(data.get("department", "")).strip(),
        "designation": str(data.get("designation", "")).strip(),
        "joining_date": str(data.get("joining_date", "")).strip(),
        "salary": str(data.get("salary", "")).strip(),
    }

    if not EMP_ID_RE.match(cleaned["employee_id"]):
        errors.append("Employee ID must be 2-20 characters (letters, numbers, hyphen).")
    if len(cleaned["full_name"]) < 2 or len(cleaned["full_name"]) > 100:
        errors.append("Full name must be between 2 and 100 characters.")
    if not EMAIL_RE.match(cleaned["email"]):
        errors.append("Please enter a valid email address.")
    if not PHONE_RE.match(cleaned["phone"]):
        errors.append("Phone number must have 7-15 digits (optional + at the start).")
    if not cleaned["department"]:
        errors.append("Department is required.")
    if not cleaned["designation"]:
        errors.append("Designation is required.")

    try:
        datetime.strptime(cleaned["joining_date"], "%Y-%m-%d")
    except ValueError:
        errors.append("Joining date must be a valid date (YYYY-MM-DD).")

    try:
        salary = float(cleaned["salary"])
        if salary < 0 or salary > 99999999:
            raise ValueError
        cleaned["salary"] = round(salary, 2)
    except ValueError:
        errors.append("Salary must be a positive number.")

    return cleaned, errors
