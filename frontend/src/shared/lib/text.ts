const DIGITS = "0123456789";

export const keepDigits = (value: string): string =>
  value
    .split("")
    .filter((char) => DIGITS.includes(char))
    .join("");
