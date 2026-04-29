'use client'

import { useState } from 'react'
import Link from 'next/link'

type ToastState = { show: boolean; message: string }

// ─── Nav ───────────────────────────────────────────────────────────────────

function Nav() {
  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/logo.png" alt="Nudgit" className="h-10 w-auto object-contain" />
        </Link>
        <div className="flex items-center gap-6 text-sm font-medium">
          <a href="#features" className="text-gray-500 hover:text-black transition-colors">Features</a>
          <a href="#pricing" className="text-gray-500 hover:text-black transition-colors">Pricing</a>
          <Link href="/login" className="text-gray-500 hover:text-black transition-colors">Sign in</Link>
          <Link href="/signup" className="bg-black hover:bg-gray-800 text-white px-4 py-2 rounded-lg transition-colors">
            Buy now — $29
          </Link>
        </div>
      </div>
    </nav>
  )
}

// ─── Hero ────────────────────────────────────────────────────────────────────

function Hero({ onJoin }: { onJoin: (e: React.FormEvent) => void }) {
  return (
    <section className="px-6 pt-12 pb-20 max-w-6xl mx-auto">
      <div className="grid lg:grid-cols-2 gap-12 items-center">

        <div>
          <div className="inline-flex items-center gap-2 bg-orange/10 text-orange px-3 py-1.5 rounded-full text-xs font-semibold mb-7">
            <span className="w-1.5 h-1.5 bg-orange rounded-full" />
            $29 one-time · Own it forever · First 20 signups only
          </div>

          <h1 className="text-5xl md:text-6xl font-black text-black tracking-tight leading-[1.04] mb-5">
            Get paid.<br />
            <span className="text-orange">Without the chase.</span>
          </h1>

          <p className="text-lg text-gray-500 leading-relaxed mb-8 max-w-md">
            Nudgit sends perfectly timed invoice reminders — so you stop losing money to forgotten payments. No awkward follow-ups. No embarrassing emails. Pay once, own forever.
          </p>

          <form onSubmit={onJoin} className="flex flex-col sm:flex-row gap-3 mb-6">
            <input
              type="email"
              name="email"
              placeholder="you@yourbusiness.com"
              required
              className="flex-1 px-4 py-3.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-orange placeholder-gray-400"
            />
            <button
              type="submit"
              className="bg-orange hover:bg-orange-dark active:scale-[0.98] text-white px-6 py-3.5 rounded-xl text-sm font-bold transition-all shadow-orange whitespace-nowrap"
            >
              Buy now — $29 →
            </button>
          </form>

          <div className="flex items-center gap-3 text-xs text-gray-400">
            <div className="flex -space-x-2">
              {['u1','u2','u3'].map(s => (
                <img key={s} src={`https://picsum.photos/seed/${s}/32/32`} className="w-7 h-7 rounded-full border-2 border-white object-cover" alt="" />
              ))}
            </div>
            <span>147 freelancers already signed up · 30-day money-back guarantee</span>
          </div>
        </div>

        {/* Dashboard preview */}
        <div className="relative">
          <div className="absolute -inset-4 bg-gradient-to-br from-orange/5 via-transparent to-orange/10 rounded-3xl blur-2xl" />
          <div className="relative bg-white rounded-2xl border border-gray-200 shadow-2xl overflow-hidden">
            <div className="bg-gray-50 border-b border-gray-100 px-5 py-3.5 flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
              <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
              <span className="ml-3 text-[10px] text-gray-400 font-mono">nudgit.app</span>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-3 gap-3 mb-4">
                {[
                  { label: 'Outstanding', value: '$8,450', color: 'text-black' },
                  { label: 'Overdue', value: '6 ⚠', color: 'text-red-500' },
                  { label: 'Paid', value: '$1,300', color: 'text-green-500' },
                ].map(c => (
                  <div key={c.label} className="bg-gray-50 rounded-xl p-3.5 border border-gray-100">
                    <p className="text-[11px] text-gray-400 font-medium mb-1">{c.label}</p>
                    <p className={`text-xl font-bold ${c.color}`}>{c.value}</p>
                  </div>
                ))}
              </div>
              <div className="rounded-xl border border-gray-100 overflow-hidden">
                <div className="bg-gray-50 px-4 py-2.5 border-b border-gray-100 flex items-center justify-between">
                  <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Invoices</span>
                  <span className="text-[11px] text-orange font-semibold">+ Add</span>
                </div>
                {[
                  { client: 'Meridian Design Co.', amount: '$2,100', due: 'Apr 22', status: 'Overdue', sBg: 'bg-red-50', sFg: 'text-red-600' },
                  { client: 'Harlow Photography', amount: '$850', due: 'Apr 29', status: 'Pending', sBg: 'bg-gray-50', sFg: 'text-gray-500' },
                  { client: 'CoreTech Solutions', amount: '$4,200', due: 'May 3', status: 'Pending', sBg: 'bg-gray-50', sFg: 'text-gray-500' },
                ].map(r => (
                  <div key={r.client} className="px-4 py-3 flex items-center justify-between border-b border-gray-50 last:border-0">
                    <div>
                      <p className="text-xs font-semibold text-black">{r.client}</p>
                      <p className="text-[11px] text-gray-400">Due {r.due}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-gray-500">{r.amount}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${r.sBg} ${r.sFg}`}>{r.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── Problem / Solution ────────────────────────────────────────────────────────

function Problem() {
  return (
    <section className="bg-black text-white px-6 py-20">
      <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-16">
        <div>
          <p className="text-orange text-xs font-black uppercase tracking-widest mb-4">The problem</p>
          <h2 className="text-3xl md:text-4xl font-black mb-5 tracking-tight leading-tight">
            You sent the invoice.<br />Then you forgot.
          </h2>
          <p className="text-gray-400 leading-relaxed mb-6">
            It happens to every freelancer. You move on, the project closes, the invoice sits in an inbox. Three months later: $4,200 gone. Nudgit fixes it.
          </p>
          <div className="space-y-3">
            {[
              { t: '😬', d: 'No reminder system. Invoices just... die in inboxes.' },
              { t: '😩', d: "Chasing feels awkward. So you don't. And lose money." },
              { t: '😓', d: "No visibility. You never know what's actually overdue." },
            ].map(p => (
              <div key={p.t} className="flex items-start gap-3 bg-white/5 rounded-xl p-4">
                <span className="text-xl">{p.t}</span>
                <p className="text-gray-300 text-sm">{p.d}</p>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-orange text-xs font-black uppercase tracking-widest mb-4">The fix</p>
          <h2 className="text-3xl md:text-4xl font-black mb-5 tracking-tight leading-tight text-white">
            Nudgit sends the reminders. You stay professional.
          </h2>
          <div className="space-y-3 mb-8">
            {[
              { d: '3 days before due date', s: 'Friendly heads-up. Nothing awkward.' },
              { d: 'On the due date', s: 'Professional nudge. Nothing personal.' },
              { d: '3 days overdue', s: 'Polite but clear. Time is money.' },
              { d: '7 days overdue', s: 'Firm. You don\'t have to be.' },
            ].map((s, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-orange flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-white text-xs font-black">{i + 1}</span>
                </div>
                <div>
                  <p className="text-orange text-xs font-semibold">{s.d}</p>
                  <p className="text-gray-400 text-sm">{s.s}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="bg-white/5 rounded-2xl p-5 border border-white/10">
            <p className="text-gray-500 text-xs">Average freelancer loses</p>
            <p className="text-4xl font-black text-white mt-1">$4,200<span className="text-lg text-gray-500 font-normal">/year</span></p>
          </div>
        </div>
      </div>
    </section>
  )
}

// ─── How it works ────────────────────────────────────────────────────────────

function HowItWorks() {
  return (
    <section id="features" className="px-6 py-20 max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <p className="text-orange text-xs font-black uppercase tracking-widest mb-3">How it works</p>
        <h2 className="text-4xl md:text-5xl font-black text-black tracking-tight">Three steps. Zero awkwardness.</h2>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {[
          { n: '01', t: 'Add your invoice', d: 'Client name, email, amount, due date. Or import 100 via CSV. 30 seconds.' },
          { n: '02', t: 'Pick your tone', d: 'Friendly, professional, or firm. We wrote the copy. You just choose.' },
          { n: '03', t: 'Nudgit handles it', d: 'Reminders go out automatically. Mark paid with one click when it lands.' },
        ].map(s => (
          <div key={s.n} className="relative border border-gray-200 rounded-2xl p-6 hover:border-orange/40 transition-all">
            <div className="text-5xl font-black text-gray-100 mb-3">{s.n}</div>
            <h3 className="font-black text-black text-lg mb-2">{s.t}</h3>
            <p className="text-gray-500 text-sm leading-relaxed">{s.d}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── Features ───────────────────────────────────────────────────────────────

function Features() {
  const features = [
    { t: 'Human-written copy', d: "Reminders sound like a colleague. Never desperate, never passive.", i: '✍' },
    { t: 'Smart timing', d: 'Friendly before due date. Firm after. Perfectly timed.', i: '⏰' },
    { t: 'Full visibility', d: "Every invoice, every status. See who opened and who ignored.", i: '◉' },
    { t: 'CSV bulk import', d: '100 invoices at once. One click. All of them get nudged.', i: '⇪' },
    { t: 'One-click paid', d: "Client pays? Mark done. No more accidental follow-ups.", i: '✓' },
    { t: 'Email + SMS', d: "Some clients never open email. Nudgit reaches them on SMS.", i: '◎' },
  ]
  return (
    <section className="bg-gray-50 px-6 py-20 border-t border-gray-100">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-orange text-xs font-black uppercase tracking-widest mb-3">Features</p>
          <h2 className="text-4xl font-black text-black tracking-tight">Everything you need. Nothing you don't.</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map(f => (
            <div key={f.t} className="bg-white rounded-2xl p-5 border border-gray-100 hover:shadow-md transition-all">
              <div className="text-2xl mb-3 text-orange">{f.i}</div>
              <h3 className="font-bold text-black text-sm mb-1">{f.t}</h3>
              <p className="text-gray-500 text-xs leading-relaxed">{f.d}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ─── Testimonials ─────────────────────────────────────────────────────────────

function Testimonials() {
  return (
    <section className="px-6 py-20 max-w-6xl mx-auto">
      <div className="text-center mb-12">
        <p className="text-orange text-xs font-black uppercase tracking-widest mb-3">Early feedback</p>
        <h2 className="text-4xl font-black text-black tracking-tight">People are already getting paid.</h2>
      </div>
      <div className="grid md:grid-cols-3 gap-5">
        {[
          { q: "I had $3,400 in unpaid invoices. Nudgit got me paid on all of them in two weeks.", n: 'Daniela R.', r: 'Brand designer' },
          { q: "The awkwardness was costing me real money. Nudgit handles it so professionally.", n: 'Marcus T.', r: 'Web developer' },
          { q: "Imported 20 invoices in 10 minutes. 18 of them paid by the end of the week.", n: 'Sofia M.', r: 'Photographer' },
        ].map(t => (
          <div key={t.n} className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
            <div className="text-orange text-2xl mb-3">"</div>
            <p className="text-gray-700 text-sm leading-relaxed mb-4">{t.q}</p>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-orange/10 flex items-center justify-center text-orange text-xs font-bold">{t.n.charAt(0)}</div>
              <div><p className="text-sm font-bold text-black">{t.n}</p><p className="text-xs text-gray-400">{t.r}</p></div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── Pricing ─────────────────────────────────────────────────────────────────

function Pricing({ onJoin }: { onJoin: (e: React.FormEvent) => void }) {
  return (
    <section id="pricing" className="bg-gray-50 px-6 py-20 border-t border-gray-100">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <p className="text-orange text-xs font-black uppercase tracking-widest mb-3">Pricing</p>
          <h2 className="text-4xl font-black text-black tracking-tight">Pay once. Own it forever.</h2>
          <p className="text-gray-500 mt-2 text-sm">No subscriptions. No recurring charges. No tricks.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-5 items-start">
          {[
            { n: 'Starter', p: 19, op: null, d: 'For freelancers starting out.', fs: ['20 invoices/mo', '3 reminders/invoice', 'Email only', 'CSV import', 'Basic dashboard'], hl: false, cta: 'Start free trial' },
            { n: 'Lifetime Access', p: 29, op: null, d: 'Pay once. Own it forever. Best value.', fs: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS', 'CSV import', 'Full dashboard', 'Custom sequences', 'Priority support', 'All future updates'], hl: true, cta: 'Buy now — $29' },
            { n: 'Agency', p: 89, op: null, d: 'For agencies with multiple clients.', fs: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS + Slack', 'CSV import', 'Multi-client view', 'Advanced sequences'], hl: false, cta: 'Contact us' },
          ].map(plan => (
            <div key={plan.n} className={`rounded-2xl p-6 border-2 transition-all ${plan.hl ? 'border-orange bg-white shadow-xl' : 'border-gray-200 bg-white'}`}>
              {plan.hl && <div className="text-center mb-3"><span className="bg-orange text-white text-[11px] font-black px-3 py-1 rounded-full">Best value · Pay once</span></div>}
              <h3 className="font-black text-black text-lg mb-1">{plan.n}</h3>
              <p className="text-gray-500 text-xs mb-4">{plan.d}</p>
              <div className="flex items-end gap-1 mb-5">
                <span className="text-4xl font-black text-black">${plan.p}</span>
                <span className="text-green-500 text-sm font-bold mb-1">one-time</span>
              </div>
              <ul className="space-y-2 mb-5">
                {plan.fs.map(f => (
                  <li key={f} className="flex items-center gap-2 text-xs text-gray-600">
                    <svg className="w-3.5 h-3.5 text-orange flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                    {f}
                  </li>
                ))}
              </ul>
              <button onClick={onJoin} className={`w-full py-3 rounded-xl text-sm font-bold transition-all active:scale-[0.98] ${plan.hl ? 'bg-orange hover:bg-orange-dark text-white shadow-orange' : 'bg-black hover:bg-gray-800 text-white'}`}>
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
        <p className="text-center text-xs text-gray-400 mt-5">30-day money-back guarantee · Instant access after payment</p>
      </div>
    </section>
  )
}

// ─── FAQ ─────────────────────────────────────────────────────────────────────

function FAQ() {
  const [open, setOpen] = useState<number | null>(null)
  const faqs = [
    { q: 'Is this really a one-time payment?', a: 'Yes. Pay $29 once and own Lifetime Access forever. No subscriptions. No hidden charges. Ever.' },
    { q: 'What if I want a refund?', a: '30-day money-back guarantee. Not happy? Full refund, no questions.' },
    { q: 'How does Nudgit send emails on my behalf?', a: 'Nudgit uses your connected email. Clients see the email from you — Nudgit handles the timing, content, and tracking.' },
    { q: 'Can I customise the reminder messages?', a: 'Yes. Start with our templates (Friendly, Professional, Firm) or write your own from scratch.' },
    { q: 'What if a client pays but I forget to mark it?', a: 'One click to mark as paid. Or Nudgit detects replies and auto-marks invoices as paid.' },
  ]
  return (
    <section id="faq" className="px-6 py-20 max-w-3xl mx-auto">
      <div className="text-center mb-12">
        <p className="text-orange text-xs font-black uppercase tracking-widest mb-3">FAQ</p>
        <h2 className="text-3xl font-black text-black tracking-tight">Common questions.</h2>
      </div>
      <div className="space-y-3">
        {faqs.map((f, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-100 overflow-hidden">
            <button onClick={() => setOpen(open === i ? null : i)} className="w-full px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
              <span className="font-semibold text-sm text-black">{f.q}</span>
              <svg className={`w-4 h-4 text-gray-400 transition-transform flex-shrink-0 ml-3 ${open === i ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
            </button>
            {open === i && <div className="px-5 pb-4"><p className="text-gray-500 text-sm leading-relaxed">{f.a}</p></div>}
          </div>
        ))}
      </div>
    </section>
  )
}

// ─── CTA ─────────────────────────────────────────────────────────────────────

function CTA({ onJoin }: { onJoin: (e: React.FormEvent) => void }) {
  return (
    <section className="bg-black text-white px-6 py-20">
      <div className="max-w-2xl mx-auto text-center">
        <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4">Stop leaving money on the table.</h2>
        <p className="text-gray-400 mb-2">$29 one-time · Own it forever.</p>
        <p className="text-gray-600 text-sm mb-8">First 20 signups get the founding price. No credit card required.</p>
        <form onSubmit={onJoin} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto mb-4">
          <input type="email" name="email" placeholder="you@yourbusiness.com" required className="flex-1 px-4 py-3.5 bg-white/10 border border-white/20 rounded-xl text-sm text-white placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-orange" />
          <button type="submit" className="bg-orange hover:bg-orange-dark active:scale-[0.98] text-white px-6 py-3.5 rounded-xl text-sm font-bold transition-all whitespace-nowrap">
            Buy now — $29 →
          </button>
        </form>
        <p className="text-xs text-gray-600">Secure Stripe checkout · Instant access · 30-day money-back guarantee</p>
      </div>
    </section>
  )
}

// ─── Footer ──────────────────────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="px-6 py-8 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400">
      <div className="flex items-center gap-2">
        <img src="/logo.png" alt="Nudgit" className="h-5 w-auto object-contain opacity-50" />
        <span>© 2026 Nudgit</span>
      </div>
      <div className="flex gap-4">
        <a href="#" className="hover:text-gray-600">Privacy</a>
        <a href="#" className="hover:text-gray-600">Terms</a>
        <a href="mailto:hello@nudgit.app" className="hover:text-gray-600">Contact</a>
      </div>
    </footer>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function HomePage() {
  function handleJoin(e: React.FormEvent) {
    e.preventDefault()
    const form = e.currentTarget as HTMLFormElement
    const email = (form.elements.namedItem('email') as HTMLInputElement)?.value ?? ''
    window.location.href = `/signup?email=${encodeURIComponent(email)}`
  }

  return (
    <div>
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
    </div>
  )
}
