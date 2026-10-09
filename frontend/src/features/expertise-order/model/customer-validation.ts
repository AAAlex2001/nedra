import type { FormErrors, OrderState } from "./types";

const COMPANY_MESSAGE = "Заполните реквизиты заказчика";
const INDIVIDUAL_MESSAGE = "Заполните данные заказчика";

export const customerErrors = (state: OrderState): FormErrors => {
  const errors: FormErrors = {};

  if (state.customerType === "individual") {
    for (const [field, value] of Object.entries(state.individual)) {
      if (value.trim() === "") errors[`individual-${field}`] = INDIVIDUAL_MESSAGE;
    }

    return errors;
  }

  for (const [field, value] of Object.entries(state.company)) {
    if (field === "kpp") continue;
    if (value.trim() === "") errors[`company-${field}`] = COMPANY_MESSAGE;
  }

  return errors;
};
