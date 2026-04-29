import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Nudgit — Get paid without the awkwardness',
  description: 'Nudgit sends perfectly timed invoice reminders so freelancers stop losing money to forgotten payments. $9/mo founding price, locked for life. Start free trial.',
  keywords: ['invoice reminders', 'freelancer tools', 'get paid', 'invoice follow up', 'automated reminders'],
  authors: [{ name: 'Nudgit' }],
  openGraph: {
    title: 'Nudgit — Get paid without the awkwardness',
    description: 'Automated invoice reminders for freelancers. Stop losing $4,200/year to forgotten invoices.',
    url: 'https://nudgeit.pro',
    siteName: 'Nudgit',
    type: 'website',
    locale: 'en_US',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Nudgit — Get paid without the awkwardness',
    description: 'Stop losing money to forgotten invoices. $9/mo founding price, locked for life.',
    site: '@nudgitapp',
  },
  icons: {
    icon: '/logo.png',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased min-h-screen bg-white text-black">
        {children}
      </body>
    </html>
  )
}
