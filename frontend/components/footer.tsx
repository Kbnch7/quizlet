export function Footer() {
  const currentYear = new Date().getFullYear();
  return (
    <footer className="flex items-center justify-center">
      <p>© {currentYear} Ruzlet.</p>
    </footer>
  );
}
