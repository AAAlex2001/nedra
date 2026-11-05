"""Реакции и счётчики."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from src.articles.models.article import Article


class SetReactionRequest(BaseModel):
    """Выбор реакции."""

    model_config = ConfigDict(extra="forbid")

    value: Literal[1, -1]


class ArticleCountersResponse(BaseModel):
    """Счётчики и реакция посетителя."""

    views_count: int
    likes_count: int
    dislikes_count: int
    my_reaction: int | None

    @classmethod
    def from_model(
        cls,
        *,
        article: Article,
        reaction_value: int | None,
    ) -> "ArticleCountersResponse":
        """Подготовить счётчики."""

        return cls(
            views_count=article.views_count,
            likes_count=article.likes_count,
            dislikes_count=article.dislikes_count,
            my_reaction=reaction_value,
        )
