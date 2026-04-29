'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    // Supabase not wired yet — simulate a moment then redirect
    await new Promise(r => setTimeout(r, 800))
    window.location.href = '/dashboard'
  }

  return (
    <div className="min-h-screen bg-zinc-50 flex flex-col">
      {/* Nav */}
      <nav className="px-8 py-5 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <img src="/logo.png" alt="Nudgit" className="h-8 w-auto object-contain" />
          <span className="font-semibold text-lg text-[#18181B] tracking-tight">Nudgit</span>
        </Link>
        <Link href="/signup" className="text-sm text-zinc-500 hover:text-zinc-700 transition-colors">
          Don&apos;t have an account?
        </Link>
      </nav>

      {/* Form */}
      <div className="flex-1 flex items-center justify-center px-8 py-12">
        <div className="w-full max-w-sm">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-semibold text-zinc-900 tracking-tight mb-2">Welcome back</h1>
            <p className="text-zinc-500 text-sm">Sign in to your Chase account</p>
          </div>

          <form onSubmit={handleLogin} className="bg-white rounded-2xl border border-zinc-200 p-8 shadow-sm space-y-4">
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@yourbusiness.com"
                required
                className="w-full px-4 py-3 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent placeholder-zinc-400"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-zinc-700 mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-3 border border-zinc-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent placeholder-zinc-400"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-zinc-900 hover:bg-zinc-800 disabled:bg-zinc-300 text-white py-3 rounded-xl text-sm font-semibold transition-all active:translate-y-[1px] flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Signing in...
                </>
              ) : 'Sign in'}
            </button>
          </form>

          <p className="text-center text-xs text-zinc-400 mt-4">
            <a href="#" className="hover:text-zinc-600 transition-colors">Forgot your password?</a>
          </p>
        </div>
      </div>
    </div>
  )
}