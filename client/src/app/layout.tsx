import './globals.css';

export const metadata = {
  title: 'BidShield - Procurement Fraud Detection',
  description: 'Government procurement bid ring detection and fraud prevention',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-full flex flex-col bg-gray-50" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}