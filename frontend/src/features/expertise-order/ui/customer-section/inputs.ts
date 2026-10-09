import type { CustomerType } from "@/entities/expertise";
import type { CompanyField, IndividualField } from "../../model/types";

type CompanyInput = {
  field: CompanyField;
  label: string;
  placeholder: string;
  numeric?: boolean;
  optional?: boolean;
  wide?: boolean;
};

type IndividualInput = {
  field: IndividualField;
  label: string;
  placeholder: string;
  type?: "text" | "date";
  numeric?: boolean;
  wide?: boolean;
};

export const CUSTOMER_TYPES: { value: CustomerType; label: string }[] = [
  { value: "legal", label: "Юридическое лицо" },
  { value: "entrepreneur", label: "ИП" },
  { value: "individual", label: "Физическое лицо" },
];

export const ENTREPRENEUR_INPUTS: CompanyInput[] = [
  {
    field: "full_name",
    label: "Полное наименование",
    placeholder: "Индивидуальный предприниматель Иванов Иван Иванович",
    wide: true,
  },
  { field: "name", label: "Сокращённое наименование", placeholder: "ИП Иванов И. И." },
  { field: "inn", label: "ИНН", placeholder: "12 цифр", numeric: true },
  { field: "ogrn", label: "ОГРНИП", placeholder: "15 цифр", numeric: true },
  {
    field: "address",
    label: "Адрес регистрации",
    placeholder: "630000, г. Новосибирск, ул. Ленина, д. 1, кв. 2",
    wide: true,
  },
  { field: "bank", label: "Банк", placeholder: "АО «Альфа-Банк»", wide: true },
  { field: "bic", label: "БИК", placeholder: "9 цифр", numeric: true },
  { field: "account", label: "Расчётный счёт", placeholder: "20 цифр", numeric: true },
  { field: "corr_account", label: "Корреспондентский счёт", placeholder: "20 цифр", numeric: true },
  { field: "signer_position", label: "Подписант", placeholder: "Индивидуальный предприниматель" },
  { field: "signer_name", label: "ФИО подписанта", placeholder: "Иванов Иван Иванович" },
  {
    field: "signer_genitive",
    label: "В лице кого",
    placeholder: "индивидуального предпринимателя Иванова Ивана Ивановича",
    wide: true,
  },
  { field: "signer_basis", label: "Действует на основании", placeholder: "листа записи ЕГРИП" },
];

export const COMPANY_INPUTS: CompanyInput[] = [
  {
    field: "full_name",
    label: "Полное наименование",
    placeholder: "Общество с ограниченной ответственностью «Ромашка»",
    wide: true,
  },
  { field: "name", label: "Сокращённое наименование", placeholder: "ООО «Ромашка»" },
  { field: "inn", label: "ИНН", placeholder: "10 или 12 цифр", numeric: true },
  { field: "kpp", label: "КПП", placeholder: "Если есть", numeric: true, optional: true },
  { field: "ogrn", label: "ОГРН или ОГРНИП", placeholder: "13 или 15 цифр", numeric: true },
  {
    field: "address",
    label: "Юридический адрес",
    placeholder: "630000, г. Новосибирск, ул. Ленина, д. 1",
    wide: true,
  },
  { field: "bank", label: "Банк", placeholder: "АО «Альфа-Банк»", wide: true },
  { field: "bic", label: "БИК", placeholder: "9 цифр", numeric: true },
  { field: "account", label: "Расчётный счёт", placeholder: "20 цифр", numeric: true },
  { field: "corr_account", label: "Корреспондентский счёт", placeholder: "20 цифр", numeric: true },
  { field: "signer_position", label: "Должность подписанта", placeholder: "Генеральный директор" },
  { field: "signer_name", label: "ФИО подписанта", placeholder: "Иванов Иван Иванович" },
  {
    field: "signer_genitive",
    label: "В лице кого",
    placeholder: "генерального директора Иванова Ивана Ивановича",
    wide: true,
  },
  { field: "signer_basis", label: "Действует на основании", placeholder: "Устава" },
];

export const INDIVIDUAL_INPUTS: IndividualInput[] = [
  { field: "full_name", label: "ФИО полностью", placeholder: "Иванов Иван Иванович", wide: true },
  {
    field: "passport_number",
    label: "Серия и номер паспорта",
    placeholder: "4510 123456",
    numeric: true,
  },
  { field: "passport_issued_at", label: "Дата выдачи", placeholder: "", type: "date" },
  {
    field: "passport_issued_by",
    label: "Кем выдан",
    placeholder: "ГУ МВД России по г. Москве",
    wide: true,
  },
  {
    field: "address",
    label: "Адрес регистрации",
    placeholder: "г. Москва, ул. Тверская, д. 1, кв. 2",
    wide: true,
  },
];
