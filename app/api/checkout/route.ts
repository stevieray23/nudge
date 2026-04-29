import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  try {
    const { priceId, email } = await req.json()

    const stripeSecretKey = process.env.STRIPE_SECRET_KEY

    // Stripe not configured — return a signal to frontend to show confirmation
    if (!stripeSecretKey || stripeSecretKey === 'placeholder') {
      return NextResponse.json({ configured: false }, { status: 200 })
    }

    // Dynamically import stripe to avoid build errors when key is missing
    const Stripe = (await import('stripe')).default
    const stripe = new Stripe(stripeSecretKey, { apiVersion: '2025-03-31.basil' })

    const session = await stripe.checkout.sessions.create({
      mode: 'subscription',
      payment_method_types: ['card'],
      line_items: [{ price: priceId, quantity: 1 }],
      customer_email: email,
      success_url: `${req.headers.get('origin') ?? 'http://localhost:3000'}/signup?success=true`,
      cancel_url: `${req.headers.get('origin') ?? 'http://localhost:3000'}/signup?canceled=true`,
    })

    return NextResponse.json({ url: session.url }, { status: 200 })
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    console.error('[checkout]', message)
    return NextResponse.json({ error: message }, { status: 500 })
  }
}