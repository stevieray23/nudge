'use client'

import { useState } from 'react'
import Link from 'next/link'

// ─── Types ───────────────────────────────────────────────────────────────────

type ToastState = { show: boolean; message: string }

// ─── Nav ───────────────────────────────────────────────────────────────────

function Nav() {
  return (
    <nav className="sticky top-0 z-50 bg-[#FFFBF5]/90 backdrop-blur-md border-b border-[#E5E7EB]">
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between h-16">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <img src="/logo.png" alt="Nudgit" className="h-9 w-auto object-contain" />
          <span className="font-semibold text-[#18181B] text-lg tracking-tight">Nudgit</span>
        </Link>
        {/* Right */}
        <div className="flex items-center gap-5 text-sm">
          <a href="#features" className="text-[#64748B] hover:text-[#18181B] transition-colors">Features</a>
          <a href="#pricing" className="text-[#64748B] hover:text-[#18181B] transition-colors">Pricing</a>
          <Link href="/login" className="text-[#64748B] hover:text-[#18181B] transition-colors font-medium">Log in</Link>
          <Link href="/signup" className="bg-[#18181B] hover:bg-[#27272A] text-white px-4 py-2 rounded-lg font-semibold text-sm transition-colors">
            Start free trial
          </Link>
        </div>
      </div>
    </nav>
  )
}

// ─── Hero ────────────────────────────────────────────────────────────────────

