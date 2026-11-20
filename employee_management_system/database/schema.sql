-- Employee Management System - database creation script
CREATE DATABASE IF NOT EXISTS employee_management
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE employee_management;

-- Administrators (passwords are stored as hashes, never plain text)
CREATE TABLE IF NOT EXISTS admins (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    employee_id  VARCHAR(20)   NOT NULL UNIQUE,
    full_name    VARCHAR(100)  NOT NULL,
    email        VARCHAR(120)  NOT NULL UNIQUE,
    phone        VARCHAR(20)   NOT NULL,
    department   VARCHAR(60)   NOT NULL,
    designation  VARCHAR(80)   NOT NULL,
    joining_date DATE          NOT NULL,
    salary       DECIMAL(10,2) NOT NULL CHECK (salary >= 0),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_full_name (full_name),
    INDEX idx_department (department)
) ENGINE=InnoDB;
