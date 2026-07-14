import DocsCard from "@/shared/ui/docs-card";
import InfoCard from "@/shared/ui/info-card";
import SectionHeading from "@/shared/ui/section-heading";
import { OSNOVNYE_SVEDENIYA } from "./data";

const SvedeniyaOsnovnye = () => {
  const { title, info, docsTitle, docs } = OSNOVNYE_SVEDENIYA;

  return (
    <>
      <SectionHeading title={title} />
      <InfoCard rows={info} />
      <DocsCard title={docsTitle} docs={docs} />
    </>
  );
};

export default SvedeniyaOsnovnye;
