'use client'

import { useState } from 'react'
import Link from 'next/link'

function Confetti() {
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {[
        { x: 20, y: 30, color: '#F59E0B', size: 8, delay: 0 },
        { x: 35, y: 15, color: '#EF4444', size: 6, delay: 0.1 },
        { x: 55, y: 25, color: '#F59E0B', size: 10, delay: 0.05 },
        { x: 70, y: 35, color: '#FBBF24', size: 7, delay: 0.15 },
        { x: 85, y: 20, color: '#F59E0B', size: 6, delay: 0.08 },
        { x: 10, y: 50, color: '#F59E0B', size: 9, delay: 0.12 },
        { x: 45, y: 45, color: '#EF4444', size: 7, delay: 0.2 },
        { x: 75, y: 55, color: '#F59E0B', size: 8, delay: 0.07 },
      ].map((dot, i) => (
        <div key={i} style={{ position: 'absolute', left: `${dot.x}%`, top: `${dot.y}%`, width: dot.size, height: dot.size, borderRadius: '50%', background: dot.color, animation: `confettiFall 1.5s ease-out ${dot.delay}s forwards` }} />
      ))}
      <style>{`@keyframes confettiFall { 0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; } 100% { transform: translateY(120px) rotate(360deg) scale(0); opacity: 0; } }`}</style>
    </div>
  )
}

function Nav() {
  return (
    <nav className="sticky top-0 z-50 bg-[#FFFBF5]/90 backdrop-blur-md border-b border-[#E5E7EB] px-8 py-5 flex items-center justify-between">
      <Link href="/" className="flex items-center gap-2.5">
        <img src="/logo.png" alt="Nudgit" className="h-8 w-auto object-contain" />
        <span className="font-semibold text-[#18181B] text-lg tracking-tight">Nudgit</span>
      </Link>
      <span className="text-sm text-[#64748B]">Already have an account? <Link href="/login" className="text-[#18181B] font-semibold hover:text-[#F59E0B] transition-colors">Sign in</Link></span>
    </nav>
  )
}

type Plan = {
  name: string; badge: string | null; price: number; originalPrice: number | null
  desc: string; features: string[]; highlight: boolean; stripePriceId: string
}

const plans: Plan[] = [
  {
    name: 'Starter', badge: null, price: 19, originalPrice: null,
    desc: 'For freelancers just getting started with invoicing.',
    features: ['20 invoices/month', 'Up to 3 reminders per invoice', 'Email reminders', 'CSV import', 'Basic dashboard'],
    highlight: false,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_STARTER_PRICE_ID ?? '',
  },
  {
    name: 'Pro', badge: 'Founding price', price: 9, originalPrice: 39,
    desc: 'For serious freelancers. This price locks in forever. No tricks.',
    features: ['100 invoices/month', 'Unlimited reminders', 'Email + SMS reminders', 'CSV import', 'Full dashboard', 'Custom sequences', 'Priority support'],
    highlight: true,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID ?? '',
  },
  {
    name: 'Agency', badge: null, price: 89, originalPrice: null,
    desc: 'For agencies managing multiple clients and contractors.',
    features: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS + Slack', 'CSV import', 'Full dashboard', 'Multi-client view', 'Advanced sequences', 'Dedicated support'],
    highlight: false,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_AGENCY_PRICE_ID ?? '',
  },
]

