// Catalogue queries. The only place the site reads product data.
//
// Every value returned here was written by product.build_all() and nothing
// is recomputed on the way out - in particular no price is derived, summed
// or rounded in the site. The feed reads the same rows from the same build,
// which is what makes a feed/page disagreement structurally impossible
// rather than merely unlikely.

export interface Variant {
  id: string;
  slug: string;
  frame: string;
  frame_label: string;
  size: string;
  size_label: string;
  size_cm: string;
  price: number;
  title: string;
  image_path: string;
  availability: string;
}

export interface Product {
  slug: string;
  sku: string;
  item_group_id: string;
  title: string;
  description: string;
  section: string;
  section_title: string;
  niche: string;
  niche_title: string;
  style: string;
  style_title: string;
  colour: string;
  colour_title: string;
  subject: string;
  product_type: string;
  brand: string;
  mpn: string;
  bucket: string;
  price_from: number;
  default_frame: string;
  default_size: string;
  rank: number;
}

export type DB = D1Database;

export const getDb = (locals: any): DB => {
  const db = locals?.runtime?.env?.DB;
  if (!db)
    throw new Error(
      'No D1 binding. Run `wrangler d1 create wallart`, put the id in ' +
        'wrangler.toml, then `npm run db:seed:local`.'
    );
  return db;
};

export async function product(db: DB, slug: string) {
  const p = await db
    .prepare('SELECT * FROM products WHERE slug = ?')
    .bind(slug)
    .first<Product>();
  if (!p) return null;
  const { results } = await db
    .prepare(
      'SELECT * FROM variants WHERE slug = ? ' +
        "ORDER BY CASE frame WHEN 'black' THEN 0 WHEN 'white' THEN 1 ELSE 2 END, price"
    )
    .bind(slug)
    .all<Variant>();
  return { ...p, variants: results };
}

/** Resolve ?frame=&size= to one variant. Mirrors product.variant_of(). */
export function variantOf(
  p: { variants: Variant[]; default_frame: string; default_size: string },
  frame?: string | null,
  size?: string | null
) {
  const f = frame || p.default_frame;
  const s = size || p.default_size;
  return (
    p.variants.find((v) => v.frame === f && v.size === s) ??
    p.variants.find(
      (v) => v.frame === p.default_frame && v.size === p.default_size
    ) ??
    p.variants[0]
  );
}

const LIST =
  'SELECT p.*, (SELECT image_path FROM variants v WHERE v.slug = p.slug ' +
  "AND v.frame = p.default_frame AND v.size = p.default_size) AS image_path " +
  'FROM products p';

export type Card = Product & { image_path: string };

export const byNiche = (db: DB, n: string, limit = 60, offset = 0) =>
  db
    .prepare(`${LIST} WHERE p.niche = ? ORDER BY p.rank LIMIT ? OFFSET ?`)
    .bind(n, limit, offset)
    .all<Card>();

export const bySection = (db: DB, s: string, limit = 60, offset = 0) =>
  db
    .prepare(`${LIST} WHERE p.section = ? ORDER BY p.rank LIMIT ? OFFSET ?`)
    .bind(s, limit, offset)
    .all<Card>();

export const byStyle = (db: DB, s: string, limit = 60, offset = 0) =>
  db
    .prepare(`${LIST} WHERE p.style = ? ORDER BY p.rank LIMIT ? OFFSET ?`)
    .bind(s, limit, offset)
    .all<Card>();

export const byColour = (db: DB, c: string, limit = 60, offset = 0) =>
  db
    .prepare(`${LIST} WHERE p.colour = ? ORDER BY p.rank LIMIT ? OFFSET ?`)
    .bind(c, limit, offset)
    .all<Card>();

export const byRoom = (db: DB, room: string, limit = 60, offset = 0) =>
  db
    .prepare(
      `${LIST} JOIN product_rooms r ON r.slug = p.slug WHERE r.room = ? ` +
        'ORDER BY p.rank LIMIT ? OFFSET ?'
    )
    .bind(room, limit, offset)
    .all<Card>();

