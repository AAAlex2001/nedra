import type { SectionIcon as SectionIconType } from "../../model/sections";

type SectionIconProps = {
  icon: SectionIconType | "logout";
};

const SectionIcon = ({ icon }: SectionIconProps) => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="1.7"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    {icon === "inbox" && (
      <>
        <path d="M4 13h4l1.5 3h5l1.5-3h4" />
        <path d="M5 5h14l1 8v6H4v-6l1-8Z" />
      </>
    )}
    {icon === "work" && (
      <>
        <rect x="3" y="7" width="18" height="13" rx="2" />
        <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18" />
      </>
    )}
    {icon === "done" && (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="m8 12 3 3 5-6" />
      </>
    )}
    {icon === "expert" && (
      <>
        <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" />
        <path d="m8.5 12 2.5 2.5 4.5-5" />
      </>
    )}
    {icon === "audit" && (
      <>
        <rect x="5" y="5" width="14" height="16" rx="2" />
        <rect x="9" y="3" width="6" height="4" rx="1" />
        <path d="m8 12 1 1 2-2m2 1h3m-8 5 1 1 2-2m2 1h3" />
      </>
    )}
    {icon === "invoice" && (
      <>
        <path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z" />
        <path d="M9 8h6M9 12h6" />
      </>
    )}
    {icon === "act" && (
      <>
        <path d="M7 3h7l5 5v13H7V3Z" />
        <path d="M14 3v5h5M10 13h6M10 17h4" />
      </>
    )}
    {icon === "account" && (
      <>
        <circle cx="12" cy="8" r="3.5" />
        <path d="M5 21v-2a7 7 0 0 1 14 0v2" />
      </>
    )}
    {icon === "bell" && (
      <>
        <path d="M6 16v-5a6 6 0 0 1 12 0v5l2 2H4l2-2Z" />
        <path d="M10 20a2 2 0 0 0 4 0" />
      </>
    )}
    {icon === "logout" && (
      <>
        <path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3" />
        <path d="m10 16-4-4 4-4M6 12h10" />
      </>
    )}
  </svg>
);

export default SectionIcon;
