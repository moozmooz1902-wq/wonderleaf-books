# Connecting the customer inbox

Written 31 Oct 2026. This is the one part of the back office that needs
setup outside the shop, because it reaches into the real Microsoft 365
mailbox at **sales@walryvo.com**.

Once it is done, `/admin` shows customer email and you can reply from
there. A reply goes out **as sales@walryvo.com, in the same thread**, and
lands in Sent Items — so the customer sees an answer to their own message,
not a new one from a system they have never heard of.

## Why it reads the real mailbox instead of keeping its own

The shortcut is to take delivery of the mail ourselves: point the MX record
at a Worker and store what arrives. It is a trap twice over.

- It means moving the MX record off Microsoft 365, which is the live
  business mailbox. A mistake there does not lose a feature, it loses the
  customer's email.
- A reply sent from a separate system does not thread, and comes from an
  address the customer did not write to.

Reading the real mailbox keeps one source of truth. A message read in
`/admin` is read in Outlook on your phone, and the other way round.
Nothing is copied into our database, so there is no second pile of customer
correspondence sitting somewhere the privacy policy did not account for.

---

## Step 1 — Register an app

1. Go to **<https://entra.microsoft.com>** and sign in with the Microsoft
   365 account that owns sales@walryvo.com.
2. **Applications → App registrations → New registration.**
3. Name it `Walryvo back office`. Leave "Supported account types" on
   **Accounts in this organizational directory only**. No redirect URI —
   the shop signs in as itself, not as a person.
4. **Register.**

On the overview page that appears, copy two values:

| Entra calls it | Set it as |
|---|---|
| **Application (client) ID** | `MS_CLIENT_ID` |
| **Directory (tenant) ID** | `MS_TENANT_ID` |

## Step 2 — Make a secret

1. **Certificates & secrets → Client secrets → New client secret.**
2. Description `walryvo worker`, expiry **24 months**.
3. **Copy the Value immediately** — the column headed Value, not Secret ID.
   Entra never shows it again. This is `MS_CLIENT_SECRET`.

**Put a reminder in your calendar for the expiry date.** When a client
secret expires the inbox simply stops working, with a sign-in error and no
warning beforehand.

## Step 3 — Grant the two permissions

1. **API permissions → Add a permission → Microsoft Graph →
   Application permissions** (not Delegated — the shop has no signed-in
   user).
2. Tick **Mail.ReadWrite** and **Mail.Send**.
3. **Add permissions**, then **Grant admin consent for <your tenant>**.
   Both rows must end up green and say *Granted*.

Without the consent click the sign-in succeeds and every mailbox call is
refused, which looks like a bug and is not one. The dashboard says so in
those words if it happens.

## Step 4 — Narrow it to one mailbox. Do not skip this.

**Application permissions reach EVERY mailbox in the tenant.** As granted
above, that app can read and send as anyone you ever add. For a one-person
tenant that is a smaller blast radius than it sounds, but it is still a
key that opens more doors than it needs to, and the fix is two commands.

In PowerShell:

```powershell
Install-Module ExchangeOnlineManagement -Scope CurrentUser
Connect-ExchangeOnline -UserPrincipalName sales@walryvo.com

New-ApplicationAccessPolicy `
  -AppId <MS_CLIENT_ID> `
  -PolicyScopeGroupId sales@walryvo.com `
  -AccessRight RestrictAccess `
  -Description "Walryvo back office: this mailbox only"
```

Check it took:

```powershell
Test-ApplicationAccessPolicy -Identity sales@walryvo.com -AppId <MS_CLIENT_ID>
```

`AccessCheckResult: Granted` is right. Run the same test against any other
address in the tenant and it should say **Denied**.

The policy can take up to an hour to apply.

## Step 5 — Four secrets, then deploy

From `web/site`:

```bash
npx wrangler secret put MS_TENANT_ID
npx wrangler secret put MS_CLIENT_ID
npx wrangler secret put MS_CLIENT_SECRET
npx wrangler secret put MS_MAILBOX        # sales@walryvo.com
npm run deploy
```

`MS_MAILBOX` is optional — it defaults to the contact address in
`business.config.json`, which is already sales@walryvo.com. Set it anyway;
it costs nothing and it means changing the shop's public contact address
later cannot silently repoint the inbox.

Reload `/admin`. The Customer inbox panel should fill.

---

## If it does not work

| What you see | What it is |
|---|---|
| "The inbox is not connected yet" | One of the three secrets is missing or empty. |
| "Microsoft refused the sign-in" | Wrong tenant id, wrong client id, or an expired/mistyped secret. The Value, not the Secret ID. |
| "accepted the sign-in but refused the mailbox" | Step 3 — the permissions are Delegated rather than Application, or admin consent was never granted. |
| "does not recognise the mailbox" | `MS_MAILBOX` is not a real licensed mailbox, or the access policy in step 4 is excluding it. |

## What it does not do

No attachments — the dashboard says when a message has them and you open
those in Outlook. No folders beyond the inbox, no search, no compose from
scratch. It is a support queue, not a mail client: see what customers
asked, answer them, move on. Outlook is still there for everything else.
