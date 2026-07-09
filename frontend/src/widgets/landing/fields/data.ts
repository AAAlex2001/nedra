export const FIELDS_DATA = {
  title: "Все услуги института",
  subtitle:
    "Комплексные решения в области проектирования, экспертизы, исследований, сопровождения и обучения",
};

export type FieldSection = {
  title: string;
  text?: string;
  bullets?: string[];
};

export type FieldLicense = {
  title: string;
  meta: string;
  href: string;
};

export type FieldLicenseColumn = {
  text: string;
  file: FieldLicense;
};

export type FieldItem = {
  id: string;
  title: string;
  serviceCount: number;
  image: string;
  summary: string;
  sections: FieldSection[];
  licensesTitle?: string;
  licenseColumns?: FieldLicenseColumn[];
};

export const CONTACT = {
  phone: "+7 905 995-94-11",
  email: "nedra-npi@mail.ru",
  person: "Самохин Сергей Владимирович",
};

export const formatServiceCount = (count: number): string => {
  const mod10 = count % 10;
  const mod100 = count % 100;

  if (mod10 === 1 && mod100 !== 11) {
    return `${count} услуга`;
  }

  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
    return `${count} услуги`;
  }

  return `${count} услуг`;
};

export const FIELDS_ITEMS: FieldItem[] = [
  {
    id: "01",
    title: "Проектирование и инженерные изыскания",
    serviceCount: 1,
    image: "/what_is_this/what_is_this_2.png",
    summary:
      "Разработка проектной документации и проведение инженерных изысканий для объектов различного назначения и уровня сложности",
    sections: [
      {
        title: "Описание услуги",
        bullets: [
          "Инженерные изыскания для подготовки проектной документации, строительства, реконструкции объектов капитального строительства. Обследование зданий и сооружений;",
          "Разработка проектно-сметной документации объектов гражданского и промышленного назначения, в том числе опасных производственных объектов.",
        ],
      },
      {
        title: "Результат",
        text: "Комплект проектной документации, соответствующие требованиям нормативных документов и готовый к прохождению экспертизы.",
      },
      {
        title: "Нормативная база",
        text: "Работы выполняется в соответствии с Градостроительным кодексом РФ, СП, СНиП, ГОСТ и другими действующими нормативными документами.",
      },
    ],
    licensesTitle: "Разрешительные документы",
    licenseColumns: [
      {
        text: 'Является членом саморегулируемой организации Саморегулируемая организация Ассоциация "Национальное объединение организаций по инженерным изысканиям, геологии и геотехнике". Регистрационный номер члена саморегулируемой организации И-012-004205325060-0752',
        file: {
          title: "Свидетельство РСО",
          meta: "PDF, 1.2 МБ",
          href: "#",
        },
      },
      {
        text: 'Является членом саморегулируемой организации Ассоциация «Саморегулируемая организация Объединение Проектировщиков "ОсноваПроект"». Регистрационный номер члена саморегулируемой организации П-176-004205325060-1111',
        file: {
          title: "Лицензия и аттестаты",
          meta: "PDF, 2.4 МБ",
          href: "#",
        },
      },
    ],
  },
  {
    id: "02",
    title: "Научно-техническое сопровождение",
    serviceCount: 3,
    image: "/what_is_this/what_is_this_2.png",
    summary:
      "Комплексное научно-техническое сопровождение проектных и производственных решений на всех этапах реализации.",
    sections: [],
  },
  {
    id: "03",
    title: "Промышленная безопасность",
    serviceCount: 7,
    image: "/what_is_this/what_is_this_1.png",
    summary:
      "Комплекс услуг в области обеспечения промышленной безопасности опасных производственных объектов.",
    sections: [],
  },
  {
    id: "04",
    title: "Объекты культурного наследия",
    serviceCount: 1,
    image: "/what_is_this/what_is_this_5.png",
    summary:
      "Проектные и изыскательские работы по сохранению объектов культурного наследия.",
    sections: [],
  },
  {
    id: "05",
    title: "Экологическое проектирование",
    serviceCount: 1,
    image: "/what_is_this/what_is_this_3.png",
    summary:
      "Разработка проектной документации в области охраны окружающей среды.",
    sections: [],
  },
  {
    id: "06",
    title: "Сертификация",
    serviceCount: 1,
    image: "/what_is_this/what_is_this_3.png",
    summary: "Сертификация продукции и услуг в установленном порядке.",
    sections: [],
  },
  {
    id: "07",
    title: "Научно-испытательная лаборатория",
    serviceCount: 1,
    image: "/what_is_this/what_is_this_6.png",
    summary:
      "Исследования и испытания в области эндогенной пожаробезопасности, физико-механических свойств горных пород и технологических характеристик твёрдого минерального топлива.",
    sections: [],
  },
  {
    id: "08",
    title: "Образовательная деятельность",
    serviceCount: 1,
    image: "/what_is_this/what_is_this_4.png",
    summary:
      "Повышение квалификации проектных специалистов в соответствии с требованиями законодательства РФ.",
    sections: [],
  },
  {
    id: "09",
    title: "Атомная лицензия",
    serviceCount: 1,
    image: "/what_is_this/what_is_this_1.png",
    summary:
      "Лицензирование деятельности в области использования атомной энергии.",
    sections: [],
  },
];
