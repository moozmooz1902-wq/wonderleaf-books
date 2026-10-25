// Who this business is, and the few helpers that depend on it.
//
// business.json is a copy of web/business.config.json, written by
// build_db.py so the site and the feed read identical values. Nothing here
// invents a fact about the business: if a field is null the build is
// supposed to fail, and preflight.py is what fails it.
import business from '../data/business.json';
import taxonomy from '../data/taxonomy.json';

export const B = business as Business;
export const TAX = taxonomy as Taxonomy;

export interface Business {
  brand: string;
  domain: string;
  legal_name: string;
  company_number: string;
  vat_number: string;
  registered_address: string[];
  trading_address_same: boolean;
  trading_address: string[] | null;
  email: string;
  phone: string;
  support_hours: string;
  currency: string;
  prices_include_vat: boolean;
  fulfilment: {
    made_in: string;
    dispatch_working_days: number;
    delivery: { name: string; price: number; min_days: number; max_days: number; region: string }[];
    ships_to: string[];
  };
  returns: {
    window_days: number;
    who_pays_return_postage: 'customer' | 'us';
    restocking_fee: number;
  };
  social_proof: { reviews: string };
}

export interface Taxonomy {
  sections: { slug: string; title: string }[];
  niches: Record<string, { slug: string; title: string; section: string; blurb: string }>;
  styles: { slug: string; title: string; blurb: string }[];
  colours: { slug: string; title: string; blurb: string }[];
  rooms: { slug: string; title: string }[];
}

// FAIL READABLY, AT BOOT, NAMING THE FIELD.
//
// With the delivery price still null, a product page died with "Cannot read
// properties of null (reading 'toFixed')" pointing at a line of the
// template - which says nothing about the cause and sends you reading the
// wrong file. These fields are the ones only the seller can supply, so a
// missing one is a configuration error and should say so once, loudly,
// rather than surface as a different mystery on every page that happens to
// touch it.
//
// preflight.py is still what prevents a deploy; this is what makes the
// failure legible while the shop is being set up.
const REQUIRED: (keyof Business)[] = [
  'brand', 'domain', 'legal_name', 'company_number', 'vat_number',
  'registered_address', 'email', 'phone',
];
const unset = REQUIRED.filter((k) => !B[k]);
if (B.fulfilment?.delivery?.[0]?.price === null ||
    B.fulfilment?.delivery?.[0]?.price === undefined)
  unset.push('fulfilment.delivery[0].price' as keyof Business);
if (unset.length)
  throw new Error(
    // Worded to avoid the phrase preflight.py scans for ("not set"): this
    // message is source text, so saying it here made the checker report
    // its own error string as placeholder copy on the live site.
    `business.config.json is incomplete: ${unset.join(', ')} ` +
      `${unset.length === 1 ? 'is' : 'are'} still empty. Fill ` +
      `web/business.config.json, then re-run ` +
      `python3 catalogue/build_db.py to copy it into the site. ` +
      `The shop must not go live with blanks in its business identity - ` +
      `see the note at the top of that file.`
  );

export const money = (n: number) =>
  new Intl.NumberFormat('en-GB', { style: 'currency', currency: B.currency }).format(n);

/** The shop's own image URL. Never an r2.dev one - see wrangler.toml. */
export const img = (path: string) => `/img/${path}`;

export const siteUrl = (env?: { SITE_URL?: string }) =>
  (env?.SITE_URL || `https://${B.domain}`).replace(/\/$/, '');

export const abs = (path: string, env?: { SITE_URL?: string }) =>
  `${siteUrl(env)}${path.startsWith('/') ? path : '/' + path}`;

/** Delivery, said the same way everywhere it is said. */
export const deliveryLine = () => {
  const d = B.fulfilment.delivery[0];
  const cost = d.price === 0 ? 'Free' : money(d.price);
  return `${cost} UK delivery. Made to order and dispatched within ${B.fulfilment.dispatch_working_days} working days, then ${d.min_days}-${d.max_days} working days in the post.`;
};

export const returnsLine = () =>
  `${B.returns.window_days}-day returns from the day it arrives.`;

export const niche = (slug: string) => TAX.niches[slug];
export const sectionTitle = (slug: string) =>
  TAX.sections.find((s) => s.slug === slug)?.title ?? slug;
