# Backend Implementation Walkthrough

## Summary

Complete FastAPI backend implementation for the **Split It Fair** expense-splitting application.
All 7 feature areas are fully wired: Auth, Groups (with invite flow), Notifications, Expenses (with algorithm-backed splits), Dashboard Stats, Debt Simplification, and Multi-Currency placeholder.

---

## File Structure (Final)

```
backend/
├── .env                              # DB credentials (unchanged)
├── .env.example                      # Template (unchanged)
├── requirements.txt                  # Updated: +pydantic[email], +httpx, +python-dotenv
├── alembic.ini                       # Unchanged
├── alembic/                          # Unchanged
└── app/
    ├── __init__.py
    ├── main.py                       # Unchanged — FastAPI app, CORS, health check
    ├── database.py                   # Unchanged — raw psycopg2 helper
    ├── core/
    │   ├── config.py                 # Unchanged — Settings from .env
    │   └── algorithms/
    │       ├── __init__.py           # Unchanged — re-exports
    │       ├── expense_splitter.py   # Unchanged — 4 split methods + Hamilton rounding
    │       └── debt_simplifier.py    # Unchanged — heap-based edge minimization
    ├── db/
    │   ├── base.py                   # Unchanged — SQLAlchemy Base
    │   └── session.py                # Unchanged — async engine + sessionmaker
    ├── models/
    │   ├── __init__.py               # UPDATED — registers Notification, MemberStatus
    │   ├── user.py                   # UPDATED — added notifications relationship
    │   ├── group.py                  # Unchanged
    │   ├── group_member.py           # UPDATED — added MemberStatus enum + status column
    │   ├── expense.py                # Unchanged
    │   ├── split.py                  # Unchanged
    │   └── notification.py           # NEW — Notification model
    ├── schemas/
    │   ├── __init__.py               # UPDATED — registers new exports
    │   ├── user.py                   # Unchanged
    │   ├── group.py                  # UPDATED — GroupMemberDetailResponse w/ status
    │   ├── expense.py                # Unchanged
    │   └── notification.py           # NEW — notification response + invite action schemas
    ├── services/
    │   ├── __init__.py               # Unchanged
    │   ├── currency_service.py       # NEW — Forex API placeholder
    │   └── notification_service.py   # NEW — centralised notification factory
    └── api/
        ├── __init__.py               # Unchanged
        ├── deps.py                   # Unchanged — get_db, get_current_user (JWT)
        └── v1/
            ├── api.py                # UPDATED — added notifications router
            └── endpoints/
                ├── auth.py           # IMPLEMENTED — login + register
                ├── users.py          # IMPLEMENTED — CRUD /me
                ├── groups.py         # IMPLEMENTED — CRUD + invite + leave + balances
                ├── expenses.py       # IMPLEMENTED — create + list + detail + stats
                └── notifications.py  # NEW — list + read + invite respond
```

---

## API Endpoint Map

### Authentication
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/login/access-token` | OAuth2 password login → JWT |
| `POST` | `/api/v1/register` | Create new user account |

### Users
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/users/` | Create user (internal) |
| `GET` | `/api/v1/users/me` | Get current user profile |
| `PUT` | `/api/v1/users/me` | Update current user profile |

### Groups
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/groups/` | Create a new group |
| `GET` | `/api/v1/groups/` | List user's groups |
| `GET` | `/api/v1/groups/{group_id}` | Group detail + members |
| `POST` | `/api/v1/groups/{group_id}/invite` | **NEW** Invite member (pending state) |
| `POST` | `/api/v1/groups/{group_id}/members` | Add member directly (legacy) |
| `DELETE` | `/api/v1/groups/{group_id}/leave` | Leave group (zero-balance guard) |
| `GET` | `/api/v1/groups/{group_id}/balances` | Simplified debt transactions |

### Expenses
| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/expenses/` | Log a new expense |
| `GET` | `/api/v1/expenses/` | List expenses (?group_id= filter) |
| `GET` | `/api/v1/expenses/{expense_id}` | Expense detail |
| `GET` | `/api/v1/expenses/dashboard/stats` | Global dashboard stats |
| `GET` | `/api/v1/expenses/dashboard/stats/group/{group_id}` | Per-group stats |

