import { DIRECTION_OPTIONS } from "@/entities/service";
import { RequestForm } from "@/features/request-form";
import BlockHeading from "@/shared/ui/block-heading";
import { REQUEST_SECTION_DATA } from "./data";
import styles from "./style.module.scss";

const RequestSection = () => {
  return (
    <section id="request" className={styles.section}>
      <BlockHeading
        title={REQUEST_SECTION_DATA.title}
        subtitle={REQUEST_SECTION_DATA.subtitle}
      />

      <RequestForm directions={DIRECTION_OPTIONS} />
    </section>
  );
};

export default RequestSection;
