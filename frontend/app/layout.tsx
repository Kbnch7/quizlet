import { MainLayout } from '@/components/layouts/main-layout';
import { ThemeProvider } from '@/components/providers/theme.provider';
import { TooltipProvider } from '@/components/ui/tooltip';
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Ruzlet',
  description: 'Ruzlet is a tool for creating and studying flashcards.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning={true}>
      <body className={`antialiased`}>
        <TooltipProvider>
          <ThemeProvider attribute={'class'} defaultTheme={'system'}>
            <MainLayout>{children}</MainLayout>
          </ThemeProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
