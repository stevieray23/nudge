'use client'

import { useState } from 'react'
import Link from 'next/link'

// ─── Types ───────────────────────────────────────────────────────────────────

type ToastState = {
  show: boolean
  message: string
  type: 'success' | 'error'
}

// ─── Nav ───────────────────────────────────────────────────────────────────

function Nav() {
  return (
    <nav className="flex items-center justify-between px-8 py-5 border-b border-zinc-100/80 sticky top-0 z-50 bg-white/80 backdrop-blur-md">
      <Link href="/" className="flex items-center gap-2.5 group">
        <div className="w-8 h-8 bg-sky-500 rounded-xl flex items-center justify-center shadow-sm shadow-sky-200 group-hover:shadow-sky-300 transition-shadow">
          <span className="text-white font-bold text-sm">C</span>
        </div>
        <span className="font-semibold text-lg text-zinc-900 tracking-tight">Chase</span>
      </Link>
      <div className="flex items-center gap-5 text-sm text-zinc-500">
        <a href="#features" className="hover:text-zinc-900 transition-colors">Features</a>
        <a href="#pricing" className="hover:text-zinc-900 transition-colors">Pricing</a>
        <a href="/signup" className="bg-zinc-900 hover:bg-zinc-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          Get early access
        </a>
      </div>
    </nav>
  )
}

// ─── Hero ────────────────────────────────────────────────────────────────────

