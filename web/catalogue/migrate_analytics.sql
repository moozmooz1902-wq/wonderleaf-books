-- Adds the back-office tables to a database that already has the catalogue
-- in it, without touching the catalogue.
--
-- Apply once (and again after any change here - every statement is
-- IF NOT EXISTS, so running it twice is harmless):
--   cd web/site
--   npx wrangler d1 execute wallart --remote --file=../catalogue/migrate_analytics.sql
--
-- The same tables are in seed.sql for a fresh database; this file exists so
-- an existing one does not have to be reseeded to gain them.

CREATE TABLE IF NOT EXISTS hits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  day TEXT NOT NULL,
  visitor TEXT NOT NULL,   -- salted daily hash. No IP is stored anywhere.
  path TEXT NOT NULL,
  ref TEXT,
  src TEXT,                -- google-shopping | google-search | direct | host
  country TEXT
);
CREATE INDEX IF NOT EXISTS idx_hits_ts ON hits(ts);
CREATE INDEX IF NOT EXISTS idx_hits_day ON hits(day);

CREATE TABLE IF NOT EXISTS crawls (
  day TEXT NOT NULL,
  bot TEXT NOT NULL,
  kind TEXT NOT NULL,
  n INTEGER NOT NULL,
  PRIMARY KEY (day, bot, kind)
);

-- One row each time a basket reaches Stripe. Orders divided by checkouts is
-- the conversion rate, and a checkout with no matching order is an
-- abandoned basket - the number that says whether the problem is traffic or
-- the shop.
CREATE TABLE IF NOT EXISTS checkouts (
  id TEXT PRIMARY KEY,
  ts INTEGER NOT NULL,
  day TEXT NOT NULL,
  total REAL NOT NULL,
  items INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_checkouts_ts ON checkouts(ts);

-- PHONES THAT HAVE ASKED TO BE TOLD ABOUT ORDERS.
--
-- One row per installed copy of the back office. `endpoint` is the push
-- service's URL for that device and is the primary key, because that is
-- what identifies a subscription - reinstalling the app produces a new one
-- and the old row is deleted the first time the push service rejects it.
--
-- No payload is ever encrypted into a push: the notification is empty and
-- the phone fetches the detail itself. That is why p256dh and auth are
-- stored but unused today - they are what a payload WOULD be encrypted
-- with, and a subscription without them cannot be upgraded later.
CREATE TABLE IF NOT EXISTS push_subs (
  endpoint TEXT PRIMARY KEY,
  p256dh TEXT,
  auth TEXT,
  created TEXT NOT NULL,
  last_ok TEXT,
  fails INTEGER NOT NULL DEFAULT 0
);
