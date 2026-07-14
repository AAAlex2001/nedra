import type { IconProps } from "./types";

export const OfficialCertificateIcon = ({ className }: IconProps) => (
  <svg
    className={className}
    width="84"
    height="84"
    viewBox="0 0 84 84"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <g filter="url(#filter_official_certificate)">
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
        d="M46.25 53.3725L43.0423 50.1648C42.847 49.9695 42.5305 49.9695 42.3352 50.1648L41.1036 51.3964C40.9083 51.5917 40.9083 51.9083 41.1036 52.1036L45.8964 56.8964C46.0917 57.0917 46.4083 57.0917 46.6036 56.8964L56.8964 46.6036C57.0917 46.4083 57.0917 46.0917 56.8964 45.8964L55.6648 44.6648C55.4695 44.4695 55.153 44.4695 54.9577 44.6648L46.25 53.3725ZM28.375 39.875C28.375 39.5989 28.5989 39.375 28.875 39.375H37.5C37.7761 39.375 38 39.5989 38 39.875V41.625C38 41.9011 37.7761 42.125 37.5 42.125H28.875C28.5989 42.125 28.375 41.9011 28.375 41.625V39.875ZM28.375 33C28.375 32.7239 28.5989 32.5 28.875 32.5H44.375C44.6511 32.5 44.875 32.7239 44.875 33V34.75C44.875 35.0261 44.6511 35.25 44.375 35.25H28.875C28.5989 35.25 28.375 35.0261 28.375 34.75V33ZM28.375 26.125C28.375 25.8489 28.5989 25.625 28.875 25.625H44.375C44.6511 25.625 44.875 25.8489 44.875 26.125V27.875C44.875 28.1511 44.6511 28.375 44.375 28.375H28.875C28.5989 28.375 28.375 28.1511 28.375 27.875V26.125Z"
        fill="#F69827"
      />
      <path
        d="M38 56.75C38 57.0261 37.7761 57.25 37.5 57.25H24.25C22.7334 57.25 21.5 56.0166 21.5 54.5V21.5C21.5 19.9834 22.7334 18.75 24.25 18.75H49C50.5166 18.75 51.75 19.9834 51.75 21.5V41.625C51.75 41.9011 51.5261 42.125 51.25 42.125H49.5C49.2239 42.125 49 41.9011 49 41.625V22C49 21.7239 48.7761 21.5 48.5 21.5H24.75C24.4739 21.5 24.25 21.7239 24.25 22V54C24.25 54.2761 24.4739 54.5 24.75 54.5H37.5C37.7761 54.5 38 54.7239 38 55V56.75Z"
        fill="#F69827"
      />
    </g>
    <defs>
      <filter
        id="filter_official_certificate"
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
