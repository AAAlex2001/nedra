const DIGITS = "0123456789";

export const keepDigits = (value: string): string =>
  value
    .split("")
    .filter((char) => DIGITS.includes(char))
    .join("");

export const pluralize = (count: number, forms: [string, string, string]): string => {
  const lastTwo = count % 100;
  const last = count % 10;

  if (lastTwo >= 11 && lastTwo <= 19) return forms[2];
  if (last === 1) return forms[0];
  if (last >= 2 && last <= 4) return forms[1];

  return forms[2];
};
