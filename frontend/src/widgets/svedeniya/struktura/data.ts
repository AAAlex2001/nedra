import { COMPANY_CONTACTS } from "@/shared/config/company";
import type { DocLink } from "@/shared/ui/docs-card";
import type { InfoRow } from "@/shared/ui/info-card";

export const SVEDENIYA_STRUKTURA = {
  title: "Структура и органы управления образовательной организацией",
  info: [
    {
      label: "Организационно-правовая форма",
      value: "Общество с ограниченной ответственностью",
    },
    {
      label: "Высший орган управления организацией",
      value: "Единственный Учредитель – Самохин Александр Владимирович",
    },
    {
      label: "Единоличный исполнительный орган",
      value: "Директор – Самохин Александр Владимирович",
    },
    { label: "Директор", value: "Самохин Александр Владимирович" },
    { label: "Единый телефон", value: COMPANY_CONTACTS.phone },
    { label: "Электронная почта", value: COMPANY_CONTACTS.email },
    {
      label: "Образовательная деятельность осуществляется по следующим адресам",
      value: COMPANY_CONTACTS.address,
    },
  ] as InfoRow[],
  collegial: {
    title: "Коллегиальные органы",
    items: ["Педагогический совет", "Общее собрание работников"],
  },
  docsTitle: "Документы",
  docs: [
    {
      label:
        "1.1 О порядке организации деятельности Общего собрания (конференции) работников",
      kind: "pdf",
      href: "https://disk.yandex.ru/i/UXsSkS4-i-pRUg",
    },
    {
      label:
        "1.1 О порядке организации деятельности Общего собрания (конференции) работников",
      kind: "sign",
      href: "https://disk.yandex.ru/d/enoNZzKoBLRohQ",
    },
    {
      label: "1.2 Положение о Педагогическом совете",
      kind: "pdf",
      href: "https://disk.yandex.ru/i/PR3BlOHbd-ezzw",
    },
    {
      label: "1.2 Положение о Педагогическом совете",
      kind: "sign",
      href: "https://disk.yandex.ru/d/DaSfQlqIPsvTmg",
    },
  ] as DocLink[],
};
