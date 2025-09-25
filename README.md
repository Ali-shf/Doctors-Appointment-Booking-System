# 🩺 Doctors Appointment Booking System

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)  
![Django](https://img.shields.io/badge/Django-5.0-green.svg)  
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)  
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)  
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A web-based appointment booking system where patients can book visits with doctors, handle payments, and manage schedules — built with **Django**, **PostgreSQL**, and **Docker**.

---

## 📌 Table of Contents

- [About](#-about)
- [Tech Stack](#-tech-stack)
- [Project Workflow](#-project-workflow)
- [Getting Started](#-getting-started)
- [Development](#-development)
- [Production](#-production)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 About

The system provides patients with an easy way to book appointments, while doctors can manage their availability and reservations.

Core features include:

- Appointment booking
- Doctor availability management
- Payment handling
- Notifications & confirmations

---

## 🛠 Tech Stack

- **Backend**: Django (Python 3.12)
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose
- **Environment Management**: `.env.dev`, `.env.prod`
- **Version Control**: Git + GitHub

---

## 🔄 Project Workflow

We follow a **Git branching strategy** for smooth collaboration:

1. **Branching**

   - `main` → production-ready code
   - `dev` → integration branch for features
   - `feat/*` → individual feature branches (e.g., `feat-auth`, `feat-wallet-v01`)

2. **Feature Development**

   - Create a branch from `dev`
   - Implement the feature
   - Commit with meaningful messages
   - Push to GitHub

3. **Pull Requests & Reviews**

   - Open PR from `feat/*` → `dev`
   - Resolve conflicts locally if needed
   - Get reviewed & merged

4. **Release to Production**
   - Merge `dev` → `main`
   - Deploy from `main`

---

## ⚙️ Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```
