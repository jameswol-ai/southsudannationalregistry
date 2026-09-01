import type {Metadata} from 'next';
import './globals.css'; // Global styles

export const metadata: Metadata = {
  title: 'South Sudan National Registry',
  description: 'Official national population census, civil registry, administrative hierarchy (State, County, Payam, Boma), and electoral roll portal for the Republic of South Sudan.',
  openGraph: {
    title: 'South Sudan National Registry',
    description: 'Official national population census, civil registry, administrative hierarchy (State, County, Payam, Boma), and electoral roll portal for the Republic of South Sudan.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'South Sudan National Registry',
    description: 'Official national population census, civil registry, administrative hierarchy (State, County, Payam, Boma), and electoral roll portal for the Republic of South Sudan.',
  },
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
