import type { IconProps } from "./types";

export const ThumbDownIcon = ({ className }: IconProps) => (
  <svg
    className={className}
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <path
      d="M17 14V3h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1h-3Zm0 0-4.5 7.2a1.6 1.6 0 0 1-2.9-1.1l.8-5.1H5a2 2 0 0 1-2-2.3l1.2-7.9A2 2 0 0 1 6.2 3H17"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
