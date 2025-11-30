import { ReactNode } from 'react';
import { Footer } from '../footer';
import { Navbar } from '../navbar';

export function MainLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid grid-rows-[auto_1fr_auto] items-center justify-items-center min-h-dvh w-full">
      <Navbar />
      {children}
      <div></div>
      <Footer />
    </div>
  );
}
