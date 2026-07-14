import type { IconProps } from "./types";

export const OfficialResultsIcon = ({ className }: IconProps) => (
  <svg
    className={className}
    width="84"
    height="84"
    viewBox="0 0 84 84"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <g filter="url(#filter_official_results)">
      <rect
        x="6"
        y="6"
        width="64"
        height="64"
        rx="20"
        fill="white"
        shapeRendering="crispEdges"
      />
      <path
        d="M53.5833 35.25V51.75C53.5833 52.6043 53.5833 53.0315 53.444 53.3688C53.2575 53.8172 52.9008 54.1732 52.4522 54.3588C52.1148 54.5 51.6877 54.5 50.8333 54.5C49.979 54.5 49.5518 54.5 49.2145 54.3607C48.7662 54.1742 48.4101 53.8175 48.2245 53.3688C48.0833 53.0315 48.0833 52.6043 48.0833 51.75V35.25C48.0833 34.3957 48.0833 33.9685 48.2227 33.6312C48.4091 33.1828 48.7658 32.8268 49.2145 32.6412C49.5518 32.5 49.979 32.5 50.8333 32.5C51.6877 32.5 52.1148 32.5 52.4522 32.6393C52.9005 32.8258 53.2565 33.1825 53.4422 33.6312C53.5833 33.9685 53.5833 34.3957 53.5833 35.25Z"
        stroke="#F69827"
        strokeWidth="3"
        strokeLinejoin="round"
      />
      <path
        d="M46.25 21.5H51.75V27"
        stroke="#F69827"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M50.8333 22.4165C50.8333 22.4165 43.5 31.5832 24.25 37.9998"
        stroke="#F69827"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M40.75 41.6665V51.7498C40.75 52.6042 40.75 53.0313 40.6107 53.3687C40.4242 53.817 40.0675 54.173 39.6188 54.3587C39.2815 54.4998 38.8543 54.4998 38 54.4998C37.1457 54.4998 36.7185 54.4998 36.3812 54.3605C35.9328 54.174 35.5768 53.8173 35.3912 53.3687C35.25 53.0313 35.25 52.6042 35.25 51.7498V41.6665C35.25 40.8122 35.25 40.385 35.3893 40.0477C35.5758 39.5993 35.9325 39.2433 36.3812 39.0577C36.7185 38.9165 37.1457 38.9165 38 38.9165C38.8543 38.9165 39.2815 38.9165 39.6188 39.0558C40.0672 39.2423 40.4232 39.599 40.6088 40.0477C40.75 40.385 40.75 40.8122 40.75 41.6665ZM27.9167 46.2498V51.7498C27.9167 52.6042 27.9167 53.0313 27.7773 53.3687C27.5909 53.817 27.2342 54.173 26.7855 54.3587C26.4482 54.4998 26.021 54.4998 25.1667 54.4998C24.3123 54.4998 23.8852 54.4998 23.5478 54.3605C23.0995 54.174 22.7435 53.8173 22.5578 53.3687C22.4167 53.0313 22.4167 52.6042 22.4167 51.7498V46.2498C22.4167 45.3955 22.4167 44.9683 22.556 44.631C22.7425 44.1827 23.0992 43.8266 23.5478 43.641C23.8852 43.4998 24.3123 43.4998 25.1667 43.4998C26.021 43.4998 26.4482 43.4998 26.7855 43.6392C27.2338 43.8256 27.5899 44.1823 27.7755 44.631C27.9167 44.9683 27.9167 45.3955 27.9167 46.2498Z"
        stroke="#F69827"
        strokeWidth="3"
        strokeLinejoin="round"
      />
    </g>
    <defs>
      <filter
        id="filter_official_results"
        x="0"
        y="0"
        width="84"
        height="84"
        filterUnits="userSpaceOnUse"
        colorInterpolationFilters="sRGB"
      >
        <feFlood floodOpacity="0" result="BackgroundImageFix" />
        <feColorMatrix
          in="SourceAlpha"
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
          result="hardAlpha"
        />
        <feOffset dx="4" dy="4" />
        <feGaussianBlur stdDeviation="5" />
        <feComposite in2="hardAlpha" operator="out" />
        <feColorMatrix
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.05 0"
        />
        <feBlend
          mode="normal"
          in2="BackgroundImageFix"
          result="effect1_dropShadow"
        />
        <feBlend
          mode="normal"
          in="SourceGraphic"
          in2="effect1_dropShadow"
          result="shape"
        />
      </filter>
    </defs>
  </svg>
);
