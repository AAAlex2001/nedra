import type { IconProps } from "./types";

export const ThumbUpIcon = ({ className }: IconProps) => (
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
      d="M7 10v11H4a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1h3Zm0 0 4.5-7.2a1.6 1.6 0 0 1 2.9 1.1L13.6 9H19a2 2 0 0 1 2 2.3l-1.2 7.9A2 2 0 0 1 17.8 21H7"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);
