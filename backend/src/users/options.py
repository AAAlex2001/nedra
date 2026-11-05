"""Настройки профиля пользователя."""

from datetime import timedelta

from src.users.catalog_items import AttestationArea, Direction, ExpertiseObject

AUDIT_DIRECTION = "sms_audit"

PHONE_MIN_DIGITS = 10
PHONE_MAX_DIGITS = 15
EMAIL_CODE_LIFETIME = timedelta(minutes=5)
EMAIL_CODE_MAX_ATTEMPTS = 5
EMAIL_CODE_DIGITS = 6


DIRECTIONS: list[Direction] = [
    Direction(
        code="industrial_safety",
        title="Экспертиза промышленной безопасности",
    ),
    Direction(
        code=AUDIT_DIRECTION,
        title="Аудит СУПБ",
    ),
    Direction(
        code="cadastral",
        title="Кадастровые работы",
    ),
    Direction(
        code="forensic",
        title="Судебная экспертиза",
    ),
    Direction(
        code="research",
        title="НИР",
    ),
    Direction(
        code="laboratory",
        title="Лабораторные исследования",
    ),
    Direction(
        code="diagnostics",
        title="Техдиагностирование",
    ),
    Direction(
        code="design",
        title="Проектирование",
    ),
    Direction(
        code="ecology",
        title="Экология",
    ),
    Direction(
        code="surveys",
        title="Изыскания",
    ),
]


OBJECTS: list[ExpertiseObject] = [
    ExpertiseObject(
        code="kl",
        label="КЛ",
        title="Документация на консервацию и ликвидацию",
        description=(
            "Проект консервации или ликвидации опасного производственного объекта. Экспертиза обязательна "
            "перед выводом объекта из эксплуатации."
        ),
    ),
    ExpertiseObject(
        code="tp",
        label="ТП",
        title="Документация на техническое перевооружение",
        description=(
            "Проект замены или модернизации оборудования на действующем объекте. Без положительного "
            "заключения работы начинать нельзя."
        ),
    ),
    ExpertiseObject(
        code="kl_tp",
        label="КЛ/ТП",
        title="Документация на консервацию, ликвидацию и техническое перевооружение",
        description=(
            "Единое удостоверение на проекты консервации, ликвидации и технического перевооружения для "
            "отраслей, где Ростехнадзор не разделяет эти виды документации."
        ),
    ),
    ExpertiseObject(
        code="d",
        label="Д",
        title="Декларация промышленной безопасности",
        description=(
            "Проверка декларации для объектов I и II класса опасности. Заключение подаётся в Ростехнадзор "
            "вместе с декларацией."
        ),
    ),
    ExpertiseObject(
        code="ob",
        label="ОБ",
        title="Обоснование безопасности",
        description=(
            "Экспертиза обоснования, когда объект отступает от требований правил. Положительное "
            "заключение позволяет эксплуатировать объект по обоснованию."
        ),
    ),
]


SEPARATE_DOCUMENTATION_OBJECTS = ("kl", "tp", "d", "ob")
COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION = ("kl_tp", "d", "ob")
COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION = ("kl_tp", "ob")
HAZARD_CLASSES = (1, 2, 3, 4)
HAZARD_CLASS_CATEGORY = {1: 1, 2: 2, 3: 3, 4: 3}


AREAS: list[AttestationArea] = [
    AttestationArea(
        code="Э1",
        title="Опасные производственные объекты угольной, сланцевой и торфяной промышленности",
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION,
    ),
    AttestationArea(
        code="Э2",
        title="Опасные производственные объекты горнорудной и нерудной промышленности",
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION,
    ),
    AttestationArea(
        code="Э3.1",
        title=(
            "Опасные производственные объекты, на которых получаются, используются, хранятся, "
            "транспортируются и уничтожаются взрывчатые материалы промышленного назначения"
        ),
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION,
    ),
    AttestationArea(
        code="Э3.2",
        title=(
            "Опасные производственные объекты, на которых получаются, перерабатываются, используются, "
            "хранятся, уничтожаются и транспортируются взрывчатые вещества и материалы, порох, ракетные "
            "топлива, пиротехнические составы и боеприпасы, за исключением промышленных взрывчатых "
            "материалов"
        ),
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION,
    ),
    AttestationArea(
        code="Э4",
        title="Опасные производственные объекты нефтегазодобывающего комплекса",
        objects=SEPARATE_DOCUMENTATION_OBJECTS,
    ),
    AttestationArea(
        code="Э5",
        title="Опасные производственные объекты магистрального трубопроводного транспорта",
        objects=SEPARATE_DOCUMENTATION_OBJECTS,
    ),
    AttestationArea(
        code="Э6",
        title=(
            "Опасные производственные объекты геологоразведочных и геофизических работ при разработке "
            "месторождений"
        ),
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION,
    ),
    AttestationArea(
        code="Э7",
        title=(
            "Опасные производственные объекты химической, нефтехимической и нефтеперерабатывающей "
            "промышленности, а также других взрывопожароопасных и вредных производств"
        ),
        objects=SEPARATE_DOCUMENTATION_OBJECTS,
    ),
    AttestationArea(
        code="Э8",
        title="Опасные производственные объекты нефтепродуктообеспечения",
        objects=SEPARATE_DOCUMENTATION_OBJECTS,
    ),
    AttestationArea(
        code="Э9",
        title="Химически опасные производственные объекты систем водоподготовки",
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION,
    ),
    AttestationArea(
        code="Э10",
        title="Опасные производственные объекты пищевой и масложировой промышленности",
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION,
    ),
    AttestationArea(
        code="Э11",
        title="Опасные производственные объекты газоснабжения",
        objects=SEPARATE_DOCUMENTATION_OBJECTS,
    ),
    AttestationArea(
        code="Э12",
        title=(
            "Опасные производственные объекты тепло- и электроэнергетики и другие объекты, использующие "
            "оборудование под давлением более 0,07 МПа или при температуре нагрева воды более 115 °C"
        ),
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION,
    ),
    AttestationArea(
        code="Э13",
        title=(
            "Опасные производственные объекты металлургической промышленности и производства чёрных и "
            "цветных металлов (межотраслевые)"
        ),
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITH_DECLARATION,
    ),
    AttestationArea(
        code="Э14.1",
        title="Опасные производственные объекты, на которых используются грузовые подвесные канатные дороги",
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION,
    ),
    AttestationArea(
        code="Э14.2",
        title=(
            "Опасные производственные объекты, на которых используются пассажирские канатные дороги и "
            "фуникулёры"
        ),
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION,
    ),
    AttestationArea(
        code="Э14.3",
        title="Опасные производственные объекты, на которых используются эскалаторы в метрополитенах",
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION,
    ),
    AttestationArea(
        code="Э14.4",
        title=(
            "Опасные производственные объекты, на которых используются стационарно установленные "
            "грузоподъёмные механизмы"
        ),
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION,
    ),
    AttestationArea(
        code="Э15",
        title="Опасные производственные объекты хранения, переработки и использования растительного сырья",
        objects=COMBINED_DOCUMENTATION_OBJECTS_WITHOUT_DECLARATION,
    ),
]


CATEGORIES = (1, 2, 3)
DIRECTION_CODES = {direction.code for direction in DIRECTIONS}
AREA_BY_CODE = {area.code: area for area in AREAS}
OBJECT_BY_CODE = {expertise_object.code: expertise_object for expertise_object in OBJECTS}
