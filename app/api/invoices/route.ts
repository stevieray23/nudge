import { NextResponse } from 'next/server'
import { supabase } from '../../lib/supabase'

export async function GET() {
  try {
    const { data: invoices, error } = await supabase
      .from('invoices')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 400 })
    }
    
    return NextResponse.json({ invoices })
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 })
  }
}