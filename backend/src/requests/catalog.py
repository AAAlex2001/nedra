"""Справочники видов деятельности и направлений для заявок."""

ACTIVITY_TITLES: dict[str, str] = {
    "expertise": "Экспертиза промышленной безопасности",
    "audit": "Аудит СУПБ",
    "consulting": "Консалтинг",
}

DIRECTION_TITLES: dict[str, str] = {
    "epb": "Экспертиза промышленной безопасности",
    "supb": "Аудит систем управления промышленной безопасностью",
    "consulting": "Консалтинговые услуги",
}

ACTIVITY_DIRECTION: dict[str, str] = {
    "expertise": "epb",
    "audit": "supb",
    "consulting": "consulting",
}
