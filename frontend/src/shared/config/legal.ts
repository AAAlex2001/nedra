export const LEGAL_PAGES = {
  privacy: { href: "/politika-konfidencialnosti", label: "Политика конфиденциальности" },
  agreement: { href: "/polzovatelskoe-soglashenie", label: "Пользовательское соглашение" },
  consent: {
    href: "/soglasie-na-obrabotku-personalnyh-dannyh",
    label: "Согласие на обработку персональных данных",
  },
  offer: { href: "/publichnaya-oferta", label: "Публичная оферта" },
};

export const LEGAL_LINKS = [
  LEGAL_PAGES.privacy,
  LEGAL_PAGES.agreement,
  LEGAL_PAGES.consent,
  LEGAL_PAGES.offer,
];
