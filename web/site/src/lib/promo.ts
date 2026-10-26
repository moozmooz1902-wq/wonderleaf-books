/**
 * Buy two, get one free — the ONE implementation.
 *
 * WHY THIS IS A MODULE AND NOT A FEW LINES IN THE BASKET. A promotion is a
 * price, and a price that is worked out twice is a price that will one day
 * disagree with itself. The basket page showing "£17.98" while Stripe charges
 * £26.97 is a price mismatch at the single worst moment, and "the price at
 * checkout does not match the price advertised" is named in Google's
 * dishonest-transaction rules. So the basket does not compute anything: it
 * asks /api/basket, which calls this, and checkout calls this too.
 *
 * WHY CHEAPEST-FREE. It is the ordinary reading of "buy two get one free" and
 * the one every poster shop uses: in any three prints, the cheapest costs
 * nothing. Taking the dearest free would be more generous than advertised,
 * which is a nice problem, but a shopper who worked out their own total and
 * got a different one at checkout is not a nice problem either way.
 *
 * WHAT MAKES IT LEGAL. Nothing is marked up to be marked down. Every item is
 * sold at its normal price and the discount is a genuine free third item, so
 * there is no reference price to justify - which is exactly why this works
 * and a doubled "was" price does not: a "was" price has to be a price the
 * shop actually charged, both to Google and to the CMA.
 */
export const PROMO = {
  id: 'WALRYVO-3FOR2',
  code: '3FOR2',
  title: 'Buy 2, get 1 free',
  short: 'Buy 2, get 1 free',
  blurb:
    'Add any three prints and the cheapest one is free. Mix framed and ' +
    'unframed, any sizes, across the whole range.',
  groupSize: 3,
  active: true,
} as const;

export interface PricedLine {
  id: string;
  title: string;
  qty: number;
  price: number;
  /** How many units of THIS line are free. */
  free: number;
}

export interface Priced {
  lines: PricedLine[];
  units: number;
  freeUnits: number;
  subtotal: number;
  discount: number;
  total: number;
  /** Units still needed for the next free one, 0 when none is pending. */
  toNextFree: number;
}

/**
 * Price a basket. `lines` carry the real per-unit price read from the
 * catalogue - never a price that came from the browser.
 */
export function priceBasket(
  lines: { id: string; title: string; qty: number; price: number }[]
): Priced {
  const units = lines.reduce((a, l) => a + l.qty, 0);
  const subtotal = lines.reduce((a, l) => a + l.qty * l.price, 0);

  // Every unit as its own entry, cheapest first, so the free ones are the
  // cheapest in the basket regardless of which line they came from.
  const expanded: { id: string; price: number }[] = [];
  for (const l of lines)
    for (let i = 0; i < l.qty; i++) expanded.push({ id: l.id, price: l.price });
  expanded.sort((a, b) => a.price - b.price);

  const freeUnits = PROMO.active
    ? Math.floor(units / PROMO.groupSize)
    : 0;
  const freeBy: Record<string, number> = {};
  let discount = 0;
  for (let i = 0; i < freeUnits; i++) {
    const u = expanded[i];
    discount += u.price;
    freeBy[u.id] = (freeBy[u.id] || 0) + 1;
  }

  const rem = units % PROMO.groupSize;
  return {
    lines: lines.map((l) => ({ ...l, free: freeBy[l.id] || 0 })),
    units,
    freeUnits,
    subtotal: round2(subtotal),
    discount: round2(discount),
    total: round2(subtotal - discount),
    toNextFree: PROMO.active && units > 0 ? (rem === 0 ? 0 : PROMO.groupSize - rem) : 0,
  };
}

/** Money is pounds here and pence at Stripe; never let binary floats decide. */
export const round2 = (n: number) => Math.round(n * 100) / 100;
