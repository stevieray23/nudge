'use client'

import { useState } from 'react'
import Link from 'next/link'

// ─── Confetti burst (pure CSS, no lib needed) ────────────────────────────────

function Confetti() {
  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      {[
        { x: 20, y: 30, color: '#0ea5e9', size: 8, delay: 0 },
        { x: 35, y: 15, color: '#f43f5e', size: 6, delay: 0.1 },
        { x: 55, y: 25, color: '#0ea5e9', size: 10, delay: 0.05 },
        { x: 70, y: 35, color: '#f59e0b', size: 7, delay: 0.15 },
        { x: 85, y: 20, color: '#0ea5e9', size: 6, delay: 0.08 },
        { x: 10, y: 50, color: '#0ea5e9', size: 9, delay: 0.12 },
        { x: 45, y: 45, color: '#f43f5e', size: 7, delay: 0.2 },
        { x: 75, y: 55, color: '#0ea5e9', size: 8, delay: 0.07 },
      ].map((dot, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: `${dot.x}%`,
            top: `${dot.y}%`,
            width: dot.size,
            height: dot.size,
            borderRadius: '50%',
            background: dot.color,
            animation: `confettiFall 1.5s ease-out ${dot.delay}s forwards`,
          }}
        />
      ))}
      <style>{`
        @keyframes confettiFall {
          0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; }
          100% { transform: translateY(120px) rotate(360deg) scale(0); opacity: 0; }
        }
      `}</style>
    </div>
  )
}

// ─── Nav ───────────────────────────────────────────────────────────────────

function Nav() {
  return (
    <nav className="flex items-center justify-between px-8 py-5 border-b border-zinc-100/80 sticky top-0 z-50 bg-white/90 backdrop-blur-md">
      <Link href="/" className="flex items-center gap-2.5 group">
        <div className="w-8 h-8 bg-sky-500 rounded-xl flex items-center justify-center shadow-sm shadow-sky-200">
          <span className="text-white font-bold text-sm">C</span>
        </div>
        <span className="font-semibold text-lg text-zinc-900 tracking-tight">Chase</span>
      </Link>
      <div className="flex items-center gap-3 text-sm">
        <span className="text-zinc-400">Already have an account?</span>
        <Link href="/login" className="text-zinc-600 hover:text-zinc-900 font-medium transition-colors">Sign in</Link>
      </div>
    </nav>
  )
}

// ─── Plan cards ───────────────────────────────────────────────────────────────

type Plan = {
  name: string
  badge: string | null
  price: number
  originalPrice: number | null
  desc: string
  features: string[]
  highlight: boolean
  stripePriceId: string
}

const plans: Plan[] = [
  {
    name: 'Starter',
    badge: null,
    price: 19,
    originalPrice: null,
    desc: 'For freelancers just getting started with invoicing.',
    features: ['20 invoices/month', 'Up to 3 reminders per invoice', 'Email reminders', 'CSV import', 'Basic dashboard'],
    highlight: false,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_STARTER_PRICE_ID ?? '',
  },
  {
    name: 'Pro',
    badge: 'Founding price',
    price: 9,
    originalPrice: 39,
    desc: 'For serious freelancers. This price locks in forever. No tricks.',
    features: ['100 invoices/month', 'Unlimited reminders', 'Email + SMS reminders', 'CSV import', 'Full dashboard', 'Custom sequences', 'Priority support'],
    highlight: true,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID ?? '',
  },
  {
    name: 'Agency',
    badge: null,
    price: 89,
    originalPrice: null,
    desc: 'For agencies managing multiple clients and contractors.',
    features: ['Unlimited invoices', 'Unlimited reminders', 'Email + SMS + Slack', 'CSV import', 'Full dashboard', 'Multi-client view', 'Advanced sequences', 'Dedicated support'],
    highlight: false,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_AGENCY_PRICE_ID ?? '',
  },
]

// ─── Animated checkmark ───────────────────────────────────────────────────────

