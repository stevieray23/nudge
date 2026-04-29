import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Chase — Get Paid Without the Awkwardness',
  description: 'Automated invoice reminders for freelancers and small service businesses. Never lose money to forgotten invoices again.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen bg-white text-slate-900">
        {children}
      </body>
    </html>
  )
}