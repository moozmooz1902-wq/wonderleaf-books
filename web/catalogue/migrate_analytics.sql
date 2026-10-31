-- Adds the three analytics tables to a database that already has the
-- catalogue in it, without touching the catalogue.
--
-- Apply once:
--   cd web/site
--   npx wrangler d1 execute wallart --remote --file=../catalogue/migrate_analytics.sql
--
-- Every statement is IF NOT EXISTS, so running it twice is harmless. The
-- same tables are in seed.sql for a fresh database; this file exists so an
-- existing one does not have to be reseeded to gain them.

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
