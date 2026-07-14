import type { IconProps } from "./types";

export const BurgerIcon = ({ className }: IconProps) => (
  <svg
    className={className}
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M3 6H21M3 12H21M3 18H21"
      stroke="#1A1A1A"
      strokeWidth="2"
      strokeLinecap="round"
    />
  </svg>
);
