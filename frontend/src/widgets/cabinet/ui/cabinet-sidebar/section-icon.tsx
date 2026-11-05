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
        <path d="M3 13h5l2 3h4l2-3h5v7H3Z" fill="currentColor" fillOpacity=".12" />
        <path d="m3 13 3-6h3m12 6-3-6h-3M12 3v8m-3-3 3 3 3-3" />
      </>
    )}
    {icon === "work" && (
      <>
        <rect x="3" y="7" width="18" height="13" rx="3" fill="currentColor" fillOpacity=".1" />
        <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 12a22 22 0 0 0 18 0" />
        <path d="M10 12v3h4v-3" fill="currentColor" fillOpacity=".2" />
      </>
    )}
    {icon === "done" && (
      <>
        <path d="m12 2 3 2 3.5.5.5 3.5 2 3-2 3-.5 3.5-3.5.5-3 2-3-2-3.5-.5L5 14l-2-3 2-3 .5-3.5L9 4Z" fill="currentColor" fillOpacity=".12" />
        <path d="m8 11 2.5 2.5L16 8" />
      </>
    )}
    {icon === "expert" && (
      <>
        <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" fill="currentColor" fillOpacity=".1" />
        <path d="m13 7-5 6h4l-1 4 5-6h-4l1-4Z" fill="currentColor" strokeWidth="1.2" />
      </>
    )}
    {icon === "audit" && (
      <>
        <path d="M11 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v4" />
        <path d="M6 7h7M6 11h3M6 15h3" />
        <circle cx="16" cy="15" r="4" fill="currentColor" fillOpacity=".12" />
        <path d="m19 18 3 3m-8-6 1.5 1.5L18 14" />
      </>
    )}
    {icon === "invoice" && (
      <>
        <path d="M5 3h14v18l-3.5-2-3.5 2-3.5-2L5 21V3Z" fill="currentColor" fillOpacity=".1" />
        <path d="M9 16V7h3a2.5 2.5 0 0 1 0 5H8m0 2h5" />
      </>
    )}
    {icon === "act" && (
      <>
        <path d="M5 3h9l5 5v4M5 3v18h8M14 3v5h5M8 8h3M8 12h5" />
        <circle cx="17" cy="17" r="4" fill="currentColor" fillOpacity=".12" />
        <path d="m15 17 1.3 1.3L19 15.5" />
      </>
    )}
    {icon === "account" && (
      <>
        <rect x="3" y="3" width="18" height="18" rx="5" fill="currentColor" fillOpacity=".08" />
        <circle cx="12" cy="9" r="3" />
        <path d="M7 18a5 5 0 0 1 10 0" />
      </>
    )}
    {icon === "bell" && (
      <>
        <path d="M6 16v-5a6 6 0 0 1 8-5.7M18 12v4l2 2H4l2-2Z" fill="currentColor" fillOpacity=".1" />
        <path d="M10 21h4M12 3v2" />
        <circle cx="19" cy="6" r="3" fill="#f69827" stroke="#f69827" />
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
