import InfoCard from "@/shared/ui/info-card";
import SectionHeading from "@/shared/ui/section-heading";
import { VAKANTNYE } from "./data";

const SvedeniyaVakantnye = () => {
  const { title, rows } = VAKANTNYE;

  return (
    <>
      <SectionHeading title={title} />
      <InfoCard rows={rows} />
    </>
  );
};

export default SvedeniyaVakantnye;
