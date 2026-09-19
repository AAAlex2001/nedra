from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status

from app.dependencies.admin import require_admin
from app.dependencies.articles import (
    get_article_by_id,
    get_article_repository,
    get_create_article_usecase,
    get_create_tag_usecase,
    get_tag_repository,
    get_update_article_usecase,
)
from app.models.article import Article
from app.schemas.article import (
    ArticleAdminCardSchema,
    ArticleAdminSchema,
    ArticleCreateSchema,
    ArticleUpdateSchema,
    Section,
    TagAdminSchema,
    TagCreateSchema,
    UploadResultSchema,
)
from app.services.articles.exceptions import TagNotFoundError
from app.services.articles.images import UploadError, save_article_image
from app.services.articles.repo import ArticleRepository
from app.services.articles.tags import TagRepository
from app.services.articles.usecases.create_article import CreateArticleUseCase
from app.services.articles.usecases.create_tag import CreateTagUseCase
from app.services.articles.usecases.update_article import UpdateArticleUseCase


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/articles")
async def list_articles(
    section: Section | None = Query(None, description="Раздел: blog или news"),
    articles: ArticleRepository = Depends(get_article_repository),
) -> list[ArticleAdminCardSchema]:
    """Все статьи, включая черновики."""

    items = await articles.list_all(section)

    return [ArticleAdminCardSchema.model_validate(item) for item in items]


@router.post("/articles", status_code=status.HTTP_201_CREATED)
async def create_article(
    payload: ArticleCreateSchema,
    usecase: CreateArticleUseCase = Depends(get_create_article_usecase),
) -> ArticleAdminSchema:
    """Создание статьи."""

    try:
        article = await usecase.execute(payload)
    except TagNotFoundError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return ArticleAdminSchema.model_validate(article)


@router.get("/articles/{article_id}")
async def get_article(
    article: Article = Depends(get_article_by_id),
) -> ArticleAdminSchema:
    """Статья для редактирования."""

    return ArticleAdminSchema.model_validate(article)


@router.patch("/articles/{article_id}")
async def update_article(
    payload: ArticleUpdateSchema,
    article: Article = Depends(get_article_by_id),
    usecase: UpdateArticleUseCase = Depends(get_update_article_usecase),
) -> ArticleAdminSchema:
    """Частичное обновление статьи."""

    try:
        updated = await usecase.execute(article, payload)
    except TagNotFoundError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error

    return ArticleAdminSchema.model_validate(updated)


@router.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article: Article = Depends(get_article_by_id),
    articles: ArticleRepository = Depends(get_article_repository),
) -> None:
    """Удаление статьи."""

    await articles.delete(article)


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
    tags: TagRepository = Depends(get_tag_repository),
) -> list[TagAdminSchema]:
    """Все теги с идентификаторами."""

    items = await tags.list_all(None)

    return [TagAdminSchema.model_validate(item) for item in items]


@router.post("/tags", status_code=status.HTTP_201_CREATED)
async def create_tag(
    payload: TagCreateSchema,
    usecase: CreateTagUseCase = Depends(get_create_tag_usecase),
) -> TagAdminSchema:
    """Создание тега."""

    tag = await usecase.execute(payload.title)

    return TagAdminSchema.model_validate(tag)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    tags: TagRepository = Depends(get_tag_repository),
) -> None:
    """Удаление тега. Связи со статьями снимаются каскадом."""

    tag = await tags.get_by_id(tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Тег с ID {tag_id} не найден",
        )

    await tags.delete(tag)