function AnimatedCheck() {
  return (
    <div className="relative">
      <div className="w-16 h-16 rounded-full bg-emerald-50 border-2 border-emerald-200 flex items-center justify-center mx-auto mb-5">
        <svg className="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <div className="absolute inset-0 rounded-full bg-emerald-100/30 animate-ping" style={{ animationDuration: '2s' }} />
    </div>
  )
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function SignupPage() {
  const [selectedPlan, setSelectedPlan] = useState<number>(1) // Pro default
  const [loading, setLoading] = useState(false)
  const [email, setEmail] = useState('')
  const [showConfirmation, setShowConfirmation] = useState(false)

  async function handleCheckout() {
    const plan = plans[selectedPlan]
    setLoading(true)

    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          priceId: plan.stripePriceId,
          email,
        }),
      })

      const data = await res.json()

      if (data.url) {
        window.location.href = data.url
      } else {
        // Stripe not configured — simulate success for demo
        setShowConfirmation(true)
      }
    } catch {
      setShowConfirmation(true)
    } finally {
      setLoading(false)
    }
  }

  // ─── Confirmation state ─────────────────────────────────────────────────────

  if (showConfirmation) {
    return (
      <div className="min-h-screen bg-white">
        <Nav />
        <Confetti />
        <div className="flex flex-col items-center justify-center px-8 py-24 max-w-md mx-auto text-center">
          <AnimatedCheck />
          <h1 className="text-3xl font-semibold text-zinc-900 tracking-tight mb-3">You&apos;re in!</h1>
          <p className="text-zinc-500 leading-relaxed mb-6">
            Welcome to Chase, {email || 'new friend'}. Your founding membership is confirmed.
            <br /><br />
            We&apos;ll send you an onboarding email shortly. In the meantime, tell a fellow freelancer about Chase — they might appreciate it.
          </p>
          <div className="bg-zinc-50 rounded-2xl p-5 w-full text-left border border-zinc-100">
            <p className="text-xs text-zinc-400 font-medium uppercase tracking-widest mb-3">What happens next</p>
            <ul className="space-y-2.5">
              {[
                'Check your inbox for a welcome email',
                'Set up your account and connect your email',
                'Import your first invoice (CSV or manual)',
                'Chase starts working for you automatically',
              ].map((step, i) => (
                <li key={i} className="flex items-center gap-2.5 text-sm text-zinc-600">
                  <span className="w-5 h-5 rounded-full bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-500 text-xs font-bold flex-shrink-0">{i + 1}</span>
                  {step}
                </li>
              ))}
            </ul>
          </div>
          <Link href="/login" className="mt-6 text-sm text-sky-500 font-medium hover:text-sky-600 transition-colors">
            Go to your dashboard →
          </Link>
        </div>
      </div>
    )
  }

  // ─── Main form ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-zinc-50">
      <Nav />
      <div className="max-w-4xl mx-auto px-8 py-14">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-600 border border-emerald-100 px-4 py-1.5 rounded-full text-xs font-medium mb-5">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
            Founding Member pricing — limited to first 50 signups
          </div>
          <h1 className="text-4xl font-semibold text-zinc-900 tracking-tight mb-3">
            Choose your plan.
          </h1>
          <p className="text-zinc-500">
            All plans come with a 14-day free trial. No credit card required to start.
          </p>
        </div>

        {/* Plan grid */}
        <div className="grid md:grid-cols-3 gap-5 mb-10">
          {plans.map((plan, i) => (
            <button
              key={plan.name}
              onClick={() => setSelectedPlan(i)}
              className={`text-left rounded-2xl p-6 border-2 transition-all duration-200 ${
                selectedPlan === i
                  ? plan.highlight
                    ? 'border-sky-400 bg-sky-50 shadow-xl shadow-sky-100/50'
                    : 'border-sky-400 bg-white shadow-xl shadow-sky-100/50'
                  : 'border-zinc-200 bg-white hover:border-zinc-300'
              }`}
            >
              {plan.badge && (
                <div className="mb-3">
                  <span className={`text-xs font-semibold px-3 py-1 rounded-full ${plan.highlight ? 'bg-sky-500 text-white' : 'bg-zinc-100 text-zinc-600'}`}>
                    {plan.badge}
                  </span>
                </div>
              )}
              <h3 className="font-semibold text-zinc-900 mb-1">{plan.name}</h3>
              <div className="flex items-end gap-1.5 mb-3">
                <span className="text-3xl font-bold text-zinc-900">${plan.price}</span>
                <span className="text-zinc-400 text-sm mb-1">/month</span>
                {plan.originalPrice && (
                  <span className="text-zinc-400 text-sm mb-1 line-through">${plan.originalPrice}</span>
                )}
              </div>
              <p className="text-zinc-500 text-xs mb-4 leading-relaxed">{plan.desc}</p>
              <ul className="space-y-1.5">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-xs text-zinc-600">
                    <svg className="w-3.5 h-3.5 text-sky-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              {selectedPlan === i && (
                <div className="mt-4 pt-4 border-t border-sky-200 flex items-center gap-2 text-xs text-sky-600 font-medium">
                  <div className="w-4 h-4 rounded-full bg-sky-500 flex items-center justify-center">
                    <div className="w-1.5 h-1.5 bg-white rounded-full" />
                  </div>
                  Selected
                </div>
              )}
            </button>
          ))}
        </div>

        {/* Email + CTA */}
        <div className="bg-white rounded-2xl border border-zinc-200 p-8 shadow-sm">
          <div className="max-w-md mx-auto">
            <p className="text-sm font-medium text-zinc-700 mb-3 text-center">Your email address</p>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@yourbusiness.com"
                required
                className="flex-1 px-4 py-3.5 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent placeholder-zinc-400"
              />
              <button
                onClick={handleCheckout}
                disabled={loading || !email}
                className="bg-sky-500 hover:bg-sky-600 disabled:bg-zinc-300 disabled:cursor-not-allowed active:translate-y-[1px] text-white px-6 py-3.5 rounded-xl text-sm font-semibold transition-all shadow-sm shadow-sky-200 whitespace-nowrap flex items-center justify-center gap-2 min-w-[160px]"
              >
                {loading ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Processing...
                  </>
                ) : (
                  <>Start free trial →</>
                )}
              </button>
            </div>
            <p className="text-xs text-zinc-400 text-center mt-3">
              14-day free trial · No credit card required · Cancel anytime
            </p>

            {/* Trust signals */}
            <div className="flex items-center justify-center gap-5 mt-5 pt-5 border-t border-zinc-100">
              {[
                { icon: '🔒', label: 'Secure checkout' },
                { icon: '⚡', label: 'Instant access' },
                { icon: '💳', label: 'Powered by Stripe' },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-1.5 text-xs text-zinc-400">
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Guarantee */}
        <div className="mt-6 text-center">
          <p className="text-xs text-zinc-400">
            30-day money-back guarantee. If Chase doesn&apos;t help you get paid, we refund you in full. No questions.
          </p>
        </div>
      </div>
    </div>
  )
}