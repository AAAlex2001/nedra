"""Загрузка файлов публикации."""

from fastapi import UploadFile
from pydantic import BaseModel


class UploadFileRequest(BaseModel):
    """Файл изображения или документа."""

    file: UploadFile


class UploadedFileResponse(BaseModel):
    """Публичный адрес файла."""

    url: str
