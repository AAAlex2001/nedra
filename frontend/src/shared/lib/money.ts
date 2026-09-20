export const formatRub = (value: string | number | null | undefined): string => {
  if (value === null || value === undefined || value === "") return "по запросу";

  const amount = Number(value);

  if (Number.isNaN(amount)) return String(value);

  const digits = Number.isInteger(amount) ? 0 : 2;

  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(amount);
};

export const halfOf = (value: string | null): string | null => {
  if (value === null) return null;

  const amount = Number(value);

  if (Number.isNaN(amount)) return null;

  return (amount / 2).toFixed(2);
};
