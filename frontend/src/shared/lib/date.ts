const LONG_DATE = new Intl.DateTimeFormat("ru-RU", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

export const formatDate = (value: string | null | undefined): string => {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return LONG_DATE.format(date);
};
