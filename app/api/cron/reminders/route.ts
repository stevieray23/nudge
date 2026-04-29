import { NextResponse } from 'next/server'
import { supabase } from '../../../lib/supabase'
import { sendReminder } from '../../../lib/reminders'

export async function GET() {
  const { data: invoices } = await supabase
    .from('invoices')
    .select('id, due_date, status')
    .eq('status', 'pending')
  
  for (const invoice of invoices ?? []) {
    const due = new Date(invoice.due_date)
    const daysDiff = Math.floor((Date.now() - due.getTime()) / (1000 * 60 * 60 * 24))
    if (daysDiff >= -3 && invoice.status === 'pending') {
      // Send reminder (don't send more than once per day)
      await sendReminder(invoice.id)
    }
  }
  
  return NextResponse.json({ processed: (invoices ?? []).length })
}