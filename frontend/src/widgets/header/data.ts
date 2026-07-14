export type HeaderNavItem = {
  label: string;
  href: string;
};

export const HEADER_NAV: HeaderNavItem[] = [
  { label: "О нас", href: "/#about" },
  { label: "Услуги", href: "/#services" },
  { label: "Партнёры", href: "/#partners" },
  { label: "Разрешительные документы", href: "/#documents" },
  {
    label: "Сведения об образовательной организации",
    href: "/svedeniya",
  },
  { label: "Общественные обсуждения", href: "/obshchestvennye-obsuzhdeniya" },
  { label: "Контакты", href: "/#contacts" },
];