function Hero({ onJoin }: { onJoin: (e: React.FormEvent) => void }) {
  return (
    <section className="px-6 pt-14 pb-20 max-w-6xl mx-auto">
      <div className="grid lg:grid-cols-2 gap-16 items-center">

        {/* Left: Copy */}
        <div>
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-[#FEF3C7] border border-[#FDE68A] text-[#D97706] px-4 py-1.5 rounded-full text-xs font-semibold mb-8">
            <span className="w-1.5 h-1.5 bg-[#F59E0B] rounded-full animate-pulse" />
            Founding Member price — $9/mo · Limited to first 50
          </div>

          <h1 className="text-5xl md:text-6xl font-extrabold text-[#18181B] tracking-tight leading-[1.06] mb-5">
            Stop losing<br />
            <span className="text-[#F59E0B]">money to forgotten</span><br />
            invoices.
          </h1>

          <p className="text-lg text-[#64748B] leading-relaxed mb-9 max-w-lg">
            Nudgit sends perfectly timed invoice follow-ups — so you get paid without the awkwardness of chasing. Friendly before. Firm after. Never awkward.
          </p>

          {/* Social proof numbers */}
          <div className="flex items-center gap-6 mb-8">
            {[
              { num: '$4,200', label: 'avg. lost/year to forgotten invoices' },
              { num: '< 5min', label: 'to set up your first nudge' },
            ].map((s) => (
              <div key={s.num} className="flex items-start gap-2">
                <span className="text-[#F59E0B] font-extrabold text-2xl">{s.num}</span>
                <span className="text-[#64748B] text-sm leading-tight">{s.label}</span>
              </div>
            ))}
          </div>

          <form onSubmit={onJoin} className="flex flex-col sm:flex-row gap-3 mb-5">
            <input
              type="email"
              name="email"
              placeholder="you@yourbusiness.com"
              required
              className="flex-1 px-4 py-3.5 border border-[#E5E7EB] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#F59E0B] focus:border-transparent placeholder-[#94A3B8] bg-white"
            />
            <button
              type="submit"
              className="bg-[#F59E0B] hover:bg-[#D97706] active:scale-[0.98] text-white px-6 py-3.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-amber-200 whitespace-nowrap"
            >
              Get started free →
            </button>
          </form>

          <div className="flex items-center gap-3 text-xs text-[#94A3B8]">
            <div className="flex -space-x-2">
              {['u1', 'u2', 'u3'].map((s) => (
                <img key={s} src={`https://picsum.photos/seed/${s}/32/32`} className="w-7 h-7 rounded-full border-2 border-[#FFFBF5] object-cover" alt="" />
              ))}
            </div>
            <span>147 freelancers already signed up</span>
          </div>
        </div>

        {/* Right: Dashboard preview */}
        <div className="relative">
          {/* Ambient glow */}
          <div className="absolute -inset-8 bg-gradient-to-br from-[#FEF3C7] via-transparent to-[#F59E0B]/10 rounded-full blur-3xl opacity-60" />

          <div className="relative bg-white rounded-2xl border border-[#E5E7EB] shadow-2xl overflow-hidden">
            {/* Title bar */}
            <div className="bg-[#F9FAFB] border-b border-[#E5E7EB] px-5 py-3.5 flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-[#EF4444]" />
              <div className="w-2.5 h-2.5 rounded-full bg-[#FBBF24]" />
              <div className="w-2.5 h-2.5 rounded-full bg-[#34D399]" />
              <span className="ml-3 text-[10px] text-[#94A3B8] font-mono">nudgit.app/dashboard</span>
            </div>

            {/* Dashboard content */}
            <div className="p-5">
              {/* Stats row */}
              <div className="grid grid-cols-3 gap-3 mb-4">
                {[
                  { label: 'Outstanding', value: '$8,450', sub: '+12% this week', color: 'text-[#18181B]' },
                  { label: 'Overdue', value: '6 ⚠', sub: '2 new today', color: 'text-[#EF4444]' },
                  { label: 'Paid (Apr)', value: '$12,300', sub: '+8% vs Mar', color: 'text-[#10B981]' },
                ].map((c) => (
                  <div key={c.label} className="bg-[#F9FAFB] rounded-xl p-3.5 border border-[#E5E7EB]">
                    <p className="text-[11px] text-[#94A3B8] font-medium mb-1">{c.label}</p>
                    <p className={`text-xl font-bold ${c.color}`}>{c.value}</p>
                    <p className="text-[10px] text-[#94A3B8] mt-0.5">{c.sub}</p>
                  </div>
                ))}
              </div>

              {/* Invoice list */}
              <div className="rounded-xl border border-[#E5E7EB] overflow-hidden">
                <div className="bg-[#F9FAFB] px-4 py-2.5 border-b border-[#E5E7EB] flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-[#64748B] uppercase tracking-wider">Recent invoices</span>
                  <span className="text-[11px] text-[#F59E0B] font-semibold cursor-pointer hover:text-[#D97706]">+ Add</span>
                </div>
                {[
                  { client: 'Meridian Design Co.', amount: '$2,100', due: 'Apr 22', status: 'Overdue', statusBg: 'bg-[#FEE2E2]', statusFg: 'text-[#DC2626]' },
                  { client: 'Harlow Photography', amount: '$850', due: 'Apr 29', status: 'Pending', statusBg: 'bg-[#F3F4F6]', statusFg: 'text-[#6B7280]' },
                  { client: 'CoreTech Solutions', amount: '$4,200', due: 'May 3', status: 'Pending', statusBg: 'bg-[#F3F4F6]', statusFg: 'text-[#6B7280]' },
                  { client: 'Bloom Wellness', amount: '$1,300', due: 'Apr 18', status: 'Paid ✓', statusBg: 'bg-[#DCFCE7]', statusFg: 'text-[#16A34A]' },
                ].map((row, i) => (
                  <div key={row.client} className={`px-4 py-3 flex items-center justify-between ${i % 2 === 0 ? 'bg-white' : 'bg-[#FAFAFA]'}`}>
                    <div>
                      <p className="text-xs font-semibold text-[#18181B]">{row.client}</p>
                      <p className="text-[11px] text-[#94A3B8]">Due {row.due}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-[#64748B]">{row.amount}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${row.statusBg} ${row.statusFg}`}>{row.status}</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Nudge sent indicator */}
              <div className="mt-3 flex items-center gap-2 text-[10px] text-[#94A3B8]">
                <div className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                Reminder sent to Meridian Design Co. — 2 days ago
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Problem ─────────────────────────────────────────────────────────────────

function Problem() {
  return (
    <section className="bg-[#18181B] text-white px-6 py-20">
      <div className="max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-16">
          <div>
            <p className="text-[#F59E0B] text-xs font-bold uppercase tracking-widest mb-4">The problem</p>
            <h2 className="text-3xl md:text-4xl font-bold mb-5 tracking-tight leading-tight">
              You sent the invoice.<br />Then life happened.
            </h2>
            <p className="text-[#71717A] leading-relaxed mb-8">
              Three months go by. You realise you never got paid. The client has moved on, the project is archived, and the money is just... gone. This happens to freelancers constantly.
            </p>
            <div className="space-y-3">
              {[
                { emoji: '😬', title: 'Forgot to follow up', desc: "You sent the invoice and moved on. No system. No reminders. It dies in the client's inbox." },
                { emoji: '😩', title: 'Feels awkward', desc: "You hate being 'that person' who keeps chasing. So you delay. And delay. Until it's too late." },
                { emoji: '😓', title: 'No visibility', desc: "You don't know what's overdue, what's been seen, or what's paid. Everything lives in your head." },
              ].map((p) => (
                <div key={p.title} className="flex items-start gap-3 bg-[#27272A] rounded-xl p-4">
                  <span className="text-xl mt-0.5">{p.emoji}</span>
                  <div>
                    <p className="font-semibold text-sm text-white">{p.title}</p>
                    <p className="text-[#71717A] text-xs mt-0.5 leading-relaxed">{p.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-[#F59E0B] text-xs font-bold uppercase tracking-widest mb-4">The solution</p>
            <h2 className="text-3xl md:text-4xl font-bold mb-5 tracking-tight leading-tight text-white">
              Nudgit sends the reminders. You focus on the work.
            </h2>
            <div className="space-y-4 mb-8">
              {[
                { step: '3 days before', desc: 'Friendly heads-up — "just so you know, this is coming up"' },
                { step: 'On the day', desc: 'Professional reminder — nothing personal, just business' },
                { step: '3 days after', desc: 'Polite but clear — "this is now overdue"' },
                { step: '7 days after', desc: 'Firm but fair — time to escalate' },
              ].map((s, i) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="w-7 h-7 rounded-full bg-[#F59E0B]/20 border border-[#F59E0B]/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-[#F59E0B] text-xs font-bold">{i + 1}</span>
                  </div>
                  <div>
                    <p className="text-[#F59E0B] text-xs font-semibold mb-0.5">{s.step}</p>
                    <p className="text-[#A1A1AA] text-sm">{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Loss stat */}
            <div className="bg-[#27272A] rounded-2xl p-5 border border-[#3F3F46]">
              <p className="text-[#71717A] text-xs">Average freelancer loses</p>
              <p className="text-4xl font-extrabold text-white mt-1">$4,200<span className="text-lg text-[#71717A] font-normal">/year</span></p>
              <p className="text-[#71717A] text-xs mt-1">to forgotten, unchased invoices. Nudgit fixes that.</p>
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
    { num: '01', title: 'Add your invoice', desc: 'Enter client name, email, amount, and due date. Or import 100 at once via CSV. Takes about 30 seconds.' },
    { num: '02', title: 'Pick your sequence', desc: "Choose a reminder template — Friendly, Professional, or Firm. We've written the copy. You just pick the tone." },
    { num: '03', title: 'Nudgit does the rest', desc: "Emails go out automatically at the right moments. You get notified on each step. Mark as paid with one click." },
  ]

  return (
    <section id="features" className="px-6 py-20 max-w-6xl mx-auto">
      <div className="text-center mb-14">
        <p className="text-[#F59E0B] text-xs font-bold uppercase tracking-widest mb-3">How it works</p>
        <h2 className="text-3xl md:text-4xl font-extrabold text-[#18181B] tracking-tight">Three steps. No awkwardness.</h2>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {steps.map((step, i) => (
          <div key={step.num} className="relative border border-[#E5E7EB] bg-white rounded-2xl p-6 hover:border-[#F59E0B]/50 hover:shadow-xl hover:shadow-amber-50/80 transition-all duration-300">
            <div className="text-5xl font-extrabold text-[#F3F4F6] mb-4">{step.num}</div>
            <h3 className="font-bold text-[#18181B] mb-2 text-lg">{step.title}</h3>
            <p className="text-[#64748B] text-sm leading-relaxed">{step.desc}</p>
            {i < steps.length - 1 && (
              <div className="hidden md:block absolute -right-2.5 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-white border border-[#E5E7EB] flex items-center justify-center">
                <svg className="w-2.5 h-2.5 text-[#94A3B8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
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
    { title: 'Human-written reminders', desc: "Nudgit's copy sounds like a professional colleague — never desperate, never passive.", icon: '✍' },
    { title: 'Smart timing', desc: 'Reminders go out at exactly the right moments. Friendly before, firm after. No manual work.', icon: '⏰' },
    { title: 'Full visibility', desc: "Every invoice, every status, every action taken. See who's seen it and who's ignoring it.", icon: '◉' },
    { title: 'CSV bulk import', desc: "Have a backlog? Import 100 invoices at once. One click and they're all being nudged.", icon: '⇪' },
    { title: 'One-click mark paid', desc: "Client pays? Mark it done. No more accidental follow-ups to people who already paid.", icon: '✓' },
    { title: 'Email + SMS channels', desc: "Some clients never open email. Nudgit supports SMS reminders too.", icon: '◎' },
  ]

  return (
    <section className="bg-[#FAFAFA] px-6 py-20 border-t border-[#E5E7EB]">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <p className="text-[#F59E0B] text-xs font-bold uppercase tracking-widest mb-3">Features</p>
          <h2 className="text-3xl md:text-4xl font-extrabold text-[#18181B] tracking-tight">Everything you need. Nothing you don't.</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f) => (
            <div key={f.title} className="bg-white rounded-2xl p-5 border border-[#E5E7EB] hover:shadow-lg hover:border-[#E5E7EB] transition-all">
              <div className="text-2xl mb-3 text-[#F59E0B]">{f.icon}</div>
              <h3 className="font-bold text-[#18181B] text-sm mb-1">{f.title}</h3>
              <p className="text-[#64748B] text-xs leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Testimonials ─────────────────────────────────────────────────────────────

function Testimonials() {
  const quotes = [
    { text: "I had $3,400 in unpaid invoices sitting in my inbox. Nudgit got me paid on all of them within two weeks. Can't believe I didn't have this sooner.", name: 'Daniela R.', role: 'Brand designer, freelance' },
    { text: "The awkwardness of chasing money was costing me real money. Nudgit handles it so professionally I don't even think about it anymore.", name: 'Marcus T.', role: 'Web developer, 3 years freelance' },
    { text: "I set up 20 overdue invoices in 10 minutes using the CSV import. By the end of the week, 18 of them were paid. Absolutely worth it.", name: 'Sofia M.', role: 'Photographer, small business' },
  ]

  return (
    <section className="px-6 py-20 max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <p className="text-[#F59E0B] text-xs font-bold uppercase tracking-widest mb-3">Early feedback</p>
        <h2 className="text-3xl md:text-4xl font-extrabold text-[#18181B] tracking-tight">People are already getting paid.</h2>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {quotes.map((q) => (
          <div key={q.name} className="bg-[#FAFAFA] rounded-2xl p-6 border border-[#E5E7EB]">
            <div className="text-[#F59E0B] text-2xl mb-3 leading-none">"</div>
            <p className="text-[#3F3F46] text-sm leading-relaxed mb-4">{q.text}</p>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-[#F59E0B]/20 flex items-center justify-center text-[#F59E0B] text-xs font-bold">{q.name.charAt(0)}</div>
              <div>
                <p className="text-sm font-semibold text-[#18181B]">{q.name}</p>
                <p className="text-xs text-[#94A3B8]">{q.role}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── Pricing ─────────────────────────────────────────────────────────────────

function Pricing({ onJoin }: { onJoin: (e: React.FormEvent) => void }) {
  const plans = [
    {
      name: 'Starter', price: 19, original: null,
      desc: 'For freelancers just getting started with invoicing.',
      features: ['20 invoices/month', 'Up to 3 reminders per invoice', 'Email reminders only', 'CSV import', 'Basic dashboard'],
      cta: 'Start free trial', highlight: false,
    },
    {
      name: 'Pro', price: 9, original: 39,
      desc: 'For serious freelancers. This price locks in forever.',
      features: ['100 invoices/month', 'Unlimited reminders', 'Email + SMS reminders', 'CSV import', 'Full dashboard', 'Custom sequences', 'Priority support'],
      cta: 'Get founding access', highlight: true,
    },
    {
      name: 'Agency', price: 89, original: null,
      desc: 'For agencies managing multiple clients.',
      features: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS + Slack', 'CSV import', 'Full dashboard', 'Multi-client view', 'Advanced sequences', 'Dedicated support'],
      cta: 'Contact us', highlight: false,
    },
  ]

  return (
    <section id="pricing" className="bg-[#FAFAFA] px-6 py-20 border-t border-[#E5E7EB]">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-14">
          <p className="text-[#F59E0B] text-xs font-bold uppercase tracking-widest mb-3">Pricing</p>
          <h2 className="text-3xl md:text-4xl font-extrabold text-[#18181B] tracking-tight">Simple pricing. No surprises.</h2>
          <p className="text-[#64748B] mt-3 text-sm">14-day free trial. No credit card required.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-5 items-start">
          {plans.map((plan) => (
            <div key={plan.name} className={`rounded-2xl p-6 border-2 transition-all ${plan.highlight ? 'border-[#F59E0B] bg-[#FFFBF5] shadow-xl shadow-amber-100/60 relative' : 'border-[#E5E7EB] bg-white'}`}>
              {plan.highlight && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2">
                  <span className="bg-[#F59E0B] text-white text-[11px] font-bold px-4 py-1 rounded-full shadow">Founding price</span>
                </div>
              )}
              <div className="mt-2 mb-1">
                <h3 className="font-bold text-[#18181B] text-lg">{plan.name}</h3>
                <p className="text-[#64748B] text-xs mt-0.5">{plan.desc}</p>
              </div>
              <div className="flex items-end gap-1.5 mb-5">
                <span className="text-4xl font-extrabold text-[#18181B]">${plan.price}</span>
                <span className="text-[#94A3B8] text-sm mb-1">/month</span>
                {plan.original && <span className="text-[#94A3B8] text-sm mb-1 line-through">${plan.original}</span>}
              </div>
              <ul className="space-y-2 mb-5">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-xs text-[#3F3F46]">
                    <svg className="w-3.5 h-3.5 text-[#F59E0B] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={onJoin}
                className={`w-full py-3 rounded-xl text-sm font-bold transition-all active:scale-[0.98] ${plan.highlight ? 'bg-[#F59E0B] hover:bg-[#D97706] text-white shadow-md shadow-amber-200' : 'bg-[#18181B] hover:bg-[#27272A] text-white'}`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
        <p className="text-center text-xs text-[#94A3B8] mt-6">Pro founding price locked for life. Cancel or upgrade anytime.</p>
      </div>
    </section>
  )
}

// ─── FAQ ─────────────────────────────────────────────────────────────────────

function FAQ() {
  const [open, setOpen] = useState<number | null>(null)
  const faqs = [
    { q: 'How does Nudgit send emails on my behalf?', a: 'Nudgit uses your connected email to send reminders. Clients see the email coming from you — Nudgit just handles the timing, content, and tracking.' },
    { q: 'What if a client pays but I forget to mark it?', a: 'Nudgit detects email replies and can auto-mark invoices as paid when a client confirms. You can also mark them paid manually with one click.' },
    { q: 'Can I customise the reminder messages?', a: 'Yes. Start with our templates across three tones — Friendly, Professional, or Firm. Or write your own from scratch.' },
    { q: 'When does the 14-day trial start?', a: 'Your trial starts when you create your account. No credit card required. After 14 days you subscribe or your account pauses.' },
    { q: 'What if I cancel?', a: 'Your data stays yours. Export everything before cancelling. Simple.' },
  ]

  return (
    <section id="faq" className="px-6 py-20 max-w-3xl mx-auto">
      <div className="text-center mb-12">
        <p className="text-[#F59E0B] text-xs font-bold uppercase tracking-widest mb-3">FAQ</p>
        <h2 className="text-3xl font-extrabold text-[#18181B] tracking-tight">Common questions</h2>
      </div>
      <div className="space-y-3">
        {faqs.map((faq, i) => (
          <div key={i} className="bg-white rounded-xl border border-[#E5E7EB] overflow-hidden">
            <button
              onClick={() => setOpen(open === i ? null : i)}
              className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-[#FAFAFA] transition-colors"
            >
              <span className="font-semibold text-sm text-[#18181B]">{faq.q}</span>
              <svg className={`w-4 h-4 text-[#94A3B8] transition-transform flex-shrink-0 ml-3 ${open === i ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {open === i && (
              <div className="px-5 pb-4">
                <p className="text-[#64748B] text-sm leading-relaxed">{faq.a}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── CTA ─────────────────────────────────────────────────────────────────────

function CTA({ onJoin }: { onJoin: (e: React.FormEvent) => void }) {
  return (
    <section className="bg-[#18181B] text-white px-6 py-20">
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight mb-4">Stop leaving money on the table.</h2>
        <p className="text-[#71717A] text-base mb-2">Founding Member pricing — $9/mo for life.</p>
        <p className="text-[#52525B] text-sm mb-8">First 50 signups only. 14-day free trial. No credit card required.</p>
        <form onSubmit={onJoin} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto mb-4">
          <input
            type="email"
            name="email"
            placeholder="you@yourbusiness.com"
            required
            className="flex-1 px-4 py-3.5 bg-[#27272A] border border-[#3F3F46] rounded-xl text-sm text-white placeholder-[#52525B] focus:outline-none focus:ring-2 focus:ring-[#F59E0B]"
          />
          <button
            type="submit"
            className="bg-[#F59E0B] hover:bg-[#D97706] active:scale-[0.98] text-white px-6 py-3.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-amber-900/20 whitespace-nowrap"
          >
            Get early access →
          </button>
        </form>
        <p className="text-xs text-[#3F3F46]">No spam. Unsubscribe anytime.</p>
      </div>
    </section>
  )
}

// ─── Footer ──────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="px-6 py-8 border-t border-[#E5E7EB] flex items-center justify-between text-xs text-[#94A3B8]">
      <div className="flex items-center gap-2">
        <img src="/logo.png" alt="Nudgit" className="h-5 w-auto object-contain opacity-60" />
        <span>© 2026 Nudgit</span>
      </div>
      <div className="flex items-center gap-4">
        <a href="#" className="hover:text-[#64748B] transition-colors">Privacy</a>
        <a href="#" className="hover:text-[#64748B] transition-colors">Terms</a>
        <a href="mailto:hello@nudgit.app" className="hover:text-[#64748B] transition-colors">Contact</a>
      </div>
    </footer>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function HomePage() {
  const [toast, setToast] = useState<ToastState>({ show: false, message: '' })

  function showToast(message: string) {
    setToast({ show: true, message })
    setTimeout(() => setToast(t => ({ ...t, show: false })), 4000)
  }

  function handleJoin(e: React.FormEvent) {
    e.preventDefault()
    const form = e.currentTarget as HTMLFormElement
    const email = (form.elements.namedItem('email') as HTMLInputElement)?.value ?? ''
    window.location.href = `/signup?email=${encodeURIComponent(email)}`
  }

  return (
    <div className="min-h-screen">
      <Nav />
      <Hero onJoin={handleJoin} />
      <Problem />
      <HowItWorks />
      <Features />
      <Testimonials />
      <Pricing onJoin={handleJoin} />
      <FAQ />
      <CTA onJoin={handleJoin} />
      <Footer />
      {toast.show && (
        <div className="fixed bottom-6 right-6 bg-[#18181B] text-white px-5 py-3.5 rounded-xl shadow-2xl text-sm font-medium flex items-center gap-2.5">
          <span className="text-[#10B981]">✓</span>
          {toast.message}
        </div>
      )}
    </div>
  )
}
