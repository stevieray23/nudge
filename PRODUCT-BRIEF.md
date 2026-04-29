# Chase — Product Brief v1.0
**Status:** Draft | **Date:** 2026-04-28 | **Author:** Clawbert (Co-CEO)

---

## Problem Statement

> Freelancers and small service businesses lose thousands of dollars per year simply because they forget to follow up on unpaid invoices. Current tools either charge too much, require too much setup, or feel too corporate for a one-person operation. They need something that works in five minutes, sends reminders automatically, and gets them paid — without the awkwardness of chasing money manually.

---

## Target User

**Primary persona:** Sam
- Solo freelancer or small service business (1-5 people)
- Sends 5–20 invoices/month
- Uses Wave, QuickBooks, FreshBooks, or even just a spreadsheet
- Usually forgets to follow up until the client ghosts them
- Hates confrontation and finds chasing money "awkward"
- Has lost $2K–$10K in unpaid invoices this year alone

**Secondary:** Small agency owner (1–3 people), consultant, tutor, trainer, cleaner, handyman, photographer

---

## Core Job-to-be-Done

> "I need to get paid on time without having to think about it, without looking like I'm desperate, and without spending hours following up manually."

**Current workaround:**
- Sticky notes / task manager reminders (unreliable)
- WhatsApp/Text from personal phone (unprofessional)
- Email sent manually (forgotten)
- Doing nothing and losing money

---

## Top 3 Pain Points

1. **Forgetting to follow up** — they send the invoice and move on. No system. No reminders. The invoice dies in the client's inbox.
2. **Awkwardness of chasing** — they feel like they're "bothering" clients. Nobody wants to be "that person" who keeps asking for money.
3. **No visibility** — they don't know which invoices are paid, overdue, or forgotten. Everything lives in their email or head.

---

## Product Concept: Chase

**What it does:**
- Import or create invoices with client name, amount, due date, and email
- Set a reminder sequence (e.g., "3 days before due date → friendly reminder, 3 days after → polite nudge, 7 days after → firm notice")
- Chase sends perfectly timed, human-written emails and SMS on your behalf
- You see everything in a clean dashboard: paid, pending, overdue

**Differentiator:** It feels like having a professional accounts receivable assistant — not software. The copy is warm, confident, never desperate.

---

## Pricing

| Plan | Price | Invoices/mo | Reminders | Channels |
|------|-------|-------------|------------|----------|
| Starter | $19/mo | 20 | 3 per invoice | Email only |
| Pro | $39/mo | 100 | Unlimited | Email + SMS |
| Agency | $89/mo | Unlimited | Unlimited | Email + SMS + Slack |

**Trial:** 14 days free, no credit card required

---

## MVP Scope (Ship in 2–3 weeks)

### Must-Have
1. Add invoice manually (client name, email, amount, due date)
2. Import multiple invoices via CSV
3. Set reminder sequence (template-based, pre-built)
4. Send email reminders via sequence
5. Dashboard: see all invoices, their status (pending/sent/paid/overdue)
6. Mark invoice as paid manually
7. Basic overdue highlighting

### Should-Have (Post-MVP)
- SMS reminders
- Two-way email threading (replies go to inbox)
- Client portal with payment link
- Analytics (average days to payment, payment rate %)

### Won't Have (V1)
- Actual payment processing
- Full accounting integration
- Multi-user / team support

---

## Tech Stack (MVP)

| Layer | Choice |
|-------|--------|
| Frontend | Next.js + Tailwind CSS |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth |
| Email | Loops or Resend |
| SMS | Twilio |
| Deployment | Vercel |
| Payment | Stripe (future) |

**Why this stack:** Fast to build, cheap to run, scales. Loops/Resend for email means deliverability is handled without managing SMTP. Supabase handles auth + DB in one. Total MVP infra cost: ~$50/month.

---

## Build Roadmap

### Week 1: Foundation
- [ ] Project setup (Next.js + Tailwind + Supabase)
- [ ] Auth (sign up / log in / onboarding)
- [ ] Invoice database schema
- [ ] Add invoice UI (single + CSV import)
- [ ] Invoice list dashboard

### Week 2: Core Loop
- [ ] Reminder sequence engine (rule-based: days X → send Y)
- [ ] Email template system (3 pre-built templates)
- [ ] Resend/Loops integration
- [ ] Cron job / scheduled function to trigger reminders
- [ ] Status tracking (pending → sent → viewed → paid → overdue)

### Week 3: Polish + Launch
- [ ] Dashboard: filter by status, sort by due date, overdue highlight
- [ ] Mark as paid action
- [ ] Email delivery confirmation
- [ ] Onboarding flow (add first invoice, set first sequence)
- [ ] Landing page (ChaseHQ.com — simple, one page)
- [ ] Sign up, login, pricing page
- [ ] Stripe subscription (Starter/Pro)

---

## Launch Plan

**Target:** Ship MVP and start taking signups in 3 weeks

### Channels (Launch Week)
1. **Product Hunt** — launch day. One clear hook: "Stop losing money to forgotten invoices."
2. **Indie Hackers** — post the story, not just the product
3. **r/freelance** — genuine post about the problem, not spam
4. **r/SideProject** — share the build journey
5. **Twitter/X** — short-form posts about the problem, build in public
6. **Cold DM** — DM 50 freelancers in relevant communities with a waitlist link

### Waitlist Mechanics
- Landing page with email capture
- Goal: 200 signups before launch
- Incentive: 50% lifetime discount for first 50 signups

### Validation Criteria
- $500 MRR in 30 days post-launch = green light
- 0 MRR in 60 days = pivot or kill

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Waitlist signups | 200 in 3 weeks |
| Paid customers (M1) | 10 |
| MRR (M1) | $190 |
| Email open rate | >40% |
| Trial → Paid conversion | >15% |
| Churn (M3) | <5% |

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Email deliverability bad | Medium | Use Resend/Loops (trusted IPs), warm up domain |
| Users don't import invoices | High | Make CSV dead simple, show preview before send |
| Too much friction in onboarding | High | 3-step max to first reminder sent |
| SMS cost eats margin | Low | Build in SMS cost, don't undercut |
| Competition copies fast | Medium | Build the brand/personality first |

---

## Voice & Tone (Chase's Personality)

Chase is:
- ✅ Calm, professional, never desperate
- ✅ Friendly but firm — like a trusted colleague who handles awkward conversations for you
- ✅ Confident — the reminder is professional, not apologetic

Chase is NOT:
- ❌ Smarmy or salesy
- ❌ Formal or corporate
- ❌ Passive ("just a reminder...")
- ❌ Aggressive or threatening

**Example reminder email:**
> **Subject:** Invoice #1042 — let's wrap this up
>
> Hi Sarah,
>
> Just a heads-up: your invoice for $850 is 5 days overdue. No stress — things slip through the cracks.
>
> Here's the link to view and pay: [link]
>
> Happy to answer any questions.
> — Tom

---