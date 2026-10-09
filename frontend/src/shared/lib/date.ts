const LONG_DATE = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

export const formatDate = (value: string | null | undefined): string => {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return LONG_DATE.format(date).replace(" г.", "");
};

const SHORT_DATE = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
});

const DATE_TIME = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export const formatShortDate = (value: string | null | undefined): string => {
  if (!value) return "";

  const date = new Date(value);

  return Number.isNaN(date.getTime()) ? value : SHORT_DATE.format(date);
};

export const formatDateTime = (value: string | null | undefined): string => {
  if (!value) return "";

  const date = new Date(value);

  return Number.isNaN(date.getTime()) ? value : DATE_TIME.format(date);
};

const twoDigits = (value: number) => String(value).padStart(2, "0");

export const toDateTimeInput = (value: string | null | undefined): string => {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "";

  const day = `${date.getFullYear()}-${twoDigits(date.getMonth() + 1)}-${twoDigits(date.getDate())}`;
  const time = `${twoDigits(date.getHours())}:${twoDigits(date.getMinutes())}`;

  return `${day}T${time}`;
};

export const isFutureDate = (value: string | null | undefined): boolean => {
  if (!value) return false;

  return new Date(value).getTime() > Date.now();
};
