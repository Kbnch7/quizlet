import { ReactNode } from 'react';
import { Footer } from '../footer';
import { Navbar } from '../navbar';

export function MainLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex flex-col min-h-dvh w-full">
      <Navbar />
      {children}
      <Footer />
    </div>
  );
}
