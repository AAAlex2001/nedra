from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from app.dependencies import get_article_service, require_admin
from app.schemas.articles import (
    ArticleAdminCardSchema,
    ArticleAdminSchema,
    ArticleCreateSchema,
    ArticleUpdateSchema,
    Section,
    TagAdminSchema,
    TagCreateSchema,
    UploadResultSchema,
)
from app.services.articles import ArticleService
from app.services.exceptions import ArticleNotFoundError, TagNotFoundError
from app.services.uploads import UploadError, save_article_image


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/articles")
async def list_articles(
    section: Section | None = Query(None, description="Раздел: blog или news"),
    service: ArticleService = Depends(get_article_service),
) -> list[ArticleAdminCardSchema]:
    """Все статьи, включая черновики."""

    articles = await service.list_all(section)

    return [ArticleAdminCardSchema.model_validate(article) for article in articles]


@router.post("/articles", status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreateSchema,
    service: ArticleService = Depends(get_article_service),
) -> ArticleAdminSchema:
    """Создание статьи."""

    try:
        article = await service.create(payload)
    except TagNotFoundError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return ArticleAdminSchema.model_validate(article)


@router.get("/articles/{article_id}")
async def get_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
) -> ArticleAdminSchema:
    """Статья для редактирования."""

    try:
        article = await service.get_by_id(article_id)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    return ArticleAdminSchema.model_validate(article)


@router.patch("/articles/{article_id}")
async def update_article(
    article_id: int,
    payload: ArticleUpdateSchema,
    service: ArticleService = Depends(get_article_service),
) -> ArticleAdminSchema:
    """Частичное обновление статьи."""

    try:
        article = await service.get_by_id(article_id)
        article = await service.update(article, payload)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except TagNotFoundError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return ArticleAdminSchema.model_validate(article)


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
) -> None:
    """Удаление статьи."""

    try:
        article = await service.get_by_id(article_id)
    except ArticleNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error

    await service.delete(article)


@router.post("/uploads", status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile) -> UploadResultSchema:
    """Загрузка обложки или картинки для текста."""

    try:
        url = await save_article_image(file)
    except UploadError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return UploadResultSchema(url=url)


@router.get("/tags")
async def list_tags(
    service: ArticleService = Depends(get_article_service),
) -> list[TagAdminSchema]:
    """Теги с идентификаторами."""

    tags = await service.list_tags()

    return [TagAdminSchema.model_validate(tag) for tag in tags]


@router.post("/tags", status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: TagCreateSchema,
    service: ArticleService = Depends(get_article_service),
) -> TagAdminSchema:
    """Создание тега."""

    tag = await service.create_tag(payload.title)

    return TagAdminSchema.model_validate(tag)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    service: ArticleService = Depends(get_article_service),
) -> None:
    """Удаление тега. Связи со статьями снимаются каскадом."""

    try:
        await service.delete_tag(tag_id)
    except TagNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
