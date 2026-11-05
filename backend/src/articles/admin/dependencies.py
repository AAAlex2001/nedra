"""Зависимости редактора публикаций."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.articles.admin.usecases.create_article import CreateArticleUseCase
from src.articles.admin.usecases.create_tag import CreateTagUseCase
from src.articles.admin.usecases.delete_article import DeleteArticleUseCase
from src.articles.admin.usecases.delete_tag import DeleteTagUseCase
from src.articles.admin.usecases.get_article import GetAdminArticleUseCase
from src.articles.admin.usecases.list_articles import ListAdminArticlesUseCase
from src.articles.admin.usecases.list_tags import ListAdminTagsUseCase
from src.articles.admin.usecases.update_article import UpdateArticleUseCase
from src.articles.admin.usecases.upload_document import UploadArticleDocumentUseCase
from src.articles.admin.usecases.upload_image import UploadArticleImageUseCase
from src.articles.repositories.article_contents import ArticleContentRepository
from src.articles.repositories.articles import ArticleRepository
from src.articles.repositories.tags import TagRepository
from src.core.database import get_session
from src.core.file_storage import FileStorage
from src.core.settings import Settings, get_settings


def get_list_articles_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> ListAdminArticlesUseCase:
    """Список публикаций."""

    return ListAdminArticlesUseCase(
        articles=ArticleRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_article_usecase(*, session: AsyncSession = Depends(get_session)) -> GetAdminArticleUseCase:
    """Просмотр публикации."""

    return GetAdminArticleUseCase(
        articles=ArticleRepository(session=session),
        contents=ArticleContentRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_create_article_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> CreateArticleUseCase:
    """Создание публикации."""

    return CreateArticleUseCase(
        session=session,
        articles=ArticleRepository(session=session),
        contents=ArticleContentRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_update_article_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> UpdateArticleUseCase:
    """Редактирование публикации."""

    return UpdateArticleUseCase(
        session=session,
        articles=ArticleRepository(session=session),
        contents=ArticleContentRepository(session=session),
        tags=TagRepository(session=session),
    )


def get_delete_article_usecase(
    *, session: AsyncSession = Depends(get_session)
) -> DeleteArticleUseCase:
    """Удаление публикации."""

    return DeleteArticleUseCase(
        session=session,
        articles=ArticleRepository(session=session),
    )


def get_list_tags_usecase(*, session: AsyncSession = Depends(get_session)) -> ListAdminTagsUseCase:
    """Все теги."""

    return ListAdminTagsUseCase(
        tags=TagRepository(session=session),
    )


def get_create_tag_usecase(*, session: AsyncSession = Depends(get_session)) -> CreateTagUseCase:
    """Создание тега."""

    return CreateTagUseCase(
        session=session,
        tags=TagRepository(session=session),
    )


def get_delete_tag_usecase(*, session: AsyncSession = Depends(get_session)) -> DeleteTagUseCase:
    """Удаление тега."""

    return DeleteTagUseCase(
        session=session,
        tags=TagRepository(session=session),
    )


def get_upload_image_usecase(
    *, settings: Settings = Depends(get_settings)
) -> UploadArticleImageUseCase:
    """Загрузка изображения."""

    return UploadArticleImageUseCase(
        storage=FileStorage(directory=settings.media_dir),
    )


def get_upload_document_usecase(
    *, settings: Settings = Depends(get_settings)
) -> UploadArticleDocumentUseCase:
    """Загрузка документа."""

    return UploadArticleDocumentUseCase(
        storage=FileStorage(directory=settings.media_dir),
    )
