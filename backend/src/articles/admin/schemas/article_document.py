"""Приложение к публикации."""

from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict, Field
from src.articles.options import DOCUMENT_KINDS, DOCUMENT_URL_PATTERN


class ArticleDocumentRequest(BaseModel):
    """Приложение к публикации."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=1,
        max_length=255,
    )
    url: str = Field(pattern=DOCUMENT_URL_PATTERN)

    def to_record(self) -> dict[str, str]:
        """Подготовить приложение для хранения."""

        extension = PurePosixPath(self.url).suffix

        return {"title": self.title, "url": self.url, "kind": DOCUMENT_KINDS[extension]}
