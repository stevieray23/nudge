'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

// ─── Types ─────────────────────────────────────────────────────────────────────

type InvoiceStatus = 'pending' | 'sent' | 'paid' | 'overdue'

interface Invoice {
  id: string
  client_name: string
  client_email: string
  amount: number
  due_date: string
  status: string
  reminder_count: number
  last_reminder_at: string | null
  created_at: string
}

type FilterTab = 'all' | 'overdue' | 'pending' | 'paid'

// ─── Status config ─────────────────────────────────────────────────────────────

const statusConfig: Record<string, { label: string; bg: string; text: string; dot: string }> = {
  overdue: { label: 'Overdue', bg: 'bg-red-50', text: 'text-red-600', dot: 'bg-red-400' },
  pending: { label: 'Pending', bg: 'bg-amber-50', text: 'text-amber-600', dot: 'bg-amber-400' },
  sent: { label: 'Sent', bg: 'bg-sky-50', text: 'text-sky-600', dot: 'bg-sky-400' },
  paid: { label: 'Paid', bg: 'bg-emerald-50', text: 'text-emerald-600', dot: 'bg-emerald-400' },
}

// ─── Helpers ───────────────────────────────────────────────────────────────────

function getInvoiceStatus(invoice: Invoice): string {
  if (invoice.status === 'paid') return 'paid'
  const due = new Date(invoice.due_date)
  const now = new Date()
  const diff = Math.floor((now.getTime() - due.getTime()) / (1000 * 60 * 60 * 24))
  return diff > 0 ? 'overdue' : 'pending'
}

function formatAmount(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`
}

function formatDue(date: string): string {
  const d = new Date(date)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatRelativeTime(isoString: string | null): string | null {
  if (!isoString) return null
  const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / (1000 * 60 * 60 * 24))
  if (diff === 0) return 'today'
  if (diff === 1) return 'yesterday'
  return `${diff} days ago`
}

// ─── Nav ───────────────────────────────────────────────────────────────────────

function DashboardNav() {
  return (
    <nav className="bg-white border-b border-zinc-100 px-6 py-3.5 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-7 h-7 bg-sky-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xs">C</span>
          </div>
          <span className="font-semibold text-zinc-900 tracking-tight">Chase</span>
        </Link>
        <div className="flex items-center gap-1 text-sm">
          {['Dashboard', 'Clients', 'Invoices', 'Reminders'].map((item) => (
            <button key={item} className={`px-3 py-1.5 rounded-lg transition-colors ${item === 'Dashboard' ? 'bg-zinc-900 text-white' : 'text-zinc-500 hover:text-zinc-900 hover:bg-zinc-50'}`}>
              {item}
            </button>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button className="text-zinc-400 hover:text-zinc-600 transition-colors">
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 17h5.001c.45-.32.749-.76.877-1.28a3 3 0 10-4.163-3.08 4 4 0 00-.713 1.36c0 .67.21 1.3.58 1.84l.06.1V20a1 1 0 01-.94 1h-4.58a1 1 0 01-.94-1v-1h-4v1a1 1 0 01-.94 1H4a1 1 0 01-.94-1v-1.66c.37-.54.58-1.17.58-1.84 0-.92-.37-1.79-1-2.44a4 4 0 00-.713-1.36 3 3 0 10-4.163 3.08c.128.52.427.96.877 1.28A1 1 0 003 17h3.001v1a1 1 0 001 1h1a1 1 0 001-1v-1h4v1a1 1 0 001 1h1a1 1 0 001-1v-1h5.001v-1.84l.06-.1a2.27 2.27 0 00.58-1.84 2.27 2.27 0 00-.58-1.84A2.27 2.27 0 0016 5.4a2.27 2.27 0 00-.59 1.19" />
          </svg>
        </button>
        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-sm font-semibold text-zinc-600 cursor-pointer hover:bg-slate-300 transition-colors">
          S
        </div>
      </div>
    </nav>
  )
}

// ─── Stat cards ────────────────────────────────────────────────────────────────

function StatCards({ invoices, filter }: { invoices: Invoice[]; filter: FilterTab }) {
  const totalOutstanding = invoices
    .filter(i => getInvoiceStatus(i) !== 'paid')
    .reduce((sum, i) => sum + i.amount, 0)
  const overdueCount = invoices.filter(i => getInvoiceStatus(i) === 'overdue').length
  const overdueAmount = invoices
    .filter(i => getInvoiceStatus(i) === 'overdue')
    .reduce((sum, i) => sum + i.amount, 0)
  const paidThisMonth = invoices
    .filter(i => i.status === 'paid')
    .reduce((sum, i) => sum + i.amount, 0)
  const pendingCount = invoices.filter(i => getInvoiceStatus(i) === 'pending').length

  const stats = [
    {
      label: 'Total outstanding',
      value: formatAmount(totalOutstanding),
      sub: `+${pendingCount} new this week`,
      color: 'text-zinc-900',
      icon: (
        <svg className="w-4 h-4 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      label: 'Invoices overdue',
      value: String(overdueCount),
      sub: `⚠️ ${formatAmount(overdueAmount)} overdue`,
      color: 'text-red-500',
      icon: (
        <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
    },
    {
      label: 'Paid this month',
      value: formatAmount(paidThisMonth),
      sub: '+1 vs last month',
      color: 'text-emerald-600',
      icon: (
        <svg className="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      label: 'Avg. days to payment',
      value: '14',
      sub: '↘ 3 days faster this month',
      color: 'text-sky-600',
      icon: (
        <svg className="w-4 h-4 text-sky-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      ),
    },
  ]

  if (filter !== 'all') {
    const filteredStats = filter === 'overdue'
      ? [stats[0], stats[1]]
      : filter === 'paid'
      ? [stats[0], stats[2]]
      : [stats[0], stats[3]]
    return (
      <div className="grid grid-cols-4 gap-4 mb-6">
        {filteredStats.map((s) => (
          <div key={s.label} className="bg-white rounded-xl border border-zinc-100 p-4">
            <div className="flex items-center gap-1.5 text-xs text-zinc-400 mb-1.5">
              {s.icon}
              {s.label}
            </div>
            <p className={`text-2xl font-semibold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-zinc-400 mt-0.5">{s.sub}</p>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-4 gap-4 mb-6">
      {stats.map((s) => (
        <div key={s.label} className="bg-white rounded-xl border border-zinc-100 p-4">
          <div className="flex items-center gap-1.5 text-xs text-zinc-400 mb-1.5">
            {s.icon}
            {s.label}
          </div>
          <p className={`text-2xl font-semibold ${s.color}`}>{s.value}</p>
          <p className="text-xs text-zinc-400 mt-0.5">{s.sub}</p>
        </div>
      ))}
    </div>
  )
}

