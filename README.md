# Nudgit

**Stop losing money to forgotten invoices.**

Nudgit sends perfectly timed, human-written invoice reminders so freelancers get paid — without the awkwardness of chasing.

→ **Live at [nudgeit.pro](https://nudgeit.pro)**

---

## The problem

Every freelancer knows this feeling: you sent the invoice, moved on, three months went by, and you realize you never got paid. Average freelancer loses **$4,200/year** to forgotten, unchased invoices.

## The fix

Nudgit sends reminders automatically — at exactly the right moments:
- **3 days before** due date — friendly heads-up
- **On the due date** — professional nudge
- **3 days overdue** — polite but clear
- **7 days overdue** — firm, you don't have to be

## Features

- Automated email reminders (friendly → firm, 4-step sequence)
- Email + SMS channels
- CSV bulk import — 100 invoices in one click
- Full dashboard — overdue, pending, paid
- Pre-written templates in 3 tones
- One-click mark as paid
- Stripe-powered checkout

## Pricing

| Plan | Price | Notes |
|------|-------|-------|
| Starter | $19/mo | 20 invoices, email only |
| **Pro — Founding** | **$9/mo** | **100 invoices, all channels. Locked for life.** |
| Agency | $89/mo | Unlimited, multi-client |

14-day free trial. No credit card required.

## Tech stack

- **Frontend:** Next.js 16, Tailwind CSS, TypeScript
- **Payments:** Stripe (subscriptions, checkout)
- **Database:** Supabase (PostgreSQL) — coming in v1.1
- **Email:** Resend — coming in v1.1
- **Deploy:** Vercel

## Getting started

```bash
git clone https://github.com/stevieray23/nudge.git
cd nudge
npm install
npm run dev
```

Copy `.env.example` to `.env.local` and fill in your Stripe keys.

## Status

Currently in early access. First 50 signups get founding member pricing ($9/mo locked for life).

## Contributing

PRs welcome. For major changes, open an issue first.

## License

MIT
