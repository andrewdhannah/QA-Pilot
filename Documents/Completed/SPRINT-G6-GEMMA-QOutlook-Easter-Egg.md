# Sprint G6 — QOutlook Easter Egg
## Gemma Build Prompt

Read GEMMA-STYLE-GUIDE.md before writing any code.
All previous sprints can be complete or in progress — this is fully independent.

---

## Context

This is the QA Pilot platform.
Stack: pure HTML/CSS/JS, no frameworks, no CDN links.
The OS desktop has a Browser app (`desktop/apps/browser.html`) with an internal pages registry:

```javascript
var INTERNAL_PAGES = {
    "qapache": function() { return QAPACHE_PAGE; },
    "qtube":   function() { return QTUBE_PAGE; },
};
```

When a user types a registered keyword into the browser address bar and hits Enter,
the browser renders the corresponding HTML string as a full internal page.

This sprint adds **QOutlook** — a fake Microsoft Outlook spoof — to the registry.
Type `qoutlook` in the address bar to open it.

---

## What QOutlook Is

A fake Outlook web client. Classic three-panel layout:
- **Left sidebar** — folder list (Inbox, Sent, Drafts, Junk, Deleted Items)
- **Centre panel** — email list showing ~6 fake emails
- **Right panel** — reading pane showing the selected email

The inbox has one unread email pinned at the top. The joke is the punchline.
Everything else exists to make the inbox feel real before the trainee reads it.

---

## Deliverable: QOUTLOOK_PAGE HTML string

Add `QOUTLOOK_PAGE` as a template literal string constant in `apps/browser.html`,
then register it:

```javascript
var INTERNAL_PAGES = {
    "qapache":   function() { return QAPACHE_PAGE; },
    "qtube":     function() { return QTUBE_PAGE; },
    "qoutlook":  function() { return QOUTLOOK_PAGE; },
};
```

---

## Visual Design

Match the real Outlook Web App aesthetic:

```css
/* Colour palette — Outlook blue */
--ol-blue:        #0078d4;
--ol-blue-dark:   #005a9e;
--ol-sidebar-bg:  #f3f2f1;
--ol-list-bg:     #ffffff;
--ol-reading-bg:  #ffffff;
--ol-border:      #edebe9;
--ol-unread-bar:  #0078d4;   /* left accent on unread email */
--ol-text:        #201f1e;
--ol-text-muted:  #605e5c;
--ol-hover:       #edebe9;
--ol-selected:    #deecf9;
```

Layout proportions:
- Sidebar: 200px fixed
- Email list: 300px fixed
- Reading pane: flex 1 (fills remainder)
- Full height of parent iframe (100vh)

Topbar: Outlook blue background, white "Outlook" wordmark on left,
fake search bar in centre, avatar circle "AH" on right (Andrew Hannah initials).

---

## The Emails

Six emails in the inbox. Display in this order (newest first).
The **first email is unread** (bold sender, bold subject, blue left accent bar).
All others are read.

| # | From | Subject | Time / Date | Read? |
|---|------|---------|-------------|-------|
| 1 | IT Support | Re: Coffee Machine — URGENT | 9:14 AM | **UNREAD** |
| 2 | Elyse Hannah | QA signoff — Case #4471 | Yesterday | read |
| 3 | GitHub | [QA-Pilot] Pull request merged: sprint-g5 | Yesterday | read |
| 4 | Microsoft Teams | You have a new voicemail | Mon | read |
| 5 | IT Support | Scheduled maintenance — Sat 2am | Last week | read |
| 6 | No-Reply | Your password will expire in 14 days | Last week | read |

### Email bodies (reading pane content)

**Email 1 — IT Support "Coffee Machine" (the punchline)**
```
From:    IT Support <itsupport@company.internal>
To:      Andrew Hannah
Subject: Re: Coffee Machine — URGENT
Date:    Today, 9:14 AM

Hi Andrew,

Thank you for your continued engagement with the IT helpdesk.

After careful review, we would like to remind you that the coffee
machine is not a supported system under our QA testing framework.

Specifically:
  • Bug #QA-0042 "Coffee too hot" — Cannot reproduce. Working as designed.
  • Bug #QA-0043 "Cup dispenser jammed" — Closed. User error.
  • Bug #QA-0044 "No oat milk" — Out of scope. Please see Facilities.
  • Bug #QA-0045 "Machine makes noise" — By design. It is a machine.

We have escalated your request to the Facilities team and have
updated your ticket to WONTFIX.

Please stop filing bug reports about the coffee machine.

Regards,
Derek W.
IT Support — Level 1
☎ Ext. 4001  |  📧 itsupport@company.internal

──────────────────────────────────────────
CONFIDENTIALITY NOTICE: This email and any attachments are intended
solely for the use of the individual or entity to whom they are
addressed. If you have received this email in error, please notify
the sender and delete it immediately. Do not forward to the coffee
machine.
──────────────────────────────────────────
```

**Email 2 — Elyse Hannah**
```
From:    Elyse Hannah <elyse.hannah@company.internal>
To:      QA Team
Subject: QA signoff — Case #4471

All acceptance criteria verified and signed off.
Case #4471 is clear for release.

— Elyse
Lead QA Tester
```

**Email 3 — GitHub notification** (standard style, no extra humour)
```
[QA-Pilot] Pull request #18 merged by andrewdhannah
Branch: sprint-g5 → main
View pull request: github.com/andrewdhannah/QA-Pilot/pull/18
```

**Emails 4–6** — short one-liners are fine, no reading pane content needed
(clicking them just shows a placeholder "No preview available" or similar).

---

## Interactions

- Clicking an email in the list loads its body in the reading pane
- Selected email gets `--ol-selected` background in the list
- Unread email loses its bold/blue styling when clicked (mark as read)
- Folder list items highlight on hover but clicking them does nothing
  (or shows "No items in this folder" in the email list — your choice)
- No actual send/reply functionality needed

---

## Definition of Done

- [ ] `QOUTLOOK_PAGE` string defined in `apps/browser.html`
- [ ] Registered as `"qoutlook"` in `INTERNAL_PAGES`
- [ ] Three-panel Outlook layout renders correctly inside the Browser iframe
- [ ] Topbar shows Outlook blue, wordmark, search bar, AH avatar
- [ ] All 6 emails appear in the list, Email 1 is visually unread (bold, blue accent)
- [ ] Clicking Email 1 loads the IT Support coffee machine reply in the reading pane
- [ ] Clicking Email 1 marks it as read (removes bold/accent)
- [ ] Clicking Email 2 loads Elyse's QA signoff in reading pane
- [ ] No external images, no CDN, no fetch() — fully self-contained string
- [ ] Works inside the Browser app iframe at file:// origin
- [ ] Typing `qoutlook` in the browser address bar loads the page correctly
