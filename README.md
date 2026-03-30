# Split It Fair

Split It Fair is a modern, AI-powered expense-sharing application designed to simplify group finances. It allows users to track shared expenses, split bills in various ways, and settle debts effortlessly.

## Features

- **Group Expense Management**: Create groups, add members, and track shared expenses.
- **Smart Expense Splitting**:
  - **Equal Split**: Divide costs equally among members.
  - **Percentage Split**: Split based on custom percentages.
  - **Share Split**: Assign specific shares to each member.
  - **Itemized Split**: Itemize purchases and assign them to specific members.
- **Recurring Expenses**: Set up automatic recurring expenses (daily, weekly, monthly, yearly, semi-monthly).
- **Notifications**: Get real-time notifications for group activities, new expenses, and payment reminders.
- **User Authentication**: Secure login and user management.
- **Multi-Currency Support**: Track expenses in different currencies.

## Tech Stack

- **Backend**: Python 3.12, FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **AI/ML**: PyTorch, Transformers (for future AI features)
- **Frontend**: React (planned)

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Docker (optional, for containerized setup)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd thefalcon
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate  # macOS/Linux
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r backend/requirements.txt
    ```

4.  **Database Setup**:
    - Ensure PostgreSQL is running.
    - Create a database named `splititfair`.
    - Run database migrations:
      ```bash
      alembic upgrade head
      ```

5.  **Run the Server**:
    ```bash
    python -m uvicorn app.main:app --reload --port 8000
    ```

The API will be available at `http://localhost:8000`.

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── api/             # API endpoints
│   ├── core/            # Configuration and settings
│   ├── db/              # Database models and session
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── utils/           # Utility functions
│   └── main.py          # Application entry point
├── alembic/             # Database migrations
├── requirements.txt     # Dependencies
└── README.md
```

## Development

### Adding Migrations

To create a new database migration:

```bash
# Generate migration
alembic revision --autogenerate -m "migration description"

# Apply migration
alembic upgrade head
```

### Running Tests

(Tests will be implemented in a future version)

## License

MIT License 