#!/usr/bin/env node
/**
 * Shrink an eBay active-listings download to the only part that matters.
 *
 *     node web/tools/shrink-ebay-download.mjs <download.csv> [out.csv.gz]
 *
 * WHY THIS EXISTS. A 380 MB download over a slow upstream connection is
 * most of a day of uploading, and all but a sliver of it is wasted: an End
 * file needs the ITEM NUMBER and nothing else. Titles, prices, quantities,
 * SKUs and every variation row are irrelevant to ending a listing. This
 * keeps the item number and the category - the category only so the files
 * can still be split into art and t-shirts - and throws the rest away.
 *
 * The result is roughly 1% of the original and gzips to a fraction of
 * that, so a 380 MB upload becomes a few megabytes.
 *
 * IT DOES NOT BUILD THE END FILE. That is deliberate. The end file is the
 * irreversible one, and it is worth having it built and checked somewhere
 * the checks actually run - every item number traced back to this output,
 * nothing invented, nothing dropped, header byte-identical to the file
 * eBay has already accepted.
 *
 * ONLY PARENT ROWS CARRY AN ITEM NUMBER. The rest are
 * `Relationship=Variation` children with a blank one, belonging to the
 * parent above them. eBay ends a listing by item number and that ends
 * every variation with it, so the children are dropped here rather than
 * uploaded and then ignored.
 */
import { createReadStream, createWriteStream, statSync } from 'node:fs';
import { createGzip } from 'node:zlib';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';

const [, , src, outArg] = process.argv;
if (!src) {
  console.error('usage: node shrink-ebay-download.mjs <download.csv> [out.csv.gz]');
  process.exit(2);
}
const out = outArg || 'ebay-items.csv.gz';

/**
 * A CSV reader that respects quotes.
 *
 * Splitting on commas would be wrong on the very first data row: eBay
 * titles contain commas, and a quoted field may contain a newline. This is
 * the whole parser and it is a dozen lines, which is cheaper than finding
 * out later that every title with a comma shifted the columns along one.
 */
async function* records(stream) {
  let field = '';
  let row = [];
  let quoted = false;
  let prevQuote = false;
  let first = true;
  for await (const chunk of stream) {
    let s = chunk.toString('utf8');
    // eBay writes a UTF-8 BOM. Left in place it becomes part of the first
    // field, so the "#INFO" line is not recognised, the template line is
    // read as the header, and the whole file looks like the wrong kind of
    // download. One character, and it fails in a way that blames the file.
    if (first) { s = s.replace(/^\uFEFF/, ''); first = false; }
    for (let i = 0; i < s.length; i++) {
      const c = s[i];
      if (quoted) {
        if (c === '"') {
          if (prevQuote) { field += '"'; prevQuote = false; }
          else prevQuote = true;
        } else if (prevQuote) {
          prevQuote = false;
          quoted = false;
          i--;                       // re-handle this character unquoted
        } else field += c;
      } else if (c === '"' && field === '') {
        quoted = true;
      } else if (c === ',') {
        row.push(field); field = '';
      } else if (c === '\n') {
        row.push(field); field = '';
        yield row; row = [];
      } else if (c !== '\r') {
        field += c;
      }
    }
  }
  if (field !== '' || row.length) { row.push(field); yield row; }
}

const size = statSync(src).size;
console.log(`reading ${src}  (${(size / 1048576).toFixed(1)} MB)`);

const gz = createGzip({ level: 9 });
const sink = pipeline(gz, createWriteStream(out));

let header = null;
let iItem = -1, iCat = -1, iRel = -1;
let rows = 0, listings = 0, children = 0, odd = 0;
const cats = new Map();
const seen = new Set();
let dupes = 0;

gz.write('item,category\n');

for await (const r of records(createReadStream(src))) {
  rows++;
  if (rows === 1 && r[0]?.startsWith('#INFO')) continue;   // template line
  if (!header) {
    header = r.map((h) => h.trim());
    iItem = header.indexOf('Item number');
    iCat = header.indexOf('Category name');
    iRel = header.indexOf('Relationship');
    if (iItem < 0) {
      console.error(
        'No "Item number" column. Columns found:\n  ' + header.join(' | ') +
        '\nThis does not look like an active-listings download.'
      );
      process.exit(1);
    }
    continue;
  }
  const item = (r[iItem] || '').trim();
  if (!item) { children++; continue; }
  if (!/^\d{9,15}$/.test(item)) { odd++; continue; }
  if (seen.has(item)) { dupes++; continue; }
  seen.add(item);
  const cat = (r[iCat] || '').trim();
  cats.set(cat, (cats.get(cat) || 0) + 1);
  listings++;
  if (!gz.write(`${item},${cat.replace(/,/g, ' ')}\n`)) {
    await new Promise((res) => gz.once('drain', res));
  }
}
gz.end();
await sink;

const outSize = statSync(out).size;
console.log(`
source rows              ${rows.toLocaleString()}
  variation children     ${children.toLocaleString()}   (dropped - the parent ends them)
  duplicate item numbers ${dupes.toLocaleString()}
  malformed item numbers ${odd.toLocaleString()}
LISTINGS                 ${listings.toLocaleString()}
`);
for (const [c, n] of [...cats].sort((a, b) => b[1] - a[1]))
  console.log(`   ${n.toLocaleString().padStart(9)}  ${c || '(no category)'}`);
console.log(`
wrote ${out}  (${(outSize / 1048576).toFixed(2)} MB, ${(outSize / size * 100).toFixed(2)}% of the original)

Upload that file. Paste the numbers above as well - they are what the
end files get checked against.`);
