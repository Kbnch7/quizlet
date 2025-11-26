import { MainLayout } from '@/components/layouts/main-layout';
import { ThemeProvider } from '@/components/providers/theme.provider';
import { ZustandProvider } from '@/components/providers/zustand.provider';
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
            <ZustandProvider>
              <MainLayout>{children}</MainLayout>
            </ZustandProvider>
          </ThemeProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
