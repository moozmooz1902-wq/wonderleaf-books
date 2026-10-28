# Merchant Center identity verification — step by step

Written 28 Oct 2026 from Google's own help pages, not from memory. Two
pages matter: **Verify your business documents**
(support.google.com/merchants/answer/17123687) and **Verify your business
details to restore full visibility** (…/17123828).

**Read the whole of this before you start, because of one rule:**

> If a fraudulent attempt is detected **or you reach the maximum number of
> failed attempts, your account may face full suspension.**

Attempts are limited. This is not something to begin and work out as you
go — get the documents in front of you first.

And a second rule that catches people out:

> **The person who starts the verification must be the one to finish it.**
> Other admins cannot complete it for you.

So do it in one sitting, on one device, as one person.

---

## Before you click anything: get these three things ready

**1. Your own photo ID** — passport or driving licence. Not expired.

**2. A document proving NORYMUS LIMITED exists**, showing the legal name
and the registered address:

- the **Certificate of Incorporation** from Companies House, or
- the **HMRC VAT registration certificate** (GB513541030), or
- any official registration or tax document naming the company

**3. Proof of address** if asked.

### How to photograph them — this is where attempts get burned

Google rejects more submissions on photo quality than on substance:

- A **photo of the original**. Not a photocopy, not a screenshot, not a PDF
  of a scan.
- **All four corners visible** in the frame.
- Clear, in focus, **no glare** — the usual failure is a phone flash
  bouncing off a laminated page. Use daylight, no flash.
- Current and **not expired**.

---

## The name matching, which is the real trap

Google compares the document against your profile, and a mismatch is an
**automatic rejection** — not a human deciding you're close enough.

| Field | What it must say |
|---|---|
| **Legal / payments profile name** | **NORYMUS LIMITED** — exactly, as on Companies House |
| Registered address | **28 Bedford Square, Leigh, WN7 2AA** |
| Company number | 17020866 |
| VAT | GB513541030 |
| **Display / business name** shown to shoppers | **Walryvo** |

**Those last two lines are not a contradiction and getting them the wrong
way round is the most likely way to fail this.** Merchant Center keeps the
customer-facing shop name separately from the legal identity. The shop is
Walryvo; the company is NORYMUS LIMITED; the documents prove the company.

**Check the payments profile name BEFORE you submit.** Google's page says
plainly: if the payments profile carries a different organisation name from
your proof-of-organisation document, **update the payments profile first,
then resubmit.** Doing it the other way round spends an attempt to learn
something you could have checked in thirty seconds.

---

## The steps

1. **Merchant Center → the notification or the account-issues panel.**
   The prompt appears wherever Google has flagged it — a banner, the
   "Needs attention" area, or under Business information. There is no
   fixed menu path and it moves; follow the prompt rather than hunting for
   a page.

2. **Start it, and stay with it.** Whoever clicks must finish. One device,
   one sitting.

3. **Complete whichever checks Google assigns you.** It picks the route,
   you do not:
   - **Selfie verification** — a quick liveness check through your device
     camera. Good light, plain background, no hat or glasses.
   - **Document verification** — upload the government ID and, where
     asked, the organisation document.

4. **If it asks you to connect a Google payments profile:** pick an
   existing one from the list if you have one (Ads, YouTube, Play) so the
   details autofill, or build a new one on screen. Then check every field
   against the table above before continuing.

5. **Submit, and then leave it alone.** If a manual review is needed it
   "usually takes a few working days". Do not resubmit while it is
   pending — that is how attempts get spent.

---

## What happens after

- **Passes:** restrictions lift automatically and products become eligible
  for full visibility across Google. This is the gate the whole
  `SCALE_SCHEDULE.md` ladder waits on.
- **Fails:** fix whatever it names and try again, carefully. After several
  failures, contact support rather than keep trying — the attempt limit is
  real and the end of it is full suspension.

---

## Do this first, it takes a minute

**Confirm the VAT record matches** at <https://www.gov.uk/check-uk-vat-number>
— GB513541030 should return NORYMUS LIMITED at 28 Bedford Square. Google
cross-checks the VAT record against the site and the profile, and if that
returns something different, find out why before submitting anything.

**And change the SIC code** (96090 → 47910) if you have not. It does not
block verification, but it is the same class of mismatch: the public
register saying the company does something other than sell art prints.
