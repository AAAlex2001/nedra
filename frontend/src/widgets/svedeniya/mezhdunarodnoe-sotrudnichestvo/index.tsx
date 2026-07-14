import InfoCard from "@/shared/ui/info-card";
import SectionHeading from "@/shared/ui/section-heading";
import { MEZHDUNARODNOE } from "./data";

const SvedeniyaMezhdunarodnoe = () => {
  const { title, rows } = MEZHDUNARODNOE;

  return (
    <>
      <SectionHeading title={title} />
      <InfoCard rows={rows} />
    </>
  );
};

export default SvedeniyaMezhdunarodnoe;
