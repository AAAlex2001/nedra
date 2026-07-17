import type { ComponentType } from "react";
import {
  EvrazLogo,
  KmarudaLogo,
  KuzbassugolLogo,
  MechelLogo,
  MetallserviceLogo,
  MnkLogo,
  NornickelLogo,
  PolyusLogo,
  SdsUgolLogo,
  SibantratsitLogo,
  SuekLogo,
  VorkutaugolLogo,
} from "@/shared/ui/icons";

export const PARTNERS_DATA = {
  title: "Наши партнеры",
  subtitle:
    "За годы работы мы выполнили проекты для ведущих горнодобывающих, металлургических и промышленных предприятий России.",
  note: "Представлена часть организаций, с которыми сотрудничает ООО НПИ «Недра». Среди наших заказчиков также образовательные учреждения, объекты культуры и государственные организации.",
};

export type Logo =
  | { kind: "svg"; Logo: ComponentType<{ className?: string }>; label: string; href: string }
  | { kind: "img"; src: string; width: number; height: number; label: string; href: string }
  | { kind: "placeholder"; width: number; height: number; label: string; href?: string };

export const ROWS: Logo[][] = [
  [
    { kind: "svg", Logo: NornickelLogo, label: "Норникель", href: "https://nornickel.ru/" },
    { kind: "img", src: "/partners/gazprom.png", width: 150, height: 74, label: "Газпром", href: "https://www.gazprom.ru/" },
    { kind: "img", src: "/partners/rosneft.png", width: 150, height: 120, label: "Роснефть", href: "https://www.rosneft.ru/" },
    { kind: "img", src: "/partners/topprom.png", width: 200, height: 52, label: "ТопПром", href: "https://top-prom.ru/" },
    { kind: "img", src: "/partners/pmh.png", width: 100, height: 103, label: "ПМХ", href: "https://metholding.ru/" },
  ],
  [
    { kind: "svg", Logo: VorkutaugolLogo, label: "ВоркутаУголь", href: "https://vorkutaugol.ru/" },
    { kind: "svg", Logo: MechelLogo, label: "Мечел", href: "https://mechel.ru/" },
    { kind: "svg", Logo: KuzbassugolLogo, label: "Кузбассразрезуголь", href: "https://kru.ru/" },
    { kind: "svg", Logo: SuekLogo, label: "СУЭК", href: "https://t.me/s/sueknews" },
    { kind: "svg", Logo: SdsUgolLogo, label: "СДС Уголь", href: "https://vvk-kuzbass.ru/predpriyatiya/khk-sds-ugol/" },
  ],
  [
    { kind: "svg", Logo: EvrazLogo, label: "ЕВРАЗ", href: "https://evrazsteel.ru/" },
    { kind: "img", src: "/partners/ugok.png", width: 150, height: 87, label: "УГОК", href: "https://www.ugok.ru/ru/information/" },
    { kind: "svg", Logo: KmarudaLogo, label: "КМАруда", href: "https://kmaruda.ru/" },
    { kind: "svg", Logo: PolyusLogo, label: "Полюс", href: "https://polyus.com/ru/" },
    { kind: "svg", Logo: SibantratsitLogo, label: "Сибантрацит", href: "https://www.sibanthracite.ru/" },
  ],
  [
    { kind: "svg", Logo: MetallserviceLogo, label: "Металлсервис", href: "https://mc.ru/" },
    { kind: "img", src: "/partners/stroyservice.webp", width: 300, height: 100, label: "Стройсервис", href: "https://stroysv.com/" },
    { kind: "img", src: "/partners/kolmar.png", width: 200, height: 36, label: "Колмар", href: "https://www.kolmar.ru/" },
    { kind: "svg", Logo: MnkLogo, label: "ИНК", href: "https://irkutskoil.ru/" },
    { kind: "img", src: "/partners/bashmed.webp", width: 125, height: 125, label: "Башмедь", href: "http://bm02.ru/" },
  ],
];

export const LAST_ROW: Logo[] = [
  { kind: "img", src: "/partners/volkovskiygok.webp", width: 100, height: 91, label: "Святогор", href: "https://volkgok.ru/applicants/" },
  { kind: "img", src: "/partners/metalloinvest.png", width: 350, height: 59, label: "Металлоинвест", href: "https://www.metalloinvest.com/" },
];
