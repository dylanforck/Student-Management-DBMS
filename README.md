# Student-Management-DBMS
Student Management DBMS

A simple Flask + MySQL web application for managing student records, with role‑based access control (Admin vs. User).

## Table of Contents

1. [Features](#features)  
2. [Requirements](#requirements)  
3. [Setup & Local Development](#setup--local-development)  
4. [Environment Variables](#environment-variables)  
5. [Running the App](#running-the-app)  
6. [Deployment](#deployment)  
7. [Test Accounts](#test-accounts)  
8. [Project Structure](#project-structure)  
9. [License](#license)

## Features

- User registration & login with MD5‑hashed passwords  
- Role‑based access:  
  - **Admin** can add, edit, delete students  
  - **User** can view students and query scores  
- Student CRUD (Create, Read, Update, Delete)  
- Query student scores across courses  
- Configurable via environment variables for easy local/remote deployment  

## Requirements

- **Python**: 3.8+  
- **pip** (Python package manager)  
- **MySQL** server (Railway‑hosted or local)  

Python packages (install via `requirements.txt`):

```bash
flask
mysql-connector-python
