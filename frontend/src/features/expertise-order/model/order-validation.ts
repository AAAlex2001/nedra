import type { FormErrors, OrderState } from "./types";

export const objectErrors = (state: OrderState): FormErrors => {
  const errors: FormErrors = {};

  if (state.objectName.trim() === "") errors.objectName = "Укажите наименование объекта";

  return errors;
};

export const priceErrors = (price: number): FormErrors => {
  const errors: FormErrors = {};

  if (price <= 0) errors.price = "Укажите стоимость экспертизы";

  return errors;
};

export const filesErrors = (state: OrderState): FormErrors => {
  const errors: FormErrors = {};

  if (state.files.length === 0) errors.files = "Приложите документы для экспертизы";

  return errors;
};
