import { COMPANY_CONTACTS } from "@/shared/config/company";
import type { DocLink } from "@/shared/ui/docs-card";
import type { InfoRow } from "@/shared/ui/info-card";

export const OSNOVNYE_SVEDENIYA = {
  title: "Основные сведения",
  info: [
    {
      label: "Полное наименование учреждения",
      value:
        "Общество с ограниченной ответственностью „Научный проектно-экспертный институт «Недра» (ООО «НПИ «Недра»)",
    },
    { label: "Дата создания", value: "25 марта 2016 года" },
    {
      label: "Учредителем ООО „НПИ «Недра» является",
      value: "Самохин Александр Владимирович",
    },
    { label: "Директор", value: "Самохин Александр Владимирович" },
    { label: "Юридический адрес", value: COMPANY_CONTACTS.address },
    { label: "Режим работы", value: "с 08:30 до 17:00" },
    { label: "Телефон", value: COMPANY_CONTACTS.phone },
    { label: "Почта", value: COMPANY_CONTACTS.email },
    {
      label: "Лицензия на осуществление образовательной деятельности",
      value: "№ Л035–01199–54/01139236 от 22.04.2024",
      href: "https://disk.yandex.ru/i/sYxQpjGqi6PecQ",
    },
  ] as InfoRow[],
  docsTitle: "Документы",
  docs: [
    { label: "1 Устав+Изменения", kind: "pdf", href: "https://disk.yandex.ru/i/wOZyfqMERt3wjQ" },
    { label: "1 Устав+Изменения", kind: "sign", href: "https://disk.yandex.ru/d/hPAPsJrP3NbTEw" },
    { label: "2 Лицензия (выписка) от 22.04.2024 образование", kind: "pdf", href: "https://disk.yandex.ru/i/sYxQpjGqi6PecQ" },
    { label: "2 Лицензия (выписка) от 22.04.2024 образование", kind: "sign", href: "https://disk.yandex.ru/d/bAsm4EontGPvBw" },
    { label: "3 ИНН ОГРН Недра", kind: "pdf", href: "https://disk.yandex.ru/i/30ZrdfS1REhGUg" },
    { label: "3 ИНН ОГРН Недра", kind: "sign", href: "https://disk.yandex.ru/d/su3JsraovdfALg" },
  ] as DocLink[],
};
