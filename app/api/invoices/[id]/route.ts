import { NextResponse } from 'next/server'
import { supabase } from '../../../lib/supabase'

export async function PATCH(request: Request) {
  try {
    const { id, status } = await request.json()
    
    const { data, error } = await supabase
      .from('invoices')
      .update({ status })
      .eq('id', id)
      .select()
      .single()
    
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 400 })
    }
    
    return NextResponse.json({ invoice: data })
  } catch {
    return NextResponse.json({ error: 'Invalid request' }, { status: 400 })
  }
}