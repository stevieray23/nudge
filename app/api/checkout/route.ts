import { NextRequest, NextResponse } from 'next/server'
import Stripe from 'stripe'

export async function POST(req: NextRequest) {
  try {
    const { priceId, email } = await req.json()

    if (!priceId || !email) {
      return NextResponse.json({ error: 'Missing priceId or email' }, { status: 400 })
    }

    const stripeSecretKey = process.env.STRIPE_SECRET_KEY

    if (!stripeSecretKey) {
      return NextResponse.json({ error: 'Stripe not configured' }, { status: 500 })
    }

    const stripe = new Stripe(stripeSecretKey, {
      apiVersion: '2026-04-22.dahlia',
    })

    const origin = req.headers.get('origin') ?? 'http://localhost:3000'

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      customer_email: email,
      success_url: `${origin}/signup?success=true&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/signup?canceled=true`,
      subscription_data: {
        metadata: { onboarding_source: 'nudge_landing' },
      },
    })

    return NextResponse.json({ url: session.url }, { status: 200 })
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error('[checkout]', message)
    return NextResponse.json({ error: message }, { status: 500 })
  }
}