// ─── Invoice row ───────────────────────────────────────────────────────────────

function InvoiceRow({ invoice, onUpdate }: { invoice: Invoice; onUpdate: (id: string, status: string) => void }) {
  const [loading, setLoading] = useState(false)
  const displayStatus = getInvoiceStatus(invoice)
  const s = statusConfig[displayStatus] ?? statusConfig.pending

  const handleSendReminder = async () => {
    setLoading(true)
    try {
      await fetch(`/api/cron/reminders?id=${invoice.id}`, { method: 'POST' })
    } finally {
      setLoading(false)
    }
  }

  const handleMarkPaid = async () => {
    setLoading(true)
    try {
      await onUpdate(invoice.id, 'paid')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl border border-zinc-100 px-5 py-4 flex items-center justify-between hover:border-zinc-200 hover:shadow-sm transition-all">
      <div className="flex items-center gap-4 flex-1 min-w-0">
        <div className={`w-2 h-2 rounded-full flex-shrink-0 ${s.dot}`} />
        <div className="min-w-0 flex-1">
          <p className="font-medium text-zinc-900 text-sm truncate">{invoice.client_name}</p>
          <p className="text-xs text-zinc-400 truncate">{invoice.client_email}</p>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="text-right hidden sm:block">
          <p className="text-sm font-semibold text-zinc-900">{formatAmount(invoice.amount)}</p>
          <p className="text-xs text-zinc-400">Due {formatDue(invoice.due_date)}</p>
        </div>

        <div className="hidden md:flex items-center gap-1 text-xs text-zinc-400">
          {invoice.reminder_count > 0 ? (
            <>
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              <span>{invoice.reminder_count} sent {formatRelativeTime(invoice.last_reminder_at) ? `· ${formatRelativeTime(invoice.last_reminder_at)}` : ''}</span>
            </>
          ) : (
            <span className="text-zinc-300">No reminders yet</span>
          )}
        </div>

        <div className={`text-xs px-2.5 py-1 rounded-full font-medium border ${s.bg} ${s.text} border-transparent`}>
          {s.label}
        </div>

        <div className="flex items-center gap-1">
          {displayStatus !== 'paid' && (
            <>
              <button
                onClick={handleSendReminder}
                disabled={loading}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-sky-500 hover:bg-sky-50 transition-all disabled:opacity-50"
                title="Send reminder"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
              <button
                onClick={handleMarkPaid}
                disabled={loading}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-emerald-500 hover:bg-emerald-50 transition-all disabled:opacity-50"
                title="Mark as paid"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </button>
            </>
          )}
          {displayStatus === 'paid' && (
            <div className="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center">
              <svg className="w-4 h-4 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ─── Add invoice modal ─────────────────────────────────────────────────────────

interface AddModalProps {
  onClose: () => void
  onAdded: () => void
}

function AddInvoiceModal({ onClose, onAdded }: AddModalProps) {
  const [clientName, setClientName] = useState('')
  const [clientEmail, setClientEmail] = useState('')
  const [amount, setAmount] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await fetch('/api/invoices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_name: clientName,
          client_email: clientEmail,
          amount: parseFloat(amount),
          due_date: dueDate,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.error || 'Failed to add invoice')
        return
      }
      onAdded()
      onClose()
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-6 border-b border-zinc-100">
          <h2 className="text-lg font-semibold text-zinc-900">Add invoice</h2>
          <button onClick={onClose} className="text-zinc-400 hover:text-zinc-600 transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-4">
            {error && (
              <div className="bg-red-50 text-red-600 text-sm px-4 py-2.5 rounded-xl border border-red-100">
                {error}
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-1.5">Client name</label>
              <input
                type="text"
                placeholder="e.g. Meridian Design Co."
                value={clientName}
                onChange={(e) => setClientName(e.target.value)}
                required
                className="w-full px-4 py-2.5 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-1.5">Client email</label>
              <input
                type="email"
                placeholder="e.g. accounts@meridian.co"
                value={clientEmail}
                onChange={(e) => setClientEmail(e.target.value)}
                required
                className="w-full px-4 py-2.5 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-zinc-700 mb-1.5">Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="850"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-700 mb-1.5">Due date</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  required
                  className="w-full px-4 py-2.5 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400"
                />
              </div>
            </div>
          </div>
          <div className="flex gap-3 p-6 border-t border-zinc-100">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl text-sm font-medium border border-zinc-200 text-zinc-600 hover:bg-zinc-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2.5 rounded-xl text-sm font-semibold bg-sky-500 hover:bg-sky-600 text-white transition-colors disabled:opacity-50"
            >
              {loading ? 'Adding...' : 'Add invoice →'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ─── Main ──────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [filter, setFilter] = useState<FilterTab>('all')
  const [showAddModal, setShowAddModal] = useState(false)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)

  const fetchInvoices = async () => {
    try {
      const res = await fetch('/api/invoices')
      const data = await res.json()
      if (res.ok) setInvoices(data.invoices || [])
    } catch {
      // fail silently, show empty
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchInvoices()
  }, [])

  const handleUpdate = async (id: string, status: string) => {
    try {
      const res = await fetch(`/api/invoices/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status }),
      })
      if (res.ok) {
        await fetchInvoices()
      }
    } catch {
      // fail silently
    }
  }

  const getFiltered = () => {
    if (filter === 'all') return invoices
    return invoices.filter(i => getInvoiceStatus(i) === filter)
  }

  const filtered = getFiltered()
  const overdueCount = invoices.filter(i => getInvoiceStatus(i) === 'overdue').length
  const pendingCount = invoices.filter(i => getInvoiceStatus(i) === 'pending').length

  return (
    <div className="min-h-screen bg-zinc-50">
      <DashboardNav />

      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-semibold text-zinc-900 tracking-tight">Invoices</h1>
            <p className="text-zinc-500 text-sm mt-0.5">
              {loading ? 'Loading...' : `${overdueCount} overdue and ${pendingCount} pending.`}
            </p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-sky-500 hover:bg-sky-600 active:translate-y-[1px] text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-all shadow-sm shadow-sky-200 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            Add invoice
          </button>
        </div>

        {/* Stat cards */}
        <StatCards invoices={invoices} filter={filter} />

        {/* Filter tabs */}
        <div className="flex items-center gap-1 mb-4 bg-zinc-100 p-1 rounded-xl w-fit">
          {(['all', 'overdue', 'pending', 'paid'] as FilterTab[]).map((tab) => {
            const count = tab === 'all'
              ? invoices.length
              : invoices.filter(i => getInvoiceStatus(i) === tab).length
            return (
              <button
                key={tab}
                onClick={() => setFilter(tab)}
                className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  filter === tab ? 'bg-white text-zinc-900 shadow-sm' : 'text-zinc-500 hover:text-zinc-700'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
                <span className="ml-1.5 text-zinc-400">({count})</span>
              </button>
            )
          })}
        </div>

        {/* Invoice list */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-6 h-6 border-2 border-sky-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-dashed border-zinc-200">
            <div className="text-4xl mb-3">📭</div>
            <p className="text-zinc-500 text-sm">No {filter} invoices</p>
            <button onClick={() => setShowAddModal(true)} className="mt-3 text-sky-500 text-sm font-medium hover:text-sky-600 transition-colors">
              + Add your first invoice
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((invoice) => (
              <InvoiceRow key={invoice.id} invoice={invoice} onUpdate={handleUpdate} />
            ))}
          </div>
        )}
      </div>

      {/* Add invoice modal */}
      {showAddModal && (
        <AddInvoiceModal
          onClose={() => setShowAddModal(false)}
          onAdded={fetchInvoices}
        />
      )}
    </div>
  )
}