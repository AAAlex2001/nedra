"""Хеширование паролей через bcrypt.

В базе хранится не пароль, а его хеш с солью. По хешу пароль не восстановить,
а одинаковые пароли дают разные хеши благодаря соли. Функции синхронные и
медленные по замыслу (это защита от перебора), поэтому вызывать их нужно
через asyncio.to_thread, чтобы не блокировать event loop.
"""

import bcrypt


def hash_password(password: str) -> str:
    """Захешировать пароль. Возвращает строку, которую можно хранить в БД."""

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Проверить, что пароль соответствует хешу из БД."""

    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hash_bytes)