function AnimatedCheck() {
  return (
    <div className="relative mx-auto mb-5 w-16 h-16">
      <div className="w-16 h-16 rounded-full bg-[#DCFCE7] border-2 border-[#BBF7D0] flex items-center justify-center">
        <svg className="w-8 h-8 text-[#16A34A]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <div className="absolute inset-0 rounded-full bg-[#DCFCE7]/30 animate-ping" style={{ animationDuration: '2s' }} />
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
        body: JSON.stringify({ priceId: plan.stripePriceId, email }),
      })
      const data = await res.json()
      if (data.url) {
        window.location.href = data.url
      } else {
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
      <div className="min-h-screen bg-[#FFFBF5]">
        <Nav />
        <Confetti />
        <div className="flex flex-col items-center justify-center px-8 py-24 max-w-md mx-auto text-center">
          <AnimatedCheck />
          <h1 className="text-3xl font-extrabold text-[#18181B] tracking-tight mb-3">You&apos;re in!</h1>
          <p className="text-[#64748B] leading-relaxed mb-6">
            Welcome to Nudgit, {email || 'new friend'}. Your founding membership is confirmed.
            <br /><br />
            We&apos;ll send you a welcome email shortly. Tell a fellow freelancer — they might appreciate it.
          </p>
          <div className="bg-white rounded-2xl p-5 w-full text-left border border-[#E5E7EB] shadow-sm">
            <p className="text-xs text-[#94A3B8] font-bold uppercase tracking-widest mb-3">What happens next</p>
            <ul className="space-y-2.5">
              {['Check your inbox for a welcome email', 'Set up your account and connect your email', 'Import your first invoice (CSV or manual)', 'Nudgit starts working for you automatically'].map((step, i) => (
                <li key={i} className="flex items-center gap-2.5 text-sm text-[#3F3F46]">
                  <span className="w-5 h-5 rounded-full bg-[#FEF3C7] border border-[#FDE68A] flex items-center justify-center text-[#F59E0B] text-xs font-bold flex-shrink-0">{i + 1}</span>
                  {step}
                </li>
              ))}
            </ul>
          </div>
          <Link href="/login" className="mt-6 text-sm text-[#F59E0B] font-semibold hover:text-[#D97706] transition-colors">
            Go to your dashboard →
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA]">
      <Nav />
      <div className="max-w-4xl mx-auto px-8 py-14">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-[#FEF3C7] text-[#D97706] border border-[#FDE68A] px-4 py-1.5 rounded-full text-xs font-semibold mb-5">
            <span className="w-1.5 h-1.5 bg-[#F59E0B] rounded-full animate-pulse" />
            Founding Member pricing — limited to first 50 signups
          </div>
          <h1 className="text-4xl font-extrabold text-[#18181B] tracking-tight mb-3">Choose your plan.</h1>
          <p className="text-[#64748B]">14-day free trial. No credit card required to start.</p>
        </div>

        {/* Plan grid */}
        <div className="grid md:grid-cols-3 gap-5 mb-10">
          {plans.map((plan, i) => (
            <button
              key={plan.name}
              onClick={() => setSelectedPlan(i)}
              className={`text-left rounded-2xl p-6 border-2 transition-all duration-200 ${selectedPlan === i ? (plan.highlight ? 'border-[#F59E0B] bg-[#FFFBF5] shadow-xl shadow-amber-100/60' : 'border-[#F59E0B] bg-white shadow-xl shadow-amber-100/60') : 'border-[#E5E7EB] bg-white hover:border-[#D1D5DB]'}`}
            >
              {plan.badge && (
                <div className="mb-3">
                  <span className={`text-xs font-bold px-3 py-1 rounded-full ${plan.highlight ? 'bg-[#F59E0B] text-white' : 'bg-[#F3F4F6] text-[#64748B]'}`}>{plan.badge}</span>
                </div>
              )}
              <h3 className="font-bold text-[#18181B] text-lg mb-1">{plan.name}</h3>
              <div className="flex items-end gap-1.5 mb-3">
                <span className="text-3xl font-extrabold text-[#18181B]">${plan.price}</span>
                <span className="text-[#94A3B8] text-sm mb-1">/month</span>
                {plan.originalPrice && <span className="text-[#94A3B8] text-sm mb-1 line-through">${plan.originalPrice}</span>}
              </div>
              <p className="text-[#64748B] text-xs mb-4 leading-relaxed">{plan.desc}</p>
              <ul className="space-y-1.5 mb-4">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-xs text-[#3F3F46]">
                    <svg className="w-3.5 h-3.5 text-[#F59E0B] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>
                    {f}
                  </li>
                ))}
              </ul>
              {selectedPlan === i && (
                <div className="pt-4 border-t border-amber-200 flex items-center gap-2 text-xs text-[#D97706] font-semibold">
                  <div className="w-4 h-4 rounded-full bg-[#F59E0B] flex items-center justify-center"><div className="w-1.5 h-1.5 bg-white rounded-full" /></div>
                  Selected
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Email + CTA */}
        <div className="bg-white rounded-2xl border border-[#E5E7EB] p-8 shadow-sm">
          <p className="text-sm font-semibold text-[#18181B] mb-3 text-center">Your email address</p>
          <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@yourbusiness.com"
              required
              className="flex-1 px-4 py-3.5 border border-[#E5E7EB] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#F59E0B] placeholder-[#94A3B8]"
            />
            <button
              onClick={handleCheckout}
              disabled={loading || !email}
              className="bg-[#F59E0B] hover:bg-[#D97706] disabled:bg-[#D1D5DB] disabled:cursor-not-allowed active:scale-[0.98] text-white px-6 py-3.5 rounded-xl text-sm font-bold transition-all shadow-md shadow-amber-200 whitespace-nowrap flex items-center justify-center gap-2 min-w-[160px]"
            >
              {loading ? (
                <><svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>Processing...</>
              ) : 'Start free trial →'}
            </button>
          </div>
          <p className="text-xs text-[#94A3B8] text-center mt-3">14-day free trial · No credit card required · Cancel anytime</p>

          {/* Trust signals */}
          <div className="flex items-center justify-center gap-5 mt-5 pt-5 border-t border-[#F3F4F6]">
            {[{ icon: '🔒', label: 'Secure checkout' }, { icon: '⚡', label: 'Instant access' }, { icon: '💳', label: 'Powered by Stripe' }].map((item) => (
              <div key={item.label} className="flex items-center gap-1.5 text-xs text-[#94A3B8]"><span>{item.icon}</span><span>{item.label}</span></div>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-[#94A3B8] mt-6">30-day money-back guarantee. If Nudgit doesn&apos;t help you get paid, we refund you in full. No questions.</p>
      </div>
    </div>
  )
}
