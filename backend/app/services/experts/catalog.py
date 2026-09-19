"""Справочник аттестации экспертов промышленной безопасности.

Источник — таблица буквенно-цифровых обозначений областей аттестации
Ростехнадзора. Для каждой области перечислены объекты экспертизы,
по которым она выдаётся: у части областей документация делится
на КЛ и ТП, у части объединена в КЛ/ТП, а декларации (Д) есть не везде.
Фронтенд получает этот справочник через GET /experts/catalog.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Direction:
    """Направление работы эксперта."""

    code: str
    title: str


@dataclass(frozen=True)
class ExpertiseObject:
    """Объект экспертизы: короткий код с удостоверения и расшифровка."""

    code: str
    label: str
    title: str


@dataclass(frozen=True)
class AttestationArea:
    """Область аттестации и объекты экспертизы, по которым она выдаётся."""

    code: str
    title: str
    objects: tuple[str, ...]


DIRECTIONS: list[Direction] = [
    Direction("industrial_safety", "Экспертиза промышленной безопасности"),
    Direction("sms_audit", "Аудит СУПБ"),
    Direction("cadastral", "Кадастровые работы"),
    Direction("forensic", "Судебная экспертиза"),
    Direction("research", "НИР"),
    Direction("laboratory", "Лабораторные исследования"),
    Direction("diagnostics", "Техдиагностирование"),
    Direction("design", "Проектирование"),
    Direction("ecology", "Экология"),
    Direction("surveys", "Изыскания"),
]

OBJECTS: list[ExpertiseObject] = [
    ExpertiseObject("kl", "КЛ", "Документация на консервацию и ликвидацию"),
    ExpertiseObject("tp", "ТП", "Документация на техническое перевооружение"),
    ExpertiseObject("zs", "ЗС", "Здания и сооружения"),
    ExpertiseObject("tu", "ТУ", "Технические устройства"),
    ExpertiseObject("d", "Д", "Декларация промышленной безопасности"),
    ExpertiseObject("ob", "ОБ", "Обоснование безопасности"),
]

WITH_DECLARATION = ("kl", "tp", "tu", "zs", "d", "ob")
NO_DECLARATION = ("kl", "tp", "tu", "zs", "ob")

AREAS: list[AttestationArea] = [
    AttestationArea(
        "Э1",
        "Опасные производственные объекты угольной, сланцевой и торфяной промышленности",
        JOINED_DOCS_NO_DECLARATION,
    ),
    AttestationArea(
        "Э2",
        "Опасные производственные объекты горнорудной и нерудной промышленности",
        JOINED_DOCS_WITH_DECLARATION,
    ),
    AttestationArea(
        "Э3.1",
        "Опасные производственные объекты, на которых получаются, используются, хранятся, "
        "транспортируются и уничтожаются взрывчатые материалы промышленного назначения",
        JOINED_DOCS_WITH_DECLARATION,
    ),
    AttestationArea(
        "Э3.2",
        "Опасные производственные объекты, на которых получаются, перерабатываются, "
        "используются, хранятся, уничтожаются и транспортируются взрывчатые вещества "
        "и материалы, порох, ракетные топлива, пиротехнические составы и боеприпасы, "
        "за исключением промышленных взрывчатых материалов",
        JOINED_DOCS_WITH_DECLARATION,
    ),
    AttestationArea(
        "Э4",
        "Опасные производственные объекты нефтегазодобывающего комплекса",
        SPLIT_DOCS,
    ),
    AttestationArea(
        "Э5",
        "Опасные производственные объекты магистрального трубопроводного транспорта",
        SPLIT_DOCS,
    ),
    AttestationArea(
        "Э6",
        "Опасные производственные объекты геологоразведочных и геофизических работ "
        "при разработке месторождений",
        JOINED_DOCS_WITH_DECLARATION,
    ),
    AttestationArea(
        "Э7",
        "Опасные производственные объекты химической, нефтехимической и "
        "нефтеперерабатывающей промышленности, а также других взрывопожароопасных "
        "и вредных производств",
        SPLIT_DOCS,
    ),
    AttestationArea(
        "Э8",
        "Опасные производственные объекты нефтепродуктообеспечения",
        SPLIT_DOCS,
    ),
    AttestationArea(
        "Э9",
        "Химически опасные производственные объекты систем водоподготовки",
        JOINED_DOCS_WITH_DECLARATION,
    ),
    AttestationArea(
        "Э10",
        "Опасные производственные объекты пищевой и масложировой промышленности",
        JOINED_DOCS_WITH_DECLARATION,
    ),
    AttestationArea(
        "Э11",
        "Опасные производственные объекты газоснабжения",
        SPLIT_DOCS,
    ),
    AttestationArea(
        "Э12",
        "Опасные производственные объекты тепло- и электроэнергетики и другие объекты, "
        "использующие оборудование под давлением более 0,07 МПа или при температуре "
        "нагрева воды более 115 °C",
        JOINED_DOCS_NO_DECLARATION,
    ),
    AttestationArea(
        "Э13",
        "Опасные производственные объекты металлургической промышленности и производства "
        "чёрных и цветных металлов (межотраслевые)",
        JOINED_DOCS_WITH_DECLARATION,
    ),
    AttestationArea(
        "Э14.1",
        "Опасные производственные объекты, на которых используются грузовые подвесные "
        "канатные дороги",
        JOINED_DOCS_NO_DECLARATION,
    ),
    AttestationArea(
        "Э14.2",
        "Опасные производственные объекты, на которых используются пассажирские канатные "
        "дороги и фуникулёры",
        JOINED_DOCS_NO_DECLARATION,
    ),
    AttestationArea(
        "Э14.3",
        "Опасные производственные объекты, на которых используются эскалаторы "
        "в метрополитенах",
        JOINED_DOCS_NO_DECLARATION,
    ),
    AttestationArea(
        "Э14.4",
        "Опасные производственные объекты, на которых используются стационарно "
        "установленные грузоподъёмные механизмы",
        JOINED_DOCS_NO_DECLARATION,
    ),
    AttestationArea(
        "Э15",
        "Опасные производственные объекты хранения, переработки и использования "
        "растительного сырья",
        JOINED_DOCS_NO_DECLARATION,
    ),
]

CATEGORIES = (1, 2, 3)

DIRECTION_CODES = {direction.code for direction in DIRECTIONS}
AREA_BY_CODE = {area.code: area for area in AREAS}
OBJECT_BY_CODE = {item.code: item for item in OBJECTS}
