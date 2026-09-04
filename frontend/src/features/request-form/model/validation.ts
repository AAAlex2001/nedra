import type { FieldErrors, RequestFields } from "./types";

const INN_PATTERN = /^(\d{10}|\d{12})$/;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export const validate = (
  fields: RequestFields,
  hasService: boolean,
): FieldErrors => {
  const errors: FieldErrors = {};

  if (!hasService) errors.service = "Выберите услугу";
  if (!fields.name.trim()) errors.name = "Укажите имя";
  if (!fields.telephone.trim()) errors.telephone = "Укажите телефон";

  if (!fields.email.trim()) {
    errors.email = "Укажите email";
  } else if (!EMAIL_PATTERN.test(fields.email.trim())) {
    errors.email = "Проверьте формат email";
  }

  if (fields.inn && !INN_PATTERN.test(fields.inn)) {
    errors.inn = "ИНН содержит 10 или 12 цифр";
  }

  if (!fields.comment.trim()) errors.comment = "Опишите задачу";

  return errors;
};

export const isValid = (errors: FieldErrors): boolean =>
  Object.keys(errors).length === 0;
