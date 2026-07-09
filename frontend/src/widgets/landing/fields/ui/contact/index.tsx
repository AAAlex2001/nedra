import { MailIcon, PersonIcon, PhoneIcon } from "@/shared/ui/icons";
import { CONTACT } from "../../data";
import styles from "./style.module.scss";

const FieldsContact = () => {
  return (
    <div className={styles.section}>
      <h4 className={styles.title}>Связаться по направлению</h4>
      <div className={styles.list}>
        <div className={styles.row}>
          <PhoneIcon />
          <a href={`tel:${CONTACT.phone.replace(/\s/g, "")}`}>{CONTACT.phone}</a>
        </div>
        <div className={styles.row}>
          <MailIcon />
          <a href={`mailto:${CONTACT.email}`}>{CONTACT.email}</a>
        </div>
        <div className={styles.row}>
          <PersonIcon />
          <span>{CONTACT.person}</span>
        </div>
      </div>
    </div>
  );
};

export default FieldsContact;
