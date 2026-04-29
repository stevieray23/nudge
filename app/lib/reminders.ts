import { Resend } from 'resend'
import { supabase } from './supabase'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function sendReminder(invoiceId: string) {
  const { data: invoice } = await supabase
    .from('invoices')
    .select('*')
    .eq('id', invoiceId)
    .single()
  
  if (!invoice || invoice.status === 'paid') return

  const daysOverdue = Math.floor(
    (Date.now() - new Date(invoice.due_date).getTime()) / (1000 * 60 * 60 * 24)
  )

  let subject = ''
  let body = ''

  if (daysOverdue <= 0) {
    subject = `Invoice #${invoice.id.slice(0,8)} — due ${invoice.due_date}`
    body = `Hi ${invoice.client_name},\n\nJust a heads-up: your invoice for $${(invoice.amount/100).toFixed(2)} is due on ${invoice.due_date}.\n\nHere's the link: ${process.env.NEXT_PUBLIC_BASE_URL}/pay/${invoice.id}\n\nHappy to answer any questions.\n—`
  } else if (daysOverdue <= 3) {
    subject = `Invoice #${invoice.id.slice(0,8)} — ${daysOverdue} days overdue`
    body = `Hi ${invoice.client_name},\n\nJust a friendly nudge: your invoice for $${(invoice.amount/100).toFixed(2)} is ${daysOverdue} days overdue.\n\nNo stress — here's the link: ${process.env.NEXT_PUBLIC_BASE_URL}/pay/${invoice.id}\n\n—`
  } else {
    subject = `Invoice #${invoice.id.slice(0,8)} — overdue by ${daysOverdue} days`
    body = `Hi ${invoice.client_name},\n\nYour invoice for $${(invoice.amount/100).toFixed(2)} is ${daysOverdue} days overdue. Please arrange payment at your earliest convenience.\n\nLink: ${process.env.NEXT_PUBLIC_BASE_URL}/pay/${invoice.id}\n\n—`
  }

  await resend.emails.send({
    from: 'Nudgit <hello@nudgit.app>',
    to: invoice.client_email,
    subject,
    text: body,
  })

  await supabase.from('invoices').update({ reminder_count: invoice.reminder_count + 1, last_reminder_at: new Date().toISOString() }).eq('id', invoiceId)
}