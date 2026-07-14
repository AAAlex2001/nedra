import Card from "@/shared/ui/card";
import DocsCard from "@/shared/ui/docs-card";
import { GraduationIcon, InfoIcon } from "@/shared/ui/icons";
import NoteRow from "@/shared/ui/note-row";
import SectionHeading from "@/shared/ui/section-heading";
import { OBRAZOVANIE } from "./data";

const SvedeniyaObrazovanie = () => {
  const { title, notice, qualification, docsTitle, docs } = OBRAZOVANIE;

  return (
    <>
      <SectionHeading title={title} />

      <Card gap={10}>
        <NoteRow icon={<InfoIcon />} divider>
          {notice}
        </NoteRow>
        <NoteRow icon={<GraduationIcon />}>{qualification}</NoteRow>
      </Card>

      <DocsCard title={docsTitle} docs={docs} />
    </>
  );
};

export default SvedeniyaObrazovanie;
