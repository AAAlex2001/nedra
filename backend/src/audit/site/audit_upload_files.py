"""Приложения к заявке на аудит."""

from dataclasses import dataclass, field

from fastapi import UploadFile

from src.audit.exceptions import InvalidAuditApplicationError
from src.audit.options import AUDIT_DOCUMENTS
from src.audit.schemas.audit_details import AuditDetailsSchema


@dataclass
class AuditUploadFiles:
    """Загруженные файлы заявки."""

    documents: list[UploadFile] = field(default_factory=list)  # Файлы по перечню.
    item_numbers: list[int] = field(default_factory=list)  # Номера пунктов перечня.
    company_card: UploadFile | None = None  # Карточка организации.
    opo_certificate: UploadFile | None = None  # Свидетельство регистрации ОПО.
    power_of_attorney: UploadFile | None = None  # Доверенность представителя.
    sto_file: UploadFile | None = None  # Стандарт организации.

    def prepare_attachments(self, *, details: AuditDetailsSchema) -> list["AuditAttachedFile"]:
        """Проверить и собрать приложения."""

        if len(self.documents) != len(self.item_numbers):
            raise InvalidAuditApplicationError("Для каждого файла нужен номер пункта перечня")

        for number in self.item_numbers:
            if number < 1 or number > len(AUDIT_DOCUMENTS):
                raise InvalidAuditApplicationError(f"В перечне нет пункта {number}")

        if details.applicant.by_proxy and self.power_of_attorney is None:
            raise InvalidAuditApplicationError("Приложите доверенность заявителя")

        if details.params.use_sto and self.sto_file is None:
            raise InvalidAuditApplicationError("Приложите файл СТО")

        attachments = []

        for file, number in zip(
            self.documents,
            self.item_numbers,
            strict=True,
        ):
            attachments.append(
                AuditAttachedFile(
                    file=file,
                    kind="audit_item",
                    item_number=number,
                )
            )

        if self.company_card is not None:
            attachments.append(
                AuditAttachedFile(
                    file=self.company_card,
                    kind="company_card",
                )
            )

        if self.opo_certificate is not None and details.scope == "all":
            attachments.append(
                AuditAttachedFile(
                    file=self.opo_certificate,
                    kind="opo_certificate",
                )
            )

        if self.power_of_attorney is not None and details.applicant.by_proxy:
            attachments.append(
                AuditAttachedFile(
                    file=self.power_of_attorney,
                    kind="power_of_attorney",
                )
            )

        if self.sto_file is not None and details.params.use_sto:
            attachments.append(
                AuditAttachedFile(
                    file=self.sto_file,
                    kind="sto",
                )
            )

        return attachments


@dataclass(frozen=True)
class AuditAttachedFile:
    """Файл с назначением в заявке."""

    file: UploadFile  # Загруженный файл.
    kind: str  # Назначение документа.
    item_number: int | None = None  # Номер пункта перечня.
