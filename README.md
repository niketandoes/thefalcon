# 🦅 Split It Fair

Split It Fair is a modern, full-stack expense-sharing application designed to simplify group finances. It allows users to track shared expenses, split bills in various ways, and settle debts effortlessly—functioning as an advanced, privacy-first alternative to apps like Splitwise.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)
![React](https://img.shields.io/badge/React-18-61DAFB.svg)

## ✨ Features

- **Robust Authentication**: Secure login and user management featuring Argon2 password hashing and JWT-based session handling.
- **Group Management**: Create customized groups, invite peers via email, and securely track all group-oriented expenses.
- **Smart Expense Splitting**:
  - **Equal Split**: Divide parameters automatically among active members.
  - **Custom Splitting Engines** *(Percentage, Share, Itemized)* to handle complex real-world receipts.
- **Architectural Excellence**: Asynchronous database drivers (`asyncpg`) mapped via SQLAlchemy 2.0 ensuring high performance.
- **Modern UI**: Polished, responsive frontend interface powered by React, Vite, and Zustand for frictionless state management.

---

## 🛠️ Tech Stack

### Frontend (User Interface)
- **Framework**: [React 18](https://react.dev/) with [TypeScript](https://www.typescriptlang.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand)
- **Styling**: Tailwind CSS / Vanilla CSS framework
- **HTTP Client**: Axios (configured with interceptors for JWT)
- **Deployment**: [Vercel](https://vercel.com/)

### Backend (API Server)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Database**: PostgreSQL 13+ (Cloud-hosted via Render/Neon)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) & Asyncpg
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Security**: Passlib (Argon2), python-jose (JWT)
- **Deployment**: [Render](https://render.com/)

---

## 📁 Project Structure

```text
thefalcon/
├── backend/                  # Python FastAPI application
│   ├── alembic/              # Database migration config & scripts
│   ├── app/                  # Core application source code
│   │   ├── api/v1/           # API Routers & Endpoints
│   │   ├── core/             # Settings, Security, and Config
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   └── schemas/          # Pydantic validation schemas
│   ├── requirements.txt      # Python dependencies
│   └── schema.sql            # Raw SQL ground-truth schema
└── frontend/                 # React SPA
    ├── src/
    │   ├── api/              # Axios client and remote fetchers
    │   ├── components/       # Reusable UI widgets
    │   ├── pages/            # View components (Login, Dashboard)
    │   └── store/            # Zustand state containers
    ├── package.json          # Node dependencies
    └── vite.config.ts        # Vite configuration
```

---

## 🚀 Getting Started (Local Development)

### 1. Prerequisites
- Python `3.12+`
- Node.js `18+`
- A local PostgreSQL database instance running.

### 2. Database Preparation
Create a local Postgres database:
```bash
createdb splititfair
```

### 3. Backend Setup
Navigate into the backend directory, construct your virtual environment, and install the required dependencies:
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Configure Backend Environment**  
Create a `.env` file in the `backend/` directory:
```env
# backend/.env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=split_it_fair
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your_super_secret_jwt_key
```

**Run Migrations & Start Server**
```bash
# Push schema to the database
alembic upgrade head

# Launch the FastAPI development server
python -m uvicorn app.main:app --reload --port 8000
```
*The interactive API documentation is now available at `http://localhost:8000/docs`.*

---

### 4. Frontend Setup
Open a new terminal window and navigate to the frontend directory:
```bash
cd frontend
npm install
```

**Configure Frontend Environment**  
Create a `.env` file in the `frontend/` directory connecting to your local API:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

**Launch the Client**
```bash
npm run dev
```
*The app is now running at `http://localhost:5173`.*

---

## ☁️ Deployment Guidelines

Because this app utilizes isolated instances for its frontend and backend, specific environment variables map them together. 

### Backend (Render / Heroku)
When deploying the FastAPI backend to a service like Render:
1. Set the Build Command to `pip install -r backend/requirements.txt`
2. Set the Start Command to `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add the `DATABASE_URL` environment variable containing your production PostgreSQL connection string. 
4. *Important:* Run your production migrations manually via the cloud console shell: `alembic upgrade head`.

### Frontend (Vercel / Netlify)
When deploying the Vite Frontend to Vercel:
1. Ensure the Framework Preset is set to **Vite**.
2. Go to Environment Variables and add `VITE_API_URL` pointing strictly to your deployed backend (e.g., `https://your-backend-api.onrender.com/api/v1`).
3. Deploy!

---

## 🔒 License
This project is licensed under the MIT License. See the LICENSE file for details.