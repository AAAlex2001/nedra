import { MIN_AUDIT_PRICE, type AuditObject } from "@/entities/expertise";
import { needsSto, type AuditForm } from "./audit-form";
import type { FormErrors } from "./types";

const isEmpty = (value: string): boolean => value.trim() === "";

const addApplicantErrors = (form: AuditForm, errors: FormErrors) => {
  const { applicant } = form;

  if (isEmpty(applicant.full_name)) errors.full_name = "Укажите ФИО представителя";
  if (isEmpty(applicant.position)) errors.position = "Укажите должность";
  if (isEmpty(applicant.organization)) errors.organization = "Укажите наименование организации";
  if (isEmpty(applicant.inn)) errors.inn = "Укажите ИНН организации";
  if (isEmpty(applicant.phone)) errors.phone = "Укажите контактный телефон";
  if (isEmpty(applicant.email)) errors.email = "Укажите корпоративный e-mail";
  if (applicant.by_proxy && !form.proxyFile) errors.proxyFile = "Приложите доверенность";
};

const addObjectErrors = (item: AuditObject, index: number, errors: FormErrors) => {
  const key = `object-${index}`;

  if (isEmpty(item.reg_number)) errors[`${key}-reg_number`] = "Укажите регистрационный номер ОПО";
  if (isEmpty(item.name)) errors[`${key}-name`] = "Укажите наименование ОПО";
  if (!item.hazard_class) errors[`${key}-hazard_class`] = "Выберите класс опасности ОПО";
  if (isEmpty(item.address)) errors[`${key}-address`] = "Укажите адрес ОПО";
  if (isEmpty(item.industry)) errors[`${key}-industry`] = "Укажите вид деятельности на ОПО";
  if (item.hazard_signs.length === 0) errors[`${key}-hazard_signs`] = "Отметьте признаки опасности ОПО";
};

const addScopeErrors = (form: AuditForm, errors: FormErrors) => {
  if (!form.scope) {
    errors.scope = "Выберите масштаб аудита";
    return;
  }

  if (form.scope !== "all") {
    form.objects.forEach((item, index) => addObjectErrors(item, index, errors));
    return;
  }

  if (Number(form.fleetCount) < 1) errors.fleetCount = "Укажите количество ОПО";
  if (isEmpty(form.fleetProfile)) errors.fleetProfile = "Укажите основной отраслевой профиль";
  if (form.multiRegion === null) errors.multiRegion = "Укажите, есть ли ОПО в разных субъектах РФ";
};

const addParamsErrors = (form: AuditForm, errors: FormErrors) => {
  const withSto = needsSto(form.kind);
  const stoChosen = withSto && form.useSto === true;

  if (!form.kind) errors.kind = "Выберите тип аудита";
  if (withSto && form.useSto === null) errors.useSto = "Укажите, учитывать ли СТО";
  if (stoChosen && isEmpty(form.stoName)) errors.stoName = "Укажите наименование и реквизиты СТО";
  if (stoChosen && !form.stoFile) errors.stoFile = "Приложите файл СТО";
  if (form.kind === "selective" && form.elements.length === 0) {
    errors.elements = "Выберите направления для аудита";
  }
};

const addTimingErrors = (form: AuditForm, errors: FormErrors) => {
  if (!form.timing) errors.timing = "Выберите сроки аудита";
  if (form.timing !== "custom") return;

  if (!form.start) errors.start = "Укажите начало периода";
  if (!form.end) errors.end = "Укажите окончание периода";
  if (form.start && form.end && form.start > form.end) errors.end = "Окончание раньше начала";
};

const addBudgetErrors = (form: AuditForm, price: number, errors: FormErrors) => {
  if (form.budget === "custom" && price < MIN_AUDIT_PRICE) {
    errors.price = "Стоимость аудита — не менее 100 000 ₽";
  }

  if (!form.negotiation) errors.negotiation = "Укажите, возможен ли торг";
};

export const auditErrors = (form: AuditForm, price: number): FormErrors => {
  const errors: FormErrors = {};

  addApplicantErrors(form, errors);
  addScopeErrors(form, errors);
  if (form.stages.length === 0) errors.stages = "Выберите этапы аудита";
  addParamsErrors(form, errors);
  addTimingErrors(form, errors);
  addBudgetErrors(form, price, errors);

  return errors;
};
