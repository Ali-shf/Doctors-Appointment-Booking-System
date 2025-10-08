# 🏥 Doctors Appointment Booking System

A full-featured **Django-based web application** that allows patients to book appointments with doctors efficiently.
This project demonstrates strong use of **Django ORM**, **authentication**, **REST API design**, **Dockerization**, and **modular app architecture**.

---

## 🚀 Features

* 👨‍⚕️ **Doctor Management** – Add, edit, and view doctors’ profiles and schedules
* 🧑‍💻 **Patient Registration & Login** – Secure user authentication using Django’s built-in auth system
* 📅 **Appointment Booking System** – Book, cancel, and manage appointments
* 💳 **Wallet System** – Deposit, deduct, and view transaction history
* 📊 **Admin Dashboard** – Manage all entities from one place
* 🐳 **Docker Support** – Fully containerized with PostgreSQL and Nginx
* 🧪 **Unit Testing** – Comprehensive test coverage for models and business logic

---

## 🏗️ Project Structure

![Project Structure](staticfiles/images/project_structure.png)

```
Doctors_Appointment_Booking_System/
├── account/                  # Authentication and user management
├── reservation/              # Appointment scheduling logic
├── wallet/                   # Wallet and transaction management
├── static/                   # Static assets (CSS, JS, images)
├── templates/                # HTML templates
├── Dockerfile                # Docker build configuration
├── docker-compose.yml        # Multi-container setup (Django + PostgreSQL + Nginx)
├── manage.py                 # Django project entry point
└── requirements.txt          # Dependencies
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/Doctors-Appointment-Booking-System.git
cd Doctors-Appointment-Booking-System
```

### 2️⃣ Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Run the development server

```bash
python manage.py runserver
```

Now open: [http://localhost:8000](http://localhost:8000)

---

## 🐳 Docker Setup (Optional)

Build and start containers:

```bash
docker compose up --build
```

Access the app at:
👉 [http://localhost:8000](http://localhost:8000)

---

## 🧠 Running Tests

```bash
python manage.py test
```

Example wallet test (`wallet/tests.py`):

```python
class WalletTestCase(TestCase):
    def test_wallet_balance_change(self):
        ...
```

---

## 🧩 Tech Stack

| Layer            | Technology                    |
| :--------------- | :---------------------------- |
| Backend          | Django, Django REST Framework |
| Database         | PostgreSQL                    |
| Frontend         | HTML, TailwindCSS             |
| Containerization | Docker, Docker Compose        |
| Web Server       | Nginx                         |
| Testing          | Django TestCase               |

---

## 📸 Screenshots

> *(Add your screenshots here)*
> Example:
> ![Login Page](staticfiles/images/login.png)
> ![Dashboard](staticfiles/images/dashboard.png)

---

## 🧑‍💻 Author

**Ali Shahrabi**
📧 [your.email@example.com](ali.shahrabi.dev@gmail.com)
🌐 [GitHub Profile](https://github.com/Ali-shf)

---

## ⭐️ Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes
4. Push and create a Pull Request

---

## 🪪 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for more details.

---

✨ *Built with Django, Docker, and built by # 🏥 Doctors Appointment Booking System

A full-featured **Django-based web application** that allows patients to book appointments with doctors efficiently.
This project demonstrates strong use of **Django ORM**, **authentication**, **REST API design**, **Dockerization**, and **modular app architecture**.

---

## 🚀 Features

* 👨‍⚕️ **Doctor Management** – Add, edit, and view doctors’ profiles and schedules
* 🧑‍💻 **Patient Registration & Login** – Secure user authentication using Django’s built-in auth system
* 📅 **Appointment Booking System** – Book, cancel, and manage appointments
* 💳 **Wallet System** – Deposit, deduct, and view transaction history
* 📊 **Admin Dashboard** – Manage all entities from one place
* 🐳 **Docker Support** – Fully containerized with PostgreSQL and Nginx
* 🧪 **Unit Testing** – Comprehensive test coverage for models and business logic

---

## 🏗️ Project Structure

![Project Structure](staticfiles/images/project_structure.png)

```
Doctors_Appointment_Booking_System/
├── account/                  # Authentication and user management
├── reservation/              # Appointment scheduling logic
├── wallet/                   # Wallet and transaction management
├── static/                   # Static assets (CSS, JS, images)
├── templates/                # HTML templates
├── Dockerfile                # Docker build configuration
├── docker-compose.yml        # Multi-container setup (Django + PostgreSQL + Nginx)
├── manage.py                 # Django project entry point
└── requirements.txt          # Dependencies
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/Doctors-Appointment-Booking-System.git
cd Doctors-Appointment-Booking-System
```

### 2️⃣ Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Run the development server

```bash
python manage.py runserver
```

Now open: [http://localhost:8000](http://localhost:8000)

---

## 🐳 Docker Setup (Optional)

Build and start containers:

```bash
docker compose up --build
```

Access the app at:
👉 [http://localhost:8000](http://localhost:8000)

---

## 🧠 Running Tests

```bash
python manage.py test
```

Example wallet test (`wallet/tests.py`):

```python
class WalletTestCase(TestCase):
    def test_wallet_balance_change(self):
        ...
```

---

## 🧩 Tech Stack

| Layer            | Technology                    |
| :--------------- | :---------------------------- |
| Backend          | Django, Django REST Framework |
| Database         | PostgreSQL                    |
| Frontend         | HTML, TailwindCSS             |
| Containerization | Docker, Docker Compose        |
| Web Server       | Nginx                         |
| Testing          | Django TestCase               |

---

## 📸 Screenshots

> *(Add your screenshots here)*
> Example:
> ![Login Page](staticfiles/images/login.png)
> ![Dashboard](staticfiles/images/dashboard.png)

---

## 🧑‍💻 Author

**Ali Shahrabi**
📧 [your.email@example.com](mailto:your.email@example.com)
🌐 [GitHub Profile](https://github.com/Ali-shf)

---

## ⭐️ Contributing

Contributions are welcome!

1. Fork the repo
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes
4. Push and create a Pull Request

---

## 🪪 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for more details.

---

✨ *Built with Django, Docker, and built by ❤️ * ✨

---

## 👥 Contributors

<!-- readme: contributors -start -->

[![AmirmahdiGolahmar](https://github.com/AmirmahdiGolahmar.png?size=100)](https://github.com/AmirmahdiGolahmar)
[![foadferdows](https://github.com/foadferdows.png?size=100)](https://github.com/foadferdows)
[![devbysina](https://github.com/devbysina.png?size=100)](https://github.com/devbysina)
[![Soheylnik](https://github.com/Soheylnik.png?size=100)](https://github.com/Soheylnik)

<!-- readme: contributors -end -->
* ✨

---


