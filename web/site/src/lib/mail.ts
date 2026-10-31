/**
 * THE SUPPORT INBOX — sales@walryvo.com, read and answered from /admin.
 *
 * Asked for on 31 Oct: "somewhere I can see emails from customers and reply
 * from there, like eBay."
 *
 * WHY MICROSOFT GRAPH AND NOT A MAILBOX OF OUR OWN. The obvious shortcut is
 * to take delivery of the mail ourselves - point an MX record at a Worker,
 * store what arrives in D1 - and it is a trap twice over. It would mean
 * moving the MX record off Microsoft 365, which is the live business
 * mailbox, so a mistake does not lose a feature, it loses the customer's
 * email. And a reply sent from a different system would not thread: the
 * customer sees a new message from an address that is not the one they
 * wrote to.
 *
 * Reading the real mailbox through Graph instead means the mailbox stays
 * the single source of truth. A message read here is read in Outlook on the
 * phone. A reply sent here goes out as sales@walryvo.com, in the same
 * thread, and is in Sent Items. Nothing is duplicated and nothing can
 * drift, which is the same reason the shop has one function that builds a
 * product.
 *
 * NOTHING HERE IS CACHED IN D1 ON PURPOSE. An inbox copy would be a second
 * copy of customer correspondence living somewhere the privacy policy did
 * not account for, and it would be stale the moment anyone used Outlook.
 *
 * SETUP, and the one permission to get right: see web/INBOX.md. The three
 * secrets are MS_TENANT_ID, MS_CLIENT_ID, MS_CLIENT_SECRET, and the
 * mailbox is MS_MAILBOX (defaults to the business contact address).
 * Application permissions in Entra reach EVERY mailbox in the tenant
 * unless an application access policy narrows them, so INBOX.md says to
 * narrow it to this one address.
 */

export interface MailCfg {
  tenant: string;
  clientId: string;
  secret: string;
  mailbox: string;
}

export function mailCfg(env: any, fallbackMailbox: string): MailCfg | null {
  const tenant = env?.MS_TENANT_ID;
  const clientId = env?.MS_CLIENT_ID;
  const secret = env?.MS_CLIENT_SECRET;
  if (!tenant || !clientId || !secret) return null;
  return {
    tenant,
    clientId,
    secret,
    mailbox: env?.MS_MAILBOX || fallbackMailbox,
  };
}

/**
 * An access token, cached in the isolate until shortly before it expires.
 *
 * Graph tokens last an hour. Fetching one per dashboard poll would be a
 * round trip to Microsoft every ten seconds for no reason, and would make
 * the inbox the slowest panel on the page.
 */
let tok: { value: string; until: number } | null = null;

async function token(cfg: MailCfg): Promise<string> {
  if (tok && Date.now() < tok.until) return tok.value;
  const body = new URLSearchParams({
    client_id: cfg.clientId,
    client_secret: cfg.secret,
    scope: 'https://graph.microsoft.com/.default',
    grant_type: 'client_credentials',
  });
  const r = await fetch(
    `https://login.microsoftonline.com/${encodeURIComponent(cfg.tenant)}/oauth2/v2.0/token`,
    {
      method: 'POST',
      headers: { 'content-type': 'application/x-www-form-urlencoded' },
      body,
    }
  );
  const j: any = await r.json().catch(() => ({}));
  if (!r.ok || !j.access_token)
    throw new Error(
      `Microsoft refused the sign-in: ${j.error_description || j.error || r.status}`
    );
  // 60 seconds of slack so a token never expires mid-request.
  tok = {
    value: j.access_token,
    until: Date.now() + Math.max(60, (j.expires_in || 3600) - 60) * 1000,
  };
  return tok.value;
}

