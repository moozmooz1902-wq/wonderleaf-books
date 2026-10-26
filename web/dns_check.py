#!/usr/bin/env python3
"""Snapshot walryvo.com's DNS, then prove nothing was lost moving it.

WHY THIS EXISTS. Moving nameservers to Cloudflare does not copy records -
Cloudflare answers with whatever its scan happened to import, and anything
it missed stops existing the moment the switch propagates. The mailbox is
Microsoft 365 via GoDaddy, so a missed MX or DKIM record kills
sales@walryvo.com, which is the contact address on every page of the shop
and in Merchant Center. The failure is silent: mail simply stops arriving,
and you find out when a customer says they emailed days ago.

So: snapshot BEFORE the switch, compare AFTER.

    python3 dns_check.py --save      # before you touch anything
    python3 dns_check.py             # after, compares against the snapshot

The comparison is on the record VALUES, not on how they are served, so a
record that moved from GoDaddy to Cloudflare still counts as present. A
record that vanished is reported loudly. The mail records are checked
first and a loss among them is fatal rather than a warning, because
everything else on the list is recoverable at leisure and that one is not.
"""
import argparse, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "dns_snapshot.json")
DOMAIN = "walryvo.com"

# name suffix -> record types to ask for. "" means the bare domain.
QUERIES = [
    ("", "NS"), ("", "A"), ("", "AAAA"), ("", "MX"), ("", "TXT"), ("", "CAA"),
    ("www", "CNAME"), ("www", "A"),
    ("autodiscover", "CNAME"),
    ("selector1._domainkey", "CNAME"),
    ("selector2._domainkey", "CNAME"),
    ("_dmarc", "TXT"),
    ("_sip._tls", "SRV"),
    ("_sipfederationtls._tcp", "SRV"),
    ("lyncdiscover", "CNAME"),
    ("enterpriseregistration", "CNAME"),
    ("enterpriseenrollment", "CNAME"),
    ("msoid", "CNAME"),
    ("email", "CNAME"),
    ("ftp", "CNAME"),
]

# Lose any of these and mail breaks. Everything else is an inconvenience.
MAIL_CRITICAL = {("", "MX"), ("", "TXT"), ("autodiscover", "CNAME"),
                 ("selector1._domainkey", "CNAME"),
                 ("selector2._domainkey", "CNAME"), ("_dmarc", "TXT")}


def resolve(name, rtype):
    """Ask a public resolver rather than the local one, so the answer is
    what the world sees rather than anything cached in this container."""
    fqdn = f"{name}.{DOMAIN}" if name else DOMAIN
    try:
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "20",
             f"https://dns.google/resolve?name={fqdn}&type={rtype}"],
            capture_output=True, text=True, timeout=30)
        d = json.loads(r.stdout or "{}")
    except Exception:
        return None          # None means "could not ask", not "empty"
    return sorted(a.get("data", "").strip().rstrip(".")
                  for a in d.get("Answer", [])
                  if a.get("type") == {"A": 1, "NS": 2, "CNAME": 5, "SOA": 6,
                                       "MX": 15, "TXT": 16, "AAAA": 28,
                                       "SRV": 33, "CAA": 257}.get(rtype))


def capture():
    out, failed = {}, []
    for name, rtype in QUERIES:
        vals = resolve(name, rtype)
        if vals is None:
            failed.append(f"{name or '@'} {rtype}")
            continue
        if vals:
            out[f"{name}|{rtype}"] = vals
        time.sleep(0.15)
    return out, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true",
                    help="write the snapshot (do this BEFORE switching)")
    a = ap.parse_args()

    print(f"querying {DOMAIN} ...")
    now, failed = capture()
    if failed:
        print(f"  could not query: {', '.join(failed)}")

    if a.save:
        json.dump({"captured": time.strftime("%Y-%m-%d %H:%M:%S UTC",
                                             time.gmtime()),
                   "domain": DOMAIN, "records": now},
                  open(SNAP, "w"), indent=1)
        print(f"\nsaved {len(now)} record sets to {SNAP}")
        for k, v in sorted(now.items()):
            n, t = k.split("|")
            print(f"  {t:<6} {n or '@':<28} {', '.join(x[:70] for x in v)}")
        print("\nNow move the nameservers. Re-run WITHOUT --save afterwards.")
        return 0

    if not os.path.exists(SNAP):
        print(f"\nNo snapshot at {SNAP}. Run with --save first.")
        return 2
    before = json.load(open(SNAP))
    old = before["records"]
    print(f"comparing against snapshot from {before['captured']}\n")

    lost, changed, kept, mail_lost = [], [], 0, []
    for key, vals in sorted(old.items()):
        name, rtype = key.split("|")
        cur = now.get(key, [])
        if not cur:
            lost.append((name, rtype, vals))
            if (name, rtype) in MAIL_CRITICAL:
                mail_lost.append((name, rtype, vals))
        elif set(cur) != set(vals):
            changed.append((name, rtype, vals, cur))
        else:
            kept += 1

    ns = now.get("|NS", [])
    on_cf = any("cloudflare" in x.lower() for x in ns)
    print(f"nameservers: {', '.join(ns) if ns else 'none'}")
    print(f"  -> on Cloudflare: {on_cf}\n")

    print(f"{kept} record set(s) unchanged")
    if changed:
        print(f"\n{len(changed)} CHANGED:")
        for n, t, o, c in changed:
            print(f"  {t:<6} {n or '@'}")
            print(f"         was: {', '.join(x[:70] for x in o)}")
            print(f"         now: {', '.join(x[:70] for x in c)}")
    if lost:
        print(f"\n{len(lost)} MISSING:")
        for n, t, o in lost:
            flag = "  <-- MAIL" if (n, t) in MAIL_CRITICAL else ""
            print(f"  {t:<6} {n or '@'}{flag}")
            for x in o:
                print(f"         {x[:100]}")

    print()
    if mail_lost:
        print("MAIL IS BROKEN OR ABOUT TO BE.")
        print("Add the records listed above as MAIL back in the Cloudflare")
        print("DNS tab, set to DNS only (grey cloud), then re-run this.")
        print("Until then sales@walryvo.com is not receiving.")
        return 1
    if lost or changed:
        print("Mail records survived. The differences above are not fatal,")
        print("but check each one is deliberate - the two parking A records")
        print("and the www CNAME are MEANT to be gone.")
        return 0
    print("Nothing lost. Every record from the snapshot is still answering.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
