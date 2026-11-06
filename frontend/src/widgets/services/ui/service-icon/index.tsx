const ICON_PATHS = {
  design: "M3 21V3h12v18M15 9h6v12M1 21h22M6 7h2m3 0h1M6 11h2m3 0h1M6 15h2m3 0h1M7 21v-3h4v3M18 12h1m-1 4h1",
  research: "M8 2h8M10 2v7L4 19a1.5 1.5 0 0 0 1 2h14a1.5 1.5 0 0 0 1-2L14 9V2M7 15h10M9 18h.01M14 12h.01",
  safety: "m12 2 8 3v7c0 5-8 10-8 10s-8-5-8-10V5l8-3ZM8 12l3 3 5-6",
  heritage: "m12 2 10 5H2l10-5ZM4 10v8m5-8v8m6-8v8m5-8v8M3 18h18M1 22h22",
  ecology: "M5 17C0 7 9 2 21 3c1 12-4 20-14 16M3 22 17 8M8 17v-6m0 6h7",
  certification: "M2 5h8l3 3h9v13H2V5ZM7 14l3 3 7-6",
  laboratory: "m9 2 6 3-5 9-6-3 5-9ZM7 1l10 5M15 10a6 6 0 0 1 0 12H4M3 17h9M8 17v5",
  education: "m12 3 11 5-11 5L1 8l11-5ZM5 10v7l7 4 7-4v-7m3-1v10",
  nuclear: "M21 12c0 2.2-4 4-9 4s-9-1.8-9-4 4-4 9-4 9 1.8 9 4ZM16.5 4.2c1.9 1.1 1.4 5.5-1.1 9.8s-6.1 7-8 5.8-1.4-5.5 1.1-9.8 6.1-7 8-5.8ZM7.5 4.2c1.9-1.1 5.5 1.5 8 5.8s3 8.7 1.1 9.8-5.5-1.5-8-5.8-3-8.7-1.1-9.8ZM12 12h.01",
};

export type ServiceIconName = keyof typeof ICON_PATHS;

type ServiceIconProps = {
  name: ServiceIconName;
};

const ServiceIcon = ({ name }: ServiceIconProps) => (
  <svg
    width="32"
    height="32"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.4"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d={ICON_PATHS[name]} />
  </svg>
);

export default ServiceIcon;