async function graph(cfg: MailCfg, path: string, init: RequestInit = {}) {
  const t = await token(cfg);
  const r = await fetch(`https://graph.microsoft.com/v1.0${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${t}`,
      'content-type': 'application/json',
      ...(init.headers || {}),
    },
  });
  if (r.status === 204) return null;
  const j: any = await r.json().catch(() => ({}));
  if (!r.ok) {
    const m = j?.error?.message || `HTTP ${r.status}`;
    // The two failures worth naming, because both look like bugs and are
    // both a setting somebody has not clicked yet.
    if (/Access is denied|Authorization_RequestDenied/i.test(m))
      throw new Error(
        'Microsoft accepted the sign-in but refused the mailbox. The app ' +
          'needs Mail.ReadWrite and Mail.Send APPLICATION permissions with ' +
          'admin consent granted — see web/INBOX.md step 3.'
      );
    if (/MailboxNotEnabledForRESTAPI|ResourceNotFound|does not exist/i.test(m))
      throw new Error(
        `Microsoft does not recognise the mailbox ${cfg.mailbox}. Check ` +
          'MS_MAILBOX is the full address of a real licensed mailbox.'
      );
    throw new Error(m);
  }
  return j;
}

const box = (cfg: MailCfg) => `/users/${encodeURIComponent(cfg.mailbox)}`;

export interface Note {
  id: string;
  conversationId: string;
  from: string;
  fromName: string;
  subject: string;
  preview: string;
  received: string;
  read: boolean;
  answered: boolean;
  hasAttachments: boolean;
}

function who(m: any): { addr: string; name: string } {
  const e = m?.from?.emailAddress || m?.sender?.emailAddress || {};
  return { addr: e.address || '', name: e.name || e.address || 'Unknown' };
}

/** The inbox, newest first. */
export async function listMail(cfg: MailCfg, limit = 25): Promise<Note[]> {
  const j = await graph(
    cfg,
    `${box(cfg)}/mailFolders/inbox/messages` +
      `?$top=${Math.min(50, Math.max(1, limit))}` +
      '&$orderby=receivedDateTime desc' +
      '&$select=id,conversationId,from,sender,subject,bodyPreview,' +
      'receivedDateTime,isRead,hasAttachments,flag'
  );
  return (j?.value || []).map((m: any) => {
    const w = who(m);
    return {
      id: m.id,
      conversationId: m.conversationId,
      from: w.addr,
      fromName: w.name,
      subject: m.subject || '(no subject)',
      preview: (m.bodyPreview || '').slice(0, 300),
      received: m.receivedDateTime,
      read: !!m.isRead,
      // Outlook sets this when the message has been replied to. It is not
      // perfectly reliable across clients, so the dashboard shows it as a
      // hint rather than as a status anyone should rely on.
      answered: false,
      hasAttachments: !!m.hasAttachments,
    };
  });
}

/** One message, as plain text, and marked read. */
export async function readMail(cfg: MailCfg, id: string) {
  const m = await graph(
    cfg,
    `${box(cfg)}/messages/${encodeURIComponent(id)}` +
      '?$select=id,conversationId,from,sender,toRecipients,subject,body,' +
      'receivedDateTime,isRead,hasAttachments'
  );
  // Reading it here marks it read in Outlook too, which is the point of
  // using the real mailbox: two inboxes that disagree about what has been
  // dealt with are worse than one inbox.
  if (!m.isRead)
    await graph(cfg, `${box(cfg)}/messages/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify({ isRead: true }),
    }).catch(() => {});
  const w = who(m);
  const html = m?.body?.contentType === 'html';
  return {
    id: m.id,
    conversationId: m.conversationId,
    from: w.addr,
    fromName: w.name,
    subject: m.subject || '(no subject)',
    received: m.receivedDateTime,
    hasAttachments: !!m.hasAttachments,
    text: html ? stripHtml(m?.body?.content || '') : m?.body?.content || '',
  };
}

/**
 * Reply, in the thread, as the mailbox.
 *
 * Graph's /reply keeps the conversation id, the In-Reply-To header and the
 * quoted original, so the customer sees an answer to their own message
 * rather than a new one from a system they have never heard of.
 */
export async function replyMail(cfg: MailCfg, id: string, text: string) {
  const esc = (s: string) =>
    s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c] as string));
  const html =
    '<div style="font-family:Segoe UI,Arial,sans-serif;font-size:14px">' +
    esc(text).replace(/\n/g, '<br>') +
    '</div>';
  await graph(cfg, `${box(cfg)}/messages/${encodeURIComponent(id)}/reply`, {
    method: 'POST',
    body: JSON.stringify({ message: { body: { contentType: 'HTML', content: html } } }),
  });
}

/** Rough, and only ever used for display. */
function stripHtml(h: string) {
  return h
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/(p|div|tr|li|h\d)>/gi, '\n')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}
