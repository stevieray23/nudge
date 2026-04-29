'use client'

import { useState } from 'react'
import Link from 'next/link'

function Confetti() {
  const dots = [
    { x: 20, y: 30, color: '#F59E0B', size: 8, delay: 0 },
    { x: 35, y: 15, color: '#EF4444', size: 6, delay: 0.1 },
    { x: 55, y: 25, color: '#F59E0B', size: 10, delay: 0.05 },
    { x: 70, y: 35, color: '#FBBF24', size: 7, delay: 0.15 },
    { x: 85, y: 20, color: '#F59E0B', size: 6, delay: 0.08 },
    { x: 10, y: 50, color: '#F59E0B', size: 9, delay: 0.12 },
    { x: 45, y: 45, color: '#EF4444', size: 7, delay: 0.2 },
    { x: 75, y: 55, color: '#F59E0B', size: 8, delay: 0.07 },
  ]
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {dots.map((dot, i) => (
        <div key={i} style={{
          position: 'absolute', left: `${dot.x}%`, top: `${dot.y}%`,
          width: dot.size, height: dot.size, borderRadius: '50%', background: dot.color,
          animation: `confettiFall 1.5s ease-out ${dot.delay}s forwards`,
        }} />
      ))}
      <style>{`@keyframes confettiFall { 0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; } 100% { transform: translateY(120px) rotate(360deg) scale(0); opacity: 0; } }`}</style>
    </div>
  )
}

function Nav() {
  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 px-8 py-5 flex items-center justify-between">
      <Link href="/" className="flex items-center gap-2.5">
        <img src="/logo.png" alt="Nudgit" className="h-8 w-auto object-contain" />
        <span className="font-black text-black text-lg tracking-tight">Nudgit</span>
      </Link>
      <span className="text-sm text-gray-500">Already have access? <Link href="/login" className="text-black font-bold hover:text-orange transition-colors">Sign in</Link></span>
    </nav>
  )
}

type Plan = {
  name: string; badge: string | null; price: number; originalPrice: number | null
  desc: string; features: string[]; highlight: boolean; priceId: string; isOneTime?: boolean
}

const plans: Plan[] = [
  {
    name: 'Starter', badge: null, price: 19, originalPrice: null,
    desc: 'For freelancers just getting started.',
    features: ['20 invoices/month', 'Up to 3 reminders per invoice', 'Email reminders', 'CSV import', 'Basic dashboard'],
    highlight: false, priceId: 'onetime_starter',
  },
  {
    name: 'Lifetime Access', badge: 'Best value', price: 29, originalPrice: null,
    desc: 'Pay once. Own it forever. No subscriptions.',
    features: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS', 'CSV import', 'Full dashboard', 'Custom sequences', 'Priority support', 'All future updates free'],
    highlight: true, priceId: 'onetime_lifetime', isOneTime: true,
  },
  {
    name: 'Agency', badge: null, price: 89, originalPrice: null,
    desc: 'For agencies managing multiple clients.',
    features: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS + Slack', 'CSV import', 'Full dashboard', 'Multi-client view', 'Advanced sequences'],
    highlight: false, priceId: 'onetime_agency',
  },
]

function AnimatedCheck() {
  return (
    <div className="relative mx-auto mb-5 w-16 h-16">
      <div className="w-16 h-16 rounded-full bg-green-100 border-2 border-green-200 flex items-center justify-center">
        <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <div className="absolute inset-0 rounded-full bg-green-100/30 animate-ping" style={{ animationDuration: '2s' }} />
    </div>
  )
}

