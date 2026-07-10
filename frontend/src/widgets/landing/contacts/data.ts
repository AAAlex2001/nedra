import { COMPANY_CONTACTS } from "@/shared/config/company";

export const CONTACTS_DATA = {
  title: "Наши контакты",
  director: {
    label: "Директор",
    value: "Самохин Сергей Владимирович",
  },
  phone: COMPANY_CONTACTS.phone,
  phoneHref: COMPANY_CONTACTS.phoneHref,
  email: COMPANY_CONTACTS.email,
  address: COMPANY_CONTACTS.address,
  schedule: "Режим работы: с 08:30 до 17:00 (UTC +7)",
  // Запрос для геокодера Яндекс.Карт — по нему ставится метка на карте.
  mapQuery: "Новосибирск, улица Кирова, 113/2",
};
