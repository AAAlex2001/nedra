export const ACTIVITIES_DATA = {
  titleBefore: "Аттестованная",
  titleAccent: "методика исследований",
  subtitle:
    "Исследование выполняется по аттестованным методикам и используются при подготовке проектной и разрешительной документации для предприятий угольной промышленности опасных производственных объектов",
};

export type FeatureIcon = "certified" | "certificate" | "results";

export type FeatureItem = {
  icon: FeatureIcon;
  title: string;
  description: string;
};

export const FEATURE_ITEMS: FeatureItem[] = [
  {
    icon: "certified",
    title: "Аттестованная методика",
    description:
      "Методика прошла аттестацию установленном порядке и соответствуют требованиям законодательства РФ",
  },
  {
    icon: "certificate",
    title: "Официальное свидетельство",
    description:
      "Выдано Федеральной службой по аккредитации. Действительно и актуально",
  },
  {
    icon: "results",
    title: "Результаты с официальным статусом",
    description:
      "Результаты исследования принимаются при разработке проектной и разрешительной документации",
  },
];

export type MethodologyCardData = {
  image: string;
  title: string;
  number: string;
  points: string[];
  button: { text: string; href: string };
};

export const METHODOLOGY_CARD: MethodologyCardData = {
  image: "/what_is_this/what_is_this_6.png",
  title: "Методика измерения химической активности угля",
  number: "№ 149/RA.RU.310473/2026",
  points: [
    "Официальное свидетельство Федеральной службы по аккредитации",
    "Используется при подготовке проектной и разрешительной документации",
  ],
  button: {
    text: "Открыть документ",
    href: "#",
  },
};
