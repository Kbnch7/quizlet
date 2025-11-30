import { MainLayout } from '@/components/layouts/main-layout';
import { QueryProvider } from '@/components/providers/query.provider';
import { ThemeProvider } from '@/components/providers/theme.provider';
import { ZustandProvider } from '@/components/providers/zustand.provider';
import { SidebarProvider } from '@/components/ui/sidebar';
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
          <SidebarProvider>
            <ThemeProvider attribute={'class'} defaultTheme={'system'}>
              <QueryProvider>
                <ZustandProvider>
                  <MainLayout>{children}</MainLayout>
                </ZustandProvider>
              </QueryProvider>
            </ThemeProvider>
          </SidebarProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