### Notifications (NEW)
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/notifications/` | List notifications (paginated) |
| `PATCH` | `/api/v1/notifications/{id}/read` | Mark notification read |
| `POST` | `/api/v1/notifications/invites/{group_id}/respond` | Accept/reject invite |

---

## What Was Preserved

- ✅ `expense_splitter.py` — All 4 split methods + Hamilton penny-correction (646 lines, untouched)
- ✅ `debt_simplifier.py` — Heap-based directed-graph edge minimization (90 lines, untouched)
- ✅ `config.py` — Settings with DB credentials from `.env`
- ✅ `.env` — DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- ✅ `main.py` — CORS origins, health check endpoint
- ✅ All existing ORM models (User, Group, Expense, Split) — extended, not replaced
- ✅ All existing Pydantic schemas — extended, not replaced

---

## What Was Added

### Models
- **`Notification`** — notifications table with `id`, `user_id`, `type`, `title`, `message`, `is_read`, `group_id`, `expense_id`, `created_at`
- **`MemberStatus`** enum on `GroupMember` — `PENDING`, `ACCEPTED`, `REJECTED`

### Services
- **`notification_service.py`** — `create_notification()`, `notify_group_invite()`, `notify_expense_tagged()`
- **`currency_service.py`** — `convert_currency()` with rate_override support, `get_supported_currencies()`, stub `_fetch_rate()`

### Endpoints
- All 5 endpoint files fully implemented with real DB logic
- New `notifications.py` endpoint file

---

## Algorithms Integration

The `create_expense` endpoint wires directly into the existing algorithms:

```
SplitType.EQUAL      → calculate_debt_distribution(SplitMethod.EQUAL, ...)
SplitType.PERCENTAGE → calculate_debt_distribution(SplitMethod.PERCENTAGE, ...)
SplitType.SHARE      → calculate_debt_distribution(SplitMethod.SHARES, ...)
SplitType.ITEM       → calculate_debt_distribution(SplitMethod.EXACT, ...)
```

The `get_group_balances` endpoint feeds net-balance maps into `simplify_debts()` from `debt_simplifier.py`.

---

## Verification

- All imports are resolvable within the existing project structure
- No circular dependencies introduced
- AsyncSession used consistently throughout
- JWT auth flows through existing `deps.get_current_user`

---

# 📋 DEFINITIVE PAYLOAD DICTIONARY

> **This is the canonical reference for every field sent to the server.**
> Use this to generate your database schema with zero mismatches.

---

## 1. `POST /register` — UserCreate

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `email` | `string (EmailStr)` | ✅ | — | Valid email format | User's email address (unique, used as login username) |
| `full_name` | `string \| null` | ❌ | `null` | — | User's display name |
| `preferred_currency` | `string` | ❌ | `"USD"` | Exactly 3 chars (ISO 4217) | Default currency for display/conversion |
| `is_active` | `boolean` | ❌ | `true` | — | Account active flag |
| `password` | `string` | ✅ | — | min_length=8 | Plaintext password (hashed server-side via bcrypt) |

---

## 2. `POST /login/access-token` — OAuth2PasswordRequestForm

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | `string` | ✅ | The user's **email** (OAuth2 spec requires this field name) |
| `password` | `string` | ✅ | Plaintext password |

> Sent as `application/x-www-form-urlencoded`, not JSON.

---

## 3. `PUT /users/me` — UserUpdate

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `full_name` | `string \| null` | ❌ | `null` | — | New display name |
| `preferred_currency` | `string \| null` | ❌ | `null` | 3 chars if provided | New default currency |
| `password` | `string \| null` | ❌ | `null` | — | New password (re-hashed) |

---

## 4. `POST /groups/` — GroupCreate

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | ✅ | — | Group display name |
| `description` | `string \| null` | ❌ | `null` | Optional group description |

---

## 5. `POST /groups/{group_id}/invite` — InviteMemberPayload

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | `string` | ✅ | Email of the registered user to invite |

---

## 6. `POST /groups/{group_id}/members` — AddMemberPayload

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | `string` | ✅ | Email of the user to add directly (legacy) |

---

## 7. `POST /expenses/` — ExpenseCreate

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `description` | `string` | ✅ | — | 1–200 chars | Expense title/description |
| `amount` | `decimal` | ✅ | — | > 0, max 10 digits, 2 d.p. | Total expense amount |
| `currency` | `string` | ❌ | `"USD"` | Exactly 3 chars | ISO 4217 currency code |
| `split_type` | `enum string` | ✅ | — | `"EQUAL"` \| `"PERCENTAGE"` \| `"SHARE"` \| `"ITEM"` | How the expense is divided |
| `group_id` | `UUID` | ✅ | — | Valid group UUID | The group this expense belongs to |
| `expense_date` | `date (YYYY-MM-DD)` | ❌ | today | — | When the expense occurred |
| `payer_id` | `UUID \| null` | ❌ | authenticated user | Valid user UUID in the group | Who paid for the expense |
| `splits` | `array[SplitCreate]` | ✅ | — | ≥ 1 item | Per-user split details (see below) |
| `is_recurring` | `boolean` | ❌ | `false` | — | Whether this expense repeats |
| `recurring_frequency` | `enum string \| null` | ❌ | `null` | `"DAILY"` \| `"WEEKLY"` \| `"MONTHLY"` \| `"YEARLY"` \| `"SEMI_MONTHLY"` | Recurrence interval |
| `recurring_day_of_week` | `int \| null` | ❌ | `null` | 0–6 (0=Sunday) | For WEEKLY recurrence |
| `recurring_day_of_month` | `int \| null` | ❌ | `null` | 1–31 | For MONTHLY recurrence |

### SplitCreate (nested in `splits` array)

| Field | Type | Required | Default | Constraints | Description |
|-------|------|----------|---------|-------------|-------------|
| `user_id` | `UUID` | ✅ | — | Valid user UUID | Who this split applies to |
| `percentage` | `decimal \| null` | ❌ | `null` | Max 5 digits, 2 d.p. (e.g. `50.00`) | Used when split_type=PERCENTAGE |
| `share` | `int \| null` | ❌ | `null` | ≥ 1 | Used when split_type=SHARE |
| `amount_owed` | `decimal \| null` | ❌ | `null` | Max 10 digits, 2 d.p. | Used when split_type=ITEM |

> **Note:** For `EQUAL` splits, only `user_id` is required. For other types, supply the matching field. The server ignores fields that don't match the `split_type`.

---

## 8. `POST /notifications/invites/{group_id}/respond` — InviteActionRequest

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `action` | `string` | ✅ | `"accept"` \| `"reject"` | Whether to accept or reject the group invite |

---

## 9. Query Parameters

### `GET /expenses/?group_id=`

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `group_id` | `UUID` | ❌ | Filter expenses to a specific group. Omit for global list. |

### `GET /notifications/?skip=&limit=&unread_only=`

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `skip` | `int` | ❌ | `0` | Pagination offset |
| `limit` | `int` | ❌ | `50` | Page size (max 100) |
| `unread_only` | `bool` | ❌ | `false` | Filter to unread notifications only |

---

## Database Table ↔ Payload Mapping

| DB Table | PK Type | Key Columns |
|----------|---------|-------------|
| `users` | `UUID` | id, email, hashed_password, full_name, preferred_currency, is_active |
| `groups` | `UUID` | id, name, description, created_at |
| `group_members` | `(user_id, group_id)` | status (PENDING/ACCEPTED/REJECTED), joined_at |
| `expenses` | `UUID` | id, group_id, payer_id, amount, currency, description, split_type, expense_date, is_recurring, recurring_frequency, recurring_day_of_week, recurring_day_of_month, created_at |
| `splits` | `UUID` | id, expense_id, user_id, amount_owed, percentage, share |
| `notifications` | `UUID` | id, user_id, type, title, message, is_read, group_id, expense_id, created_at |

---

## Enum Values Reference

| Enum | Values | Used In |
|------|--------|---------|
| `SplitType` | `EQUAL`, `PERCENTAGE`, `SHARE`, `ITEM` | expenses.split_type |
| `RecurringFrequency` | `DAILY`, `WEEKLY`, `MONTHLY`, `YEARLY`, `SEMI_MONTHLY` | expenses.recurring_frequency |
| `MemberStatus` | `PENDING`, `ACCEPTED`, `REJECTED` | group_members.status |
| `NotificationType` | `GROUP_INVITE`, `EXPENSE_ADDED`, `PAYMENT_RECEIVED`, `PAYMENT_REMINDER` | notifications.type |
