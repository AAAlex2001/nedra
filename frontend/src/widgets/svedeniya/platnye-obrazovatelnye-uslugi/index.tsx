import Card from "@/shared/ui/card";
import DocsCard from "@/shared/ui/docs-card";
import { GraduationCapIcon } from "@/shared/ui/icons";
import NoteRow from "@/shared/ui/note-row";
import SectionHeading from "@/shared/ui/section-heading";
import { PLATNYE } from "./data";

const SvedeniyaPlatnye = () => {
  const { title, note, docsTitle, docs } = PLATNYE;

  return (
    <>
      <SectionHeading title={title} />

      <Card gap={10}>
        <NoteRow icon={<GraduationCapIcon />}>{note}</NoteRow>
      </Card>

      <DocsCard title={docsTitle} docs={docs} />
    </>
  );
};

export default SvedeniyaPlatnye;
