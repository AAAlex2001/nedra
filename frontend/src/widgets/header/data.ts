export type HeaderNavItem = {
  label: string;
  href: string;
};

type DesktopNavItem = HeaderNavItem | {
  label: string;
  id: string;
  children: (HeaderNavItem & { description: string })[];
};

export const DESKTOP_NAV: DesktopNavItem[] = [
  { label: "О нас", href: "/#about" },
  { label: "Услуги", href: "/uslugi" },
  { label: "Сведения об образовательной организации", href: "/svedeniya" },
  { label: "Разрешительные документы", href: "/#documents" },
  { label: "Общественные обсуждения", href: "/obshchestvennye-obsuzhdeniya" },
  {
    label: "Контент",
    id: "content",
    children: [
      { label: "Блог", href: "/blog", description: "Экспертные статьи и полезные материалы" },
      { label: "Новости", href: "/novosti", description: "События института и новости отрасли" },
    ],
  },
  {
    label: "Сервисы",
    id: "blitz",
    children: [
      { label: "Блиц-эксперт", href: "/blits-ekspert", description: "Экспертиза промышленной безопасности онлайн" },
      { label: "Блиц-аудит", href: "/blits-audit", description: "Аудит системы управления промышленной безопасностью" },
    ],
  },
  { label: "Контакты", href: "/#contacts" },
];

export const HEADER_NAV: HeaderNavItem[] = [
  { label: "О нас", href: "/#about" },
  { label: "Услуги", href: "/uslugi" },
  { label: "Партнёры", href: "/#partners" },
  { label: "Разрешительные документы", href: "/#documents" },
  {
    label: "Сведения об образовательной организации",
    href: "/svedeniya",
  },
  { label: "Общественные обсуждения", href: "/obshchestvennye-obsuzhdeniya" },
  { label: "Блог", href: "/blog" },
  { label: "Новости", href: "/novosti" },
  { label: "Контакты", href: "/#contacts" },
];
