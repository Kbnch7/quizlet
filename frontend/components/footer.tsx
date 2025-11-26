import { AccessibleIcon } from '@radix-ui/react-accessible-icon';
import Image from 'next/image';

export function Footer() {
  const currentYear = new Date().getFullYear();
  return (
    <footer className="p-2 flex items-center justify-center">
      <AccessibleIcon label="">
        <Image src="/favicon.ico" alt="Ruzlet" width={32} height={32} />
      </AccessibleIcon>
      <p className="text-muted-foreground">© {currentYear} Ruzlet.</p>
    </footer>
  );
}
