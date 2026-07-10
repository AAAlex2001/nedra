import type { ComponentType } from "react";
import {
  EvrazLogo,
  KuzbassugolLogo,
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
  | { kind: "svg"; Logo: ComponentType<{ className?: string }>; label: string }
  | { kind: "img"; src: string; width: number; height: number; label: string }
  | { kind: "placeholder"; width: number; height: number; label: string };

export const ROWS: Logo[][] = [
  [
    { kind: "svg", Logo: NornickelLogo, label: "Норникель" },
    { kind: "img", src: "/partners/gazprom.png", width: 150, height: 74, label: "Газпром" },
    { kind: "img", src: "/partners/rosneft.png", width: 150, height: 120, label: "Роснефть" },
    { kind: "img", src: "/partners/topprom.png", width: 200, height: 52, label: "ТопПром" },
    { kind: "img", src: "/partners/pmh.png", width: 100, height: 103, label: "ПМХ" },
  ],
  [
    { kind: "svg", Logo: VorkutaugolLogo, label: "ВоркутаУголь" },
    { kind: "img", src: "/partners/mechel.png", width: 150, height: 39, label: "Мечел" },
    { kind: "svg", Logo: KuzbassugolLogo, label: "Кузбассразрезуголь" },
    { kind: "svg", Logo: SuekLogo, label: "СУЭК" },
    { kind: "svg", Logo: SdsUgolLogo, label: "СДС Уголь" },
  ],
  [
    { kind: "svg", Logo: EvrazLogo, label: "ЕВРАЗ" },
    { kind: "img", src: "/partners/ugok.png", width: 150, height: 87, label: "УГОК" },
    { kind: "img", src: "/partners/kmaruda.png", width: 200, height: 69, label: "КМАруда" },
    { kind: "svg", Logo: PolyusLogo, label: "Полюс" },
    { kind: "svg", Logo: SibantratsitLogo, label: "Сибантрацит" },
  ],
  [
    { kind: "svg", Logo: MetallserviceLogo, label: "Металлсервис" },
    { kind: "img", src: "/partners/stroyservice.png", width: 300, height: 100, label: "Стройсервис" },
    { kind: "img", src: "/partners/kolmar.png", width: 200, height: 36, label: "Колмар" },
    { kind: "svg", Logo: MnkLogo, label: "МНК" },
    { kind: "img", src: "/partners/bashmed.jpg", width: 125, height: 125, label: "Башмедь" },
  ],
];

export const LAST_ROW: Logo[] = [
  { kind: "img", src: "/partners/volkovskiygok.jpg", width: 100, height: 91, label: "Святогор" },
  { kind: "img", src: "/partners/metalloinvest.png", width: 350, height: 59, label: "Металлоинвест" },
];