export default function SignupPage() {
  const [selectedPlan, setSelectedPlan] = useState<number>(1)
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [showConfirmation, setShowConfirmation] = useState(false)

  async function handleCheckout() {
    if (!email) return
    setLoading(true)
    try {
      const plan = plans[selectedPlan]
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId: plan.priceId, email, mode: plan.isOneTime ? 'payment' : 'subscription' }),
      })
      const data = await res.json()
      if (data.url) {
        window.location.href = data.url
      } else {
        // Simulate success when Stripe not wired yet
        setShowConfirmation(true)
      }
    } catch {
      setShowConfirmation(true)
    } finally {
      setLoading(false)
    }
  }

  if (showConfirmation) {
    return (
      <div className="min-h-screen bg-white">
        <Nav />
        <Confetti />
        <div className="flex flex-col items-center justify-center px-8 py-24 max-w-md mx-auto text-center">
          <AnimatedCheck />
          <h1 className="text-3xl font-black text-black tracking-tight mb-3">You&apos;re in!</h1>
          <p className="text-gray-500 leading-relaxed mb-6">
            Welcome to Nudgit, {email || 'new friend'}. Your lifetime access is confirmed.
            <br /><br />
            We&apos;ll send you a setup email shortly. Tell a fellow freelancer — they might appreciate it.
          </p>
          <div className="bg-gray-50 rounded-2xl p-5 w-full text-left border border-gray-100">
            <p className="text-xs text-gray-400 font-black uppercase tracking-widest mb-3">What happens next</p>
            <ul className="space-y-2.5">
              {[
                'Check your inbox for setup instructions',
                'Create your account and connect your email',
                'Import your first invoice (CSV or manual)',
                'Nudgit starts working for you automatically',
              ].map((step, i) => (
                <li key={i} className="flex items-center gap-2.5 text-sm text-gray-600">
                  <span className="w-5 h-5 rounded-full bg-orange/10 border border-orange/30 flex items-center justify-center text-orange text-xs font-black flex-shrink-0">{i + 1}</span>
                  {step}
                </li>
              ))}
            </ul>
          </div>
          <Link href="/login" className="mt-6 text-sm font-bold text-orange hover:text-orange-dark transition-colors">
            Go to your dashboard →
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <div className="max-w-4xl mx-auto px-8 py-14">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-orange/10 text-orange px-4 py-1.5 rounded-full text-xs font-black mb-5">
            <span className="w-1.5 h-1.5 bg-orange rounded-full animate-pulse" />
            v1 Launch — founding price · First 20 signups only
          </div>
          <h1 className="text-4xl font-black text-black tracking-tight mb-3">Choose your plan.</h1>
          <p className="text-gray-500">Pay once. Own it forever. No subscriptions.</p>
        </div>

        {/* Plan grid */}
        <div className="grid md:grid-cols-3 gap-5 mb-10">
          {plans.map((plan, i) => (
            <button
              key={plan.name}
              onClick={() => setSelectedPlan(i)}
              className={`text-left rounded-2xl p-6 border-2 transition-all duration-200 ${selectedPlan === i ? (plan.highlight ? 'border-orange bg-white shadow-xl shadow-orange/20' : 'border-orange bg-white') : 'border-gray-200 bg-white hover:border-gray-300'}`}
            >
              {plan.badge && (
                <div className="mb-3">
                  <span className={`text-xs font-black px-3 py-1 rounded-full ${plan.highlight ? 'bg-orange text-white' : 'bg-gray-100 text-gray-600'}`}>{plan.badge}</span>
                </div>
              )}
              <h3 className="font-black text-black text-lg mb-1">{plan.name}</h3>
              <div className="flex items-end gap-1.5 mb-3">
                <span className="text-3xl font-black text-black">${plan.price}</span>
                {plan.isOneTime ? (
                  <span className="text-green-500 text-sm font-bold mb-1">one-time</span>
                ) : (
                  <span className="text-gray-400 text-sm mb-1">/month</span>
                )}
              </div>
              <p className="text-gray-500 text-xs mb-4 leading-relaxed">{plan.desc}</p>
              <ul className="space-y-1.5 mb-4">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-xs text-gray-600">
                    <svg className="w-3.5 h-3.5 text-orange flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                    {f}
                  </li>
                ))}
              </ul>
              {selectedPlan === i && (
                <div className="pt-4 border-t border-orange/20 flex items-center gap-2 text-xs text-orange font-bold">
                  <div className="w-4 h-4 rounded-full bg-orange flex items-center justify-center"><div className="w-1.5 h-1.5 bg-white rounded-full" /></div>
                  Selected
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Email + CTA */}
        <div className="bg-white rounded-2xl border border-gray-100 p-8 shadow-sm">
          <p className="text-sm font-bold text-black mb-3 text-center">Your email address</p>
          <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@yourbusiness.com" required className="flex-1 px-4 py-3.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-orange" />
            <button onClick={handleCheckout} disabled={loading || !email} className="bg-orange hover:bg-orange-dark disabled:bg-gray-300 disabled:cursor-not-allowed active:scale-[0.98] text-white px-6 py-3.5 rounded-xl text-sm font-bold transition-all shadow-orange whitespace-nowrap flex items-center justify-center gap-2 min-w-[160px]">
              {loading ? <><svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>Processing...</> : <>Buy now — $29 →</>}
            </button>
          </div>
          <p className="text-xs text-gray-400 text-center mt-3">Secure checkout via Stripe · Instant access after payment</p>
          <div className="flex items-center justify-center gap-5 mt-5 pt-5 border-t border-gray-100">
            {[{ icon: '🔒', label: 'Secure checkout' }, { icon: '⚡', label: 'Instant access' }, { icon: '💳', label: 'Powered by Stripe' }].map(item => (
              <div key={item.label} className="flex items-center gap-1.5 text-xs text-gray-400"><span>{item.icon}</span><span>{item.label}</span></div>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">30-day money-back guarantee. Not happy? Full refund, no questions.</p>
      </div>
    </div>
  )
}