/**
 * Facet counts come from the precomputed `facet_counts` table, never from a
 * COUNT(*) over `products`. The live version read every row in the table on
 * every page view - fine at 240 products, a full scan per request at a
 * million, and D1 bills rows read. The table is written by build_db.py and
 * has one row per facet value, so it does not grow with the catalogue.
 *
 * It also removes the interpolated column name the old version had, which
 * was safe only because every caller was internal.
 */
const FACET: Record<string, string> = {
  niche: 'niche',
  section: 'section',
  style: 'style',
  colour: 'colour',
  room: 'room',
};

export const countWhere = async (db: DB, col: string, val: string) => {
  const kind = FACET[col];
  if (!kind) throw new Error(`countWhere: no facet for column "${col}"`);
  const r = await db
    .prepare('SELECT n FROM facet_counts WHERE kind = ? AND key = ?')
    .bind(kind, val)
    .first<{ n: number }>();
  return r?.n ?? 0;
};

/** A few more from the same niche, for the bottom of a product page. */
export const alsoIn = (db: DB, n: string, notSlug: string, limit = 8) =>
  db
    .prepare(
      `${LIST} WHERE p.niche = ? AND p.slug != ? ORDER BY p.rank LIMIT ?`
    )
    .bind(n, notSlug, limit)
    .all<Card>();

/** Niche counts, for the navigation and the category index. */
export const nicheCounts = (db: DB) =>
  db
    .prepare(
      'SELECT key AS niche, title AS niche_title, parent AS section, ' +
        'parent_title AS section_title, n FROM facet_counts ' +
        "WHERE kind = 'niche' ORDER BY parent, title"
    )
    .all<{
      niche: string;
      niche_title: string;
      section: string;
      section_title: string;
      n: number;
    }>();

export const allSlugs = (db: DB) =>
  db.prepare('SELECT slug FROM products ORDER BY rank').all<{ slug: string }>();

export const variantById = (db: DB, id: string) =>
  db
    .prepare(
      'SELECT v.*, p.title AS product_title, p.slug AS product_slug ' +
        'FROM variants v JOIN products p ON p.slug = v.slug WHERE v.id = ?'
    )
    .bind(id)
    .first<Variant & { product_title: string; product_slug: string }>();

/**
 * Products in a niche restricted to particular palettes.
 *
 * The home page shows three designs at a size where the whole page turns on
 * them, and a charcoal drawing on a white wall at that scale reads as an
 * empty rectangle. This lets the page ask for the colourful end of a niche
 * and fall back to whatever that niche has if it holds none - which keeps
 * the home page working whatever the catalogue is rebuilt to contain.
 */
export const byNicheColour = (
  db: DB,
  niche: string,
  colours: string[],
  limit = 1
) =>
  db
    .prepare(
      `${LIST} WHERE p.niche = ? AND p.colour IN (` +
        colours.map(() => '?').join(',') +
        ') ORDER BY p.rank LIMIT ?'
    )
    .bind(niche, ...colours, limit)
    .all<Card>();

/**
 * Two more prints that hang with this one: same range, same palette.
 *
 * Not "related products" in the usual sense - the point is a SET. A poster
 * shop's money is in people buying three, which is why "buy two get one
 * free" exists at all, and three prints only look like a set if they share
 * a colour family. Matching on niche alone gives a charcoal coastline next
 * to a neon one, which is a worse suggestion than none.
 */
export const trio = (db: DB, niche: string, colour: string, notSlug: string) =>
  db
    .prepare(
      `${LIST} WHERE p.niche = ? AND p.colour = ? AND p.slug != ? ` +
        'ORDER BY p.rank LIMIT 2'
    )
    .bind(niche, colour, notSlug)
    .all<Card>();

/** The same frame and size of several designs, for adding a set in one go. */
export const variantsFor = (
  db: DB,
  slugs: string[],
  frame: string,
  size: string
) =>
  db
    .prepare(
      'SELECT v.*, p.slug AS product_slug FROM variants v ' +
        'JOIN products p ON p.slug = v.slug WHERE v.slug IN (' +
        slugs.map(() => '?').join(',') +
        ') AND v.frame = ? AND v.size = ?'
    )
    .bind(...slugs, frame, size)
    .all<Variant & { product_slug: string }>();
