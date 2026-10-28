export const initials = (fullName: string): string => {
  const parts = fullName.trim().split(" ").filter((part) => part !== "");
  const letters = parts.slice(0, 2).map((part) => part[0].toUpperCase());

  return letters.join("");
};
