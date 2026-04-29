# Nudge — Launch Plan

**Last updated:** 2026-04-29
**Product:** Nudge — invoice reminder SaaS for freelancers
**Website:** https://nudgeit.pro (live ✅)
**Repo:** https://github.com/stevieray23/nudge ✅
**Stripe products:** Starter $19 / Pro $9 founding / Agency $89 ✅ (created 2026-04-29)
**Vercel deployment:** ✅ live at nudgeit.pro
**Domain:** nudgeit.pro ✅ (registered on Hostinger)

---

## Pre-Launch Checklist

### Product
- [x] Landing page built
- [x] Signup + plan picker with Stripe checkout
- [x] Confirmation page with confetti
- [x] Dashboard (mock, ready for Supabase)
- [x] Stripe products created (Starter $19, Pro $9 founding, Agency $89)
- [ ] Dev server restart (blocked — PID 50612 stuck on port 3000)
- [ ] Real Stripe test checkout verified
- [ ] Vercel deployment

### Positioning
- Name: **Nudge** — avoids Chase Bank trademark risk
- Hook: *"Stop losing money to forgotten invoices."*
- Founding offer: $9/mo locked for life, first 50 customers
- No CC required to start (14-day trial)

---

## Launch Channels

### 1. Product Hunt (Biggest impact)
**Why:** Consistent 100-500 signups for B2C/small business SaaS
**When:** Launch day (coordinator with IH and Reddit)

**Prep (do now):**
- [ ] Create PH maker account at producthunt.com
- [ ] Prepare launch post: headline + 3-sentence description + demo video/GIF
- [ ] Prepare "maker comment" for launch day (warm, personal)
- [ ] Schedule reminder to post at 00:01 PST (8am London)

**Launch post structure:**
```
Headline: Nudge — automated invoice reminders for freelancers
Tagline: Get paid without the awkwardness.

Description:
Chase sends perfectly timed, human-written invoice follow-ups so you stop losing money to forgotten payments — without having to be the one asking.
- No coding required
- Import invoices via CSV in one click
- Email + SMS reminders
- $9/mo founding price — locked for life

Demo: [GIF of dashboard or Loom video]
```

**After launch:**
- Reply to every comment within 1 hour
- Ask 5 friends to upvote + comment
- Post on Twitter with PH link

---

### 2. Indie Hackers (Builds credibility)
**Why:** Audience of builders + indie hackers, great for early feedback
**When:** 2-3 days BEFORE Product Hunt

**Post type:** "Show HN" / "I built this" story

**Structure:**
```
Title: I lost $4,200 last year to forgotten invoices — built Nudge so you don't have to

Body:
- The problem (relatable, specific number)
- Why existing tools don't work
- How Nudge solves it
- The tech stack (Next.js, Stripe, Supabase — if asked)
- What I need: honest feedback + early signups
- Link to waitlist/signup
```

---

### 3. Reddit — r/freelance + r/SideProject
**Why:** Target audience directly
**When:** Same day as PH launch

**r/freelance post (not spam — share the story):**
```
Title: I built a tool to stop freelancers losing money to forgotten invoices

Body:
"Just sharing since this community helped me so much early on.

I lost $4,200 last year to invoices I just... forgot to follow up on. It's embarrassing to admit but freelancers know this happens.

Built Nudge — it sends friendly, professional invoice reminders automatically. No awkward "just following up" emails from you.

Currently in early access, first 50 get $9/mo locked for life.

Would love honest feedback from people who actually send invoices — is this useful or am I missing something?

[link]"
```

**Rules to follow:**
- Genuine post, not spam
- Engage with every comment
- Don't post and disappear
- Post once, not multiple times

---

### 4. Twitter / X — Build in Public
**Why:** Long-term engine, not one-time blast
**When:** Start NOW, continue daily through launch

**Account setup (if not already):**
- Bio: "Building Nudge — automated invoice reminders for freelancers"
- pinned tweet: problem → solution → waitlist link

**Daily cadence:**
- 1 post about the problem (invoice chasing pain)
- 1 post about the build (what shipped)
- 1 post with a tip for freelancers
- Engagement: reply to invoice/finance/freelancer accounts daily

**Launch day:**
- Thread: "We just launched on Product Hunt. Here's the 48-hour story of building Nudge."
- Screenshot of first customers/signups
- Thank people who signed up

**Hashtags:** #buildinpublic #saas #freelance #startup

---

### 5. Cold Outreach
**Why:** High conversion, low competition
**When:** Start now, ongoing

**Targets:** Freelancers on Twitter, LinkedIn, in Reddit communities

**DM template:**
```
Hey [name] — I saw you're a [designer/developer/freelancer]. I built a small tool called Nudge that sends invoice reminders automatically so you stop losing money to forgotten payments.

Would love to send you a free founding member spot ($9/mo for life) if you're open to trying it out and giving honest feedback.
```

**Key:** Offer free access in exchange for feedback — not asking them to pay.

---

## Launch Timeline

| Day | Action |
|-----|--------|
| **Now** | Set up Vercel deployment, test Stripe checkout |
| **Now** | Set up domain (nudge.app or similar) |
| **Now** | Start Twitter build-in-public cadence |
| **Now** | Cold outreach to 10 freelancers |
| **-3 days** | Post on Indie Hackers |
| **-1 day** | Confirm PH launch time, prepare all assets |
| **Launch day** | Post on PH at 00:01 PST, Reddit, Twitter thread |
| **+1 day** | Follow up on all PH/IH/Reddit comments |
| **+3 days** | Email waitlist → push to paid conversion |
| **+7 days** | Review metrics: signups, conversions, feedback |

---

## Success Metrics

| Metric | Day 1 target | Day 7 target |
|--------|--------------|--------------|
| Waitlist signups | 50 | 200 |
| Paid customers | 2 | 10 |
| MRR | $18 | $90 |
| Product Hunt votes | 100 | 200 |
| IH upvotes | 20 | 50 |

**Decision:** If $0 MRR after 14 days → pivot or kill. If >5 paying customers → double down on traffic.

---

## Domain Options
- nudge.app (likely available, ~$12/yr)
- nudgehq.com (check)
- paidby.app (taken/available check)
- nudger.app (check)

---

## Vercel Deployment Steps
1. Connect repo: `https://github.com/stevieray23/nudge`
2. Add env vars from `.env.local` to Vercel dashboard
3. Deploy → get preview URL
4. Buy domain → point to Vercel
5. Set `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` in Vercel env vars

---

## Key Copy Assets

**Email subject lines (waitlist):**
- "You're on the list — here's what happens next"
- "Nudge is live. First 50 founding spots open."
- "One invoice. Three emails. Zero awkwardness."

**PH tagline:** "Get paid without the awkwardness."
**One-liner:** "Chase sends perfectly timed invoice reminders so freelancers stop losing money."
