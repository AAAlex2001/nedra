import type { FormErrors, OrderState } from "./types";

export const orderErrors = (state: OrderState, price: number): FormErrors => {
  const errors: FormErrors = {};

  if (state.objectName.trim() === "") errors.objectName = "Укажите наименование объекта";
  if (price <= 0) errors.price = "Укажите стоимость экспертизы";
  if (state.files.length === 0) errors.files = "Приложите документы для экспертизы";

  return errors;
};