function Hero({ onJoinWaitlist }: { onJoinWaitlist: (e: React.FormEvent) => void }) {
  return (
    <section className="px-8 pt-16 pb-24 max-w-5xl mx-auto">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        {/* Left: Copy */}
        <div>
          <div className="inline-flex items-center gap-2 bg-sky-50 text-sky-600 px-4 py-1.5 rounded-full text-xs font-medium mb-8 border border-sky-100">
            <span className="w-1.5 h-1.5 bg-sky-400 rounded-full" />
            Founding Member price — $9/mo · Limited spots
          </div>

          <h1 className="text-5xl md:text-6xl font-semibold text-zinc-900 tracking-tight leading-[1.08] mb-5">
            Never chase<br />
            an invoice again.
          </h1>

          <p className="text-lg text-zinc-500 mb-8 leading-relaxed">
            Chase automates your invoice follow-ups so you stop losing money to forgotten payments — without the awkwardness of being the one who "just follows up."
          </p>

          <form onSubmit={onJoinWaitlist} className="flex flex-col sm:flex-row gap-3 mb-4">
            <input
              type="email"
              placeholder="you@yourbusiness.com"
              required
              className="flex-1 px-4 py-3.5 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent placeholder-zinc-400 bg-white"
            />
            <button
              type="submit"
              className="bg-sky-500 hover:bg-sky-600 active:translate-y-[1px] text-white px-6 py-3.5 rounded-xl text-sm font-semibold transition-all whitespace-nowrap shadow-sm shadow-sky-200"
            >
              Get early access →
            </button>
          </form>

          <div className="flex items-center gap-3 text-xs text-zinc-400">
            <div className="flex -space-x-2">
              {['https://picsum.photos/seed/u1/32/32', 'https://picsum.photos/seed/u2/32/32', 'https://picsum.photos/seed/u3/32/32'].map((src, i) => (
                <img key={i} src={src} className="w-7 h-7 rounded-full border-2 border-white object-cover" alt="" />
              ))}
            </div>
            <span>147 freelancers already waiting</span>
          </div>
        </div>

        {/* Right: Dashboard preview */}
        <div className="relative">
          <div className="bg-zinc-50 border border-zinc-200 rounded-2xl p-5 shadow-2xl shadow-zinc-200/60">
            {/* Window chrome */}
            <div className="flex items-center gap-2 mb-5">
              <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
              <span className="ml-3 text-xs text-zinc-400 font-mono">chase.app</span>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              {[
                { label: 'Outstanding', value: '$8,450', sub: '+12% this week', color: 'text-zinc-900' },
                { label: 'Overdue', value: '6', sub: '⚠ 2 new today', color: 'text-red-500' },
                { label: 'Paid (Apr)', value: '$12,300', sub: '+8% vs Mar', color: 'text-emerald-600' },
              ].map((card) => (
                <div key={card.label} className="bg-white rounded-xl p-3.5 border border-zinc-100">
                  <p className="text-[11px] text-zinc-400 mb-1 font-medium">{card.label}</p>
                  <p className={`text-xl font-semibold ${card.color}`}>{card.value}</p>
                  <p className="text-[10px] text-zinc-400 mt-0.5">{card.sub}</p>
                </div>
              ))}
            </div>

            {/* Invoice list */}
            <div className="bg-white rounded-xl border border-zinc-100 overflow-hidden">
              <div className="px-4 py-2.5 bg-zinc-50 border-b border-zinc-100 flex items-center justify-between">
                <span className="text-[11px] font-medium text-zinc-500 uppercase tracking-wider">Recent invoices</span>
                <span className="text-[11px] text-sky-500 font-medium cursor-pointer">+ Add</span>
              </div>
              {[
                { client: 'Meridian Design Co.', amount: '$2,100', due: 'Apr 22', status: 'Overdue', statusClass: 'bg-red-50 text-red-600 border-red-100' },
                { client: 'Harlow Photography', amount: '$850', due: 'Apr 29', status: 'Pending', statusClass: 'bg-zinc-50 text-zinc-500 border-zinc-100' },
                { client: 'CoreTech Solutions', amount: '$4,200', due: 'May 3', status: 'Pending', statusClass: 'bg-zinc-50 text-zinc-500 border-zinc-100' },
              ].map((row) => (
                <div key={row.client} className="px-4 py-3 flex items-center justify-between border-b border-zinc-50 last:border-0 hover:bg-zinc-50 transition-colors">
                  <div>
                    <p className="text-xs font-medium text-zinc-700">{row.client}</p>
                    <p className="text-[11px] text-zinc-400">Due {row.due}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-zinc-600">{row.amount}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${row.statusClass}`}>{row.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Floating badge */}
          <div className="absolute -bottom-4 -right-4 bg-white border border-zinc-200 rounded-xl px-3.5 py-2.5 shadow-lg shadow-zinc-200/40 flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs text-zinc-600 font-medium">Reminder sent</span>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Problem ─────────────────────────────────────────────────────────────────

function Problem() {
  return (
    <section className="bg-zinc-900 text-white px-8 py-20">
      <div className="max-w-5xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16">
          <div>
            <p className="text-sky-400 text-xs font-semibold uppercase tracking-widest mb-4">The problem</p>
            <h2 className="text-3xl md:text-4xl font-semibold mb-5 tracking-tight leading-tight">
              You sent the invoice. Then life happened.
            </h2>
            <p className="text-zinc-400 text-base leading-relaxed mb-8">
              Three months go by. You realise you never got paid. The client has moved on, the project is archived, and the money is just... gone. This happens to freelancers constantly. Chase makes sure it never happens again.
            </p>
            <div className="space-y-3">
              {[
                { emoji: '😬', title: 'Forgot to follow up', desc: 'You sent the invoice and moved on. No system. No reminders. It dies in the inbox.' },
                { emoji: '😩', title: 'Feels awkward', desc: 'You hate being "that person" who keeps chasing. So you delay. And delay. Until it\'s too late.' },
                { emoji: '😓', title: 'No visibility', desc: 'You don\'t know what\'s overdue, what\'s been seen, or what\'s paid. Everything lives in your head.' },
              ].map((item) => (
                <div key={item.title} className="flex items-start gap-3 bg-zinc-800 rounded-xl p-4">
                  <span className="text-xl mt-0.5">{item.emoji}</span>
                  <div>
                    <p className="font-medium text-sm text-white">{item.title}</p>
                    <p className="text-zinc-400 text-xs mt-0.5 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center">
            <div className="bg-zinc-800 rounded-2xl p-6 w-full border border-zinc-700">
              <p className="text-xs text-zinc-400 font-medium uppercase tracking-widest mb-4">The solution</p>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-sky-500/20 border border-sky-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sky-400 text-xs font-bold">✓</span>
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">Chase sends the first reminder for you</p>
                    <p className="text-zinc-400 text-xs mt-0.5">3 days before due date — friendly, professional. You don\'t touch anything.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-sky-500/20 border border-sky-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sky-400 text-xs font-bold">✓</span>
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">If ignored, Chase follows up</p>
                    <p className="text-zinc-400 text-xs mt-0.5">3 days after due date — polite but clear. Still professional. Not aggressive.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full bg-sky-500/20 border border-sky-500/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sky-400 text-xs font-bold">✓</span>
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">You get full visibility at all times</p>
                    <p className="text-zinc-400 text-xs mt-0.5">Dashboard shows every invoice: seen, pending, paid, overdue. No surprises.</p>
                  </div>
                </div>
              </div>
              <div className="mt-5 pt-4 border-t border-zinc-700">
                <p className="text-xs text-zinc-500">Average freelancer loses</p>
                <p className="text-3xl font-bold text-white mt-1">$4,200<span className="text-lg text-zinc-400 font-normal">/year</span></p>
                <p className="text-xs text-zinc-500 mt-1">to forgotten, unchased invoices. Chase fixes that.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── How it works ────────────────────────────────────────────────────────────

function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Add your invoice',
      desc: 'Enter client name, email, amount, and due date. Or import 100 at once via CSV. Takes about 30 seconds.',
    },
    {
      num: '02',
      title: 'Pick your sequence',
      desc: 'Choose a reminder template — friendly, professional, or firm. We\'ve written the copy. You just pick the tone.',
    },
    {
      num: '03',
      title: 'Chase handles the rest',
      desc: 'Emails go out on time, every time. You get notified on each step. Mark as paid with one click when the money arrives.',
    },
  ]

  return (
    <section id="features" className="px-8 py-20 max-w-5xl mx-auto">
      <div className="text-center mb-14">
        <p className="text-sky-500 text-xs font-semibold uppercase tracking-widest mb-3">How it works</p>
        <h2 className="text-3xl md:text-4xl font-semibold text-zinc-900 tracking-tight">Up and running in 5 minutes.</h2>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {steps.map((step, i) => (
          <div key={step.num} className="relative border border-zinc-200 rounded-2xl p-6 hover:border-sky-200 hover:shadow-xl hover:shadow-sky-100/50 transition-all duration-300">
            <div className="text-5xl font-bold text-zinc-100 mb-4">{step.num}</div>
            <h3 className="font-semibold text-zinc-900 mb-2">{step.title}</h3>
            <p className="text-zinc-500 text-sm leading-relaxed">{step.desc}</p>
            {i < steps.length - 1 && (
              <div className="hidden md:block absolute -right-2.5 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-white border border-zinc-200 flex items-center justify-center">
                <svg className="w-2.5 h-2.5 text-zinc-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── Features ───────────────────────────────────────────────────────────────

function Features() {
  const features = [
    { title: 'Human-written copy', desc: 'Reminders sound like a professional colleague — never desperate, never passive. You control the tone.', icon: '✍' },
    { title: 'Smart timing', desc: 'Chase sends emails at exactly the right moments. Friendly before, firm after. No manual work required.', icon: '⏰' },
    { title: 'Full visibility dashboard', desc: 'Every invoice, every status, every action taken. See who\'s seen your invoice and who\'s ignoring it.', icon: '◉' },
    { title: 'CSV bulk import', desc: 'Have a backlog of old invoices? Import 100 at once. One click and every one starts getting chased.', icon: '⇪' },
    { title: 'One-click mark paid', desc: 'Client pays via bank transfer? Mark it done. No more accidental follow-ups to people who already paid.', icon: '✓' },
    { title: 'Email + SMS channels', desc: 'Some clients never open email. Chase supports SMS reminders too — reach them wherever they actually are.', icon: '◎' },
  ]

  return (
    <section className="bg-zinc-50 px-8 py-20">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-14">
          <p className="text-sky-500 text-xs font-semibold uppercase tracking-widest mb-3">Features</p>
          <h2 className="text-3xl md:text-4xl font-semibold text-zinc-900 tracking-tight">Everything you need. Nothing you don't.</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div key={f.title} className="bg-white rounded-2xl p-5 border border-zinc-100 hover:shadow-lg hover:border-zinc-200 transition-all">
              <div className="text-2xl text-sky-500 mb-3 font-light">{f.icon}</div>
              <h3 className="font-semibold text-zinc-900 text-sm mb-1">{f.title}</h3>
              <p className="text-zinc-500 text-xs leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Pricing ─────────────────────────────────────────────────────────────────

function Pricing({ onJoinWaitlist }: { onJoinWaitlist: (e: React.FormEvent) => void }) {
  const plans = [
    {
      name: 'Starter',
      badge: null,
      price: '$19',
      period: '/month',
      desc: 'For freelancers getting started with invoicing.',
      features: ['20 invoices/month', 'Up to 3 reminders per invoice', 'Email reminders', 'CSV import', 'Basic dashboard'],
      cta: 'Start free trial',
    },
    {
      name: 'Pro',
      badge: 'Founding price',
      price: '$9',
      period: '/month',
      desc: 'For freelancers serious about getting paid. Launch price — locks in forever.',
      features: ['100 invoices/month', 'Unlimited reminders', 'Email + SMS reminders', 'CSV import', 'Full dashboard', 'Custom sequences', 'Priority support'],
      cta: 'Get founding access',
      highlight: true,
    },
    {
      name: 'Agency',
      badge: null,
      price: '$89',
      period: '/month',
      desc: 'For agencies managing multiple clients and contractors.',
      features: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS + Slack', 'CSV import', 'Full dashboard', 'Multi-client view', 'Advanced sequences', 'Dedicated support'],
      cta: 'Contact us',
    },
  ]

  return (
    <section id="pricing" className="px-8 py-20 max-w-5xl mx-auto">
      <div className="text-center mb-14">
        <p className="text-sky-500 text-xs font-semibold uppercase tracking-widest mb-3">Pricing</p>
        <h2 className="text-3xl md:text-4xl font-semibold text-zinc-900 tracking-tight">Simple pricing. No surprises.</h2>
        <p className="text-zinc-500 mt-3 text-sm">14-day free trial on all plans. Cancel anytime.</p>
      </div>
      <div className="grid md:grid-cols-3 gap-5 items-start">
        {plans.map((plan) => (
          <div key={plan.name} className={`rounded-2xl p-6 border ${plan.highlight ? 'border-sky-300 bg-sky-50 shadow-xl shadow-sky-100/50 relative' : 'border-zinc-200 bg-white'}`}>
            {plan.badge && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-sky-500 text-white text-[11px] font-semibold px-3 py-1 rounded-full">{plan.badge}</span>
              </div>
            )}
            <div className="mt-2 mb-1">
              <h3 className="font-semibold text-zinc-900">{plan.name}</h3>
              <p className="text-zinc-500 text-xs mt-0.5">{plan.desc}</p>
            </div>
            <div className="flex items-end gap-1 mb-5">
              <span className="text-4xl font-bold text-zinc-900">{plan.price}</span>
              <span className="text-zinc-400 text-sm mb-1">{plan.period}</span>
            </div>
            <ul className="space-y-2 mb-5">
              {plan.features.map((f) => (
                <li key={f} className="flex items-center gap-2 text-xs text-zinc-600">
                  <svg className="w-3.5 h-3.5 text-sky-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                  {f}
                </li>
              ))}
            </ul>
            <button
              onClick={onJoinWaitlist}
              className={`w-full py-3 rounded-xl text-sm font-semibold transition-all ${plan.highlight ? 'bg-sky-500 hover:bg-sky-600 active:translate-y-[1px] text-white shadow-sm shadow-sky-200' : 'bg-zinc-900 hover:bg-zinc-800 active:translate-y-[1px] text-white'}`}
            >
              {plan.cta}
            </button>
          </div>
        ))}
      </div>
      <p className="text-center text-xs text-zinc-400 mt-6">Pro founding price locked for life. Upgrades, downgrades, or cancellations at any time.</p>
    </section>
  )
}

// ─── Testimonials ─────────────────────────────────────────────────────────────

function Testimonials() {
  const quotes = [
    {
      text: "I had $3,400 in unpaid invoices sitting in my inbox. Chase got me paid on all of them within two weeks. Can't believe I didn't have this sooner.",
      name: 'Daniela R.',
      role: 'Brand designer, freelance',
    },
    {
      text: "The awkwardness of chasing money was costing me real money. Chase handles it so professionally I don't even think about it anymore.",
      name: 'Marcus T.',
      role: 'Web developer, 3 years freelance',
    },
    {
      text: "I set up 20 overdue invoices in 10 minutes using the CSV import. By the end of the week, 18 of them were paid. Absolutely worth it.",
      name: 'Sofia M.',
      role: 'Photographer, small business',
    },
  ]

  return (
    <section className="px-8 py-20 max-w-5xl mx-auto">
      <div className="text-center mb-12">
        <p className="text-sky-500 text-xs font-semibold uppercase tracking-widest mb-3">Early feedback</p>
        <h2 className="text-3xl md:text-4xl font-semibold text-zinc-900 tracking-tight">People are already getting paid.</h2>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {quotes.map((q) => (
          <div key={q.name} className="bg-zinc-50 rounded-2xl p-6 border border-zinc-100">
            <div className="text-sky-400 text-2xl mb-3 leading-none">"</div>
            <p className="text-zinc-700 text-sm leading-relaxed mb-4">{q.text}</p>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-zinc-200 flex items-center justify-center text-zinc-600 text-xs font-semibold">
                {q.name.charAt(0)}
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-900">{q.name}</p>
                <p className="text-xs text-zinc-400">{q.role}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── FAQ ─────────────────────────────────────────────────────────────────────

function FAQ() {
  const [open, setOpen] = useState<number | null>(null)
  const faqs = [
    { q: 'How does Chase send emails on my behalf?', a: 'Chase uses your connected email address to send reminders. Clients see the email coming from you — Chase just handles the timing, content, and tracking. You stay in full control.' },
    { q: 'What if a client pays but I forget to mark it?', a: 'Chase detects email replies and can automatically mark invoices as paid when a client confirms payment in the thread. You can also mark invoices paid manually with one click.' },
    { q: 'Can I customise the reminder messages?', a: 'Yes. Start with our pre-built templates across three tones — Friendly, Professional, or Firm. Or write your own from scratch. Every word is yours to control.' },
    { q: 'When does the 14-day trial start?', a: 'Your trial starts when you create your account. No credit card required to start. After 14 days you can subscribe or your account pauses — nothing charged automatically.' },
    { q: 'What happens to my invoices if I cancel?', a: 'Your data stays yours. You can export all invoices at any time before cancelling. After cancellation your account moves to a read-only state.' },
  ]

  return (
    <section id="faq" className="bg-zinc-50 px-8 py-20">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-sky-500 text-xs font-semibold uppercase tracking-widest mb-3">FAQ</p>
          <h2 className="text-3xl md:text-4xl font-semibold text-zinc-900 tracking-tight">Common questions</h2>
        </div>
        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <div key={i} className="bg-white rounded-xl border border-zinc-200 overflow-hidden">
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-zinc-50 transition-colors"
              >
                <span className="font-medium text-sm text-zinc-900">{faq.q}</span>
                <svg className={`w-4 h-4 text-zinc-400 transition-transform ${open === i ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {open === i && (
                <div className="px-5 pb-4">
                  <p className="text-zinc-500 text-sm leading-relaxed">{faq.a}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── CTA ─────────────────────────────────────────────────────────────────────

function CTA({ onJoinWaitlist }: { onJoinWaitlist: (e: React.FormEvent) => void }) {
  return (
    <section className="px-8 py-20 bg-zinc-900 text-white">
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tight mb-4">Stop losing money to forgotten invoices.</h2>
        <p className="text-zinc-400 text-base mb-2">Founding Member pricing — $9/mo for life.</p>
        <p className="text-zinc-500 text-sm mb-8">First 50 signups only. 14-day free trial. No credit card required.</p>
        <form onSubmit={onJoinWaitlist} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto mb-4">
          <input
            type="email"
            placeholder="you@yourbusiness.com"
            required
            className="flex-1 px-4 py-3.5 bg-zinc-800 border border-zinc-700 rounded-xl text-sm text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-sky-400"
          />
          <button
            type="submit"
            className="bg-sky-500 hover:bg-sky-600 active:translate-y-[1px] text-white px-6 py-3.5 rounded-xl text-sm font-semibold transition-all shadow-sm shadow-sky-500/30 whitespace-nowrap"
          >
            Get early access →
          </button>
        </form>
        <p className="text-xs text-zinc-600">No spam. Unsubscribe anytime. We don't share your email.</p>
      </div>
    </section>
  )
}

// ─── Footer ──────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="px-8 py-8 border-t border-zinc-100 flex items-center justify-between text-xs text-zinc-400">
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 bg-sky-500 rounded-md flex items-center justify-center">
          <span className="text-white font-bold text-[10px]">C</span>
        </div>
        <span>© 2026 Chase</span>
      </div>
      <div className="flex items-center gap-4">
        <a href="#" className="hover:text-zinc-600 transition-colors">Privacy</a>
        <a href="#" className="hover:text-zinc-600 transition-colors">Terms</a>
        <a href="mailto:hello@chase.app" className="hover:text-zinc-600 transition-colors">Contact</a>
      </div>
    </footer>
  )
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [toast, setToast] = useState<ToastState>({ show: false, message: '', type: 'success' })

  function showToast(message: string, type: 'success' | 'error' = 'success') {
    setToast({ show: true, message, type })
    setTimeout(() => setToast(t => ({ ...t, show: false })), 4000)
  }

  function handleJoinWaitlist(e: React.FormEvent) {
    e.preventDefault()
    const form = e.currentTarget as HTMLFormElement
    const email = (form.elements.namedItem('email') as HTMLInputElement)?.value ?? ''
    if (!email) return
    // Simulate waitlist signup — redirect to signup page
    window.location.href = `/signup?email=${encodeURIComponent(email)}`
  }

  return (
    <div className="min-h-screen bg-white">
      <Nav />
      <Hero onJoinWaitlist={handleJoinWaitlist} />
      <Problem />
      <HowItWorks />
      <Features />
      <Testimonials />
      <Pricing onJoinWaitlist={handleJoinWaitlist} />
      <FAQ />
      <CTA onJoinWaitlist={handleJoinWaitlist} />
      <Footer />
      {toast.show && (
        <div className={`fixed bottom-6 right-6 px-5 py-3.5 rounded-xl shadow-xl text-sm font-medium flex items-center gap-2.5 transition-all duration-300 ${toast.type === 'success' ? 'bg-zinc-900 text-white' : 'bg-red-500 text-white'}`}>
          <span>{toast.type === 'success' ? '✓' : '✗'}</span>
          {toast.message}
        </div>
      )}
    </div>
  )
}