

CREATE TABLE IF NOT EXISTS vendor (
    id          SERIAL PRIMARY KEY,
    name        TEXT        NOT NULL,
    country     TEXT        NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS shop (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    address TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS roll (
    id                     SERIAL PRIMARY KEY,
    vendor_id              INTEGER NOT NULL REFERENCES vendor(id),
    collection             TEXT NOT NULL,
    height                 DOUBLE PRECISION NOT NULL,
    width                  DOUBLE PRECISION NOT NULL,
    weight                 DOUBLE PRECISION NOT NULL,
    article                TEXT NOT NULL,
    base                   TEXT NOT NULL,
    cover                  TEXT NOT NULL,
    rapor                  INTEGER,
    pattern                TEXT,
    moisture_resistance    TEXT,
    production_technology  TEXT,
    light_fastness         TEXT,
    glue_application       TEXT
);

CREATE TABLE IF NOT EXISTS asset (
    id      SERIAL PRIMARY KEY,
    roll_id INTEGER NOT NULL REFERENCES roll(id) ON DELETE CASCADE,
    url     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS fact (
    id        SERIAL PRIMARY KEY,
    roll_id   INTEGER NOT NULL REFERENCES roll(id),
    shop_id   INTEGER NOT NULL REFERENCES shop(id),
    price     NUMERIC(12,2) NOT NULL,
    available INTEGER NOT NULL
);