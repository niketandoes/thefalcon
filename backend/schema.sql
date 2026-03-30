-- § 0  EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- § 1  ENUM TYPES
DROP TYPE IF EXISTS member_status CASCADE;
CREATE TYPE member_status AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED');

DROP TYPE IF EXISTS split_type CASCADE;
CREATE TYPE split_type AS ENUM ('EQUAL', 'PERCENTAGE', 'SHARE', 'ITEM');

DROP TYPE IF EXISTS recurring_frequency CASCADE;
CREATE TYPE recurring_frequency AS ENUM ('DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY', 'SEMI_MONTHLY');

DROP TYPE IF EXISTS notification_type CASCADE;
CREATE TYPE notification_type AS ENUM ('GROUP_INVITE', 'EXPENSE_ADDED', 'PAYMENT_RECEIVED', 'PAYMENT_REMINDER');

DROP TYPE IF EXISTS settlement_status CASCADE;
CREATE TYPE settlement_status AS ENUM ('PENDING', 'CONFIRMED', 'DISPUTED', 'CANCELLED');

-- § 2  USERS
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    email               CITEXT      NOT NULL UNIQUE,
    full_name           VARCHAR(100),
    hashed_password     CHAR(60)    NOT NULL,
    preferred_currency  CHAR(3)     NOT NULL DEFAULT 'USD',
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- § 3  GROUPS
DROP TABLE IF EXISTS groups CASCADE;
CREATE TABLE groups (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    created_by  UUID        NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- § 4  GROUP MEMBERS
DROP TABLE IF EXISTS group_members CASCADE;
CREATE TABLE group_members (
    id              UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id        UUID            NOT NULL REFERENCES groups (id) ON DELETE CASCADE,
    user_id         UUID            REFERENCES users  (id) ON DELETE CASCADE,
    status          member_status   NOT NULL DEFAULT 'ACCEPTED',
    role            VARCHAR(20)     NOT NULL DEFAULT 'member',
    invited_by      UUID            REFERENCES users (id) ON DELETE SET NULL,
    invited_email   CITEXT,
    joined_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    left_at         TIMESTAMPTZ,
    UNIQUE (group_id, user_id),
    UNIQUE (group_id, invited_email)
);

-- § 5  EXPENSES
DROP TABLE IF EXISTS expenses CASCADE;
CREATE TABLE expenses (
    id                      UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id                UUID            NOT NULL REFERENCES groups (id) ON DELETE RESTRICT,
    payer_id                UUID            REFERENCES users (id) ON DELETE RESTRICT,
    description             VARCHAR(200)    NOT NULL,
    amount                  NUMERIC(12, 2)  NOT NULL,
    currency                CHAR(3)         NOT NULL DEFAULT 'USD',
    split_type              split_type      NOT NULL,
    expense_date            DATE            NOT NULL DEFAULT CURRENT_DATE,
    is_recurring            BOOLEAN         NOT NULL DEFAULT FALSE,
    recurring_frequency     recurring_frequency,
    recurring_day_of_week   SMALLINT,
    recurring_day_of_month  SMALLINT,
    receipt_url             TEXT,
    is_deleted              BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- § 6  SPLITS
DROP TABLE IF EXISTS splits CASCADE;
CREATE TABLE splits (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    expense_id  UUID            NOT NULL REFERENCES expenses (id) ON DELETE CASCADE,
    user_id     UUID            NOT NULL REFERENCES users    (id) ON DELETE RESTRICT,
    amount_owed NUMERIC(12, 2),
    percentage  NUMERIC(7, 2),
    share       INTEGER,
    is_settled  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (expense_id, user_id)
);

-- § 7  EXPENSE_ITEMS
DROP TABLE IF EXISTS expense_items CASCADE;
CREATE TABLE expense_items (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    split_id    UUID        NOT NULL REFERENCES splits (id) ON DELETE CASCADE,
    description VARCHAR(200) NOT NULL,
    amount      NUMERIC(12, 2) NOT NULL,
    quantity    SMALLINT    NOT NULL DEFAULT 1,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- § 8  SETTLEMENTS
DROP TABLE IF EXISTS settlements CASCADE;
CREATE TABLE settlements (
    id                  UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    group_id            UUID                NOT NULL REFERENCES groups (id) ON DELETE RESTRICT,
    payer_id            UUID                NOT NULL REFERENCES users  (id) ON DELETE RESTRICT,
    payee_id            UUID                NOT NULL REFERENCES users  (id) ON DELETE RESTRICT,
    amount              NUMERIC(12, 2)      NOT NULL,
    currency            CHAR(3)             NOT NULL DEFAULT 'USD',
    status              settlement_status   NOT NULL DEFAULT 'PENDING',
    payment_reference   TEXT,
    note                TEXT,
    settled_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- § 9  NOTIFICATIONS
DROP TABLE IF EXISTS notifications CASCADE;
CREATE TABLE notifications (
    id          UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID                NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    type        notification_type   NOT NULL,
    title       VARCHAR(200)        NOT NULL,
    message     TEXT                NOT NULL,
    is_read     BOOLEAN             NOT NULL DEFAULT FALSE,
    group_id    UUID                REFERENCES groups   (id) ON DELETE SET NULL,
    expense_id  UUID                REFERENCES expenses (id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);
