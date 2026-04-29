import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'

// One-time price map — creates checkout sessions directly
const PRICE_MAP: Record<string, { amount: number; name: string; desc: string }> = {
  onetime_starter:  { amount: 1900, name: 'Nudgit Starter',     desc: '20 invoices/mo, email reminders, CSV import' },
  onetime_lifetime: { amount: 2900, name: 'Nudgit Lifetime',    desc: 'Unlimited invoices, all features, lifetime access' },
  onetime_agency:   { amount: 8900, name: 'Nudgit Agency',      desc: 'Multi-client, all features, priority support' },
}

export async function POST(req: NextRequest) {
  try {
    const { priceId, email } = await req.json()

    if (!email) return NextResponse.json({ error: 'Missing email' }, { status: 400 })

    const stripeKey = process.env.STRIPE_SECRET_KEY
    if (!stripeKey) {
      // Stripe not configured — simulate success for demo
      return NextResponse.json({ configured: false }, { status: 200 })
    }

    const stripe = new Stripe(stripeKey, { apiVersion: '2026-04-22.dahlia' })
    const origin = req.headers.get('origin') ?? 'https://nudgeit.pro'

    const priceData = PRICE_MAP[priceId]
    if (!priceData) return NextResponse.json({ error: 'Unknown price ID' }, { status: 400 })

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      payment_method_types: ['card'],
      line_items: [{
        quantity: 1,
        price_data: {
          currency: 'usd',
          unit_amount: priceData.amount,
          product_data: {
            name: priceData.name,
            description: priceData.desc,
          },
        },
      }],
      customer_email: email,
      success_url: `${origin}/signup?success=true`,
      cancel_url: `${origin}/signup?canceled=true`,
      metadata: { priceId },
    })

    return NextResponse.json({ url: session.url }, { status: 200 })
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error('[checkout]', message)
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
