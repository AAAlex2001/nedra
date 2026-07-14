import DocsCard from "@/shared/ui/docs-card";
import SectionHeading from "@/shared/ui/section-heading";
import { SVEDENIYA_DOCUMENTS } from "./data";

const SvedeniyaDocuments = () => {
  const { title, docs } = SVEDENIYA_DOCUMENTS;

  return (
    <>
      <SectionHeading title={title} />
      <DocsCard docs={docs} />
    </>
  );
};

export default SvedeniyaDocuments;
