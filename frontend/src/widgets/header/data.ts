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
  {
    label: "Институт",
    id: "institute",
    children: [
      { label: "О нас", href: "/#about", description: "Знакомство с НПИ «Недра»" },
      { label: "Партнёры", href: "/#partners", description: "Компании, с которыми мы работаем" },
    ],
  },
  { label: "Услуги", href: "/#services" },
  {
    label: "Документы",
    id: "documents",
    children: [
      { label: "Разрешительные документы", href: "/#documents", description: "Лицензии, свидетельства и сертификаты" },
      { label: "Сведения об образовательной организации", href: "/svedeniya", description: "Официальная информация об обучении" },
      { label: "Общественные обсуждения", href: "/obshchestvennye-obsuzhdeniya", description: "Материалы проектов и обсуждений" },
    ],
  },
  {
    label: "Контент",
    id: "content",
    children: [
      { label: "Блог", href: "/blog", description: "Экспертные статьи и полезные материалы" },
      { label: "Новости", href: "/novosti", description: "События института и новости отрасли" },
    ],
  },
  { label: "Контакты", href: "/#contacts" },
];

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
  { label: "Блог", href: "/blog" },
  { label: "Новости", href: "/novosti" },
  { label: "Контакты", href: "/#contacts" },
];
