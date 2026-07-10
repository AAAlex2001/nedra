import ContactRow from "@/shared/ui/contact-row";
import { MailIcon, PersonIcon, PhoneIcon } from "@/shared/ui/icons";
import type { SubService } from "../../data";
import styles from "./style.module.scss";

type ServiceDetailsProps = {
  service: SubService;
};

const ServiceDetails = ({ service }: ServiceDetailsProps) => {
  const { contact } = service;

  return (
    <div className={styles.card}>
      {service.sections.map((section) => (
        <div key={section.title} className={styles.section}>
          <h4 className={styles.title}>{section.title}</h4>

          {section.text && <p className={styles.text}>{section.text}</p>}

          {section.bullets && (
            <ul className={styles.list}>
              {section.bullets.map((bullet) => (
                <li key={bullet} className={styles.bullet}>
                  <span className={styles.dot} aria-hidden="true" />
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>
          )}

          {section.trailing && <p className={styles.text}>{section.trailing}</p>}
        </div>
      ))}

      <div className={styles.section}>
        <h4 className={styles.title}>Связаться по направлению</h4>
        <div className={styles.contact}>
          <ContactRow icon={<PhoneIcon />} href={`tel:${contact.phone.replace(/[\s-]/g, "")}`}>
            {contact.phone}
          </ContactRow>
          {contact.email && (
            <ContactRow icon={<MailIcon />} href={`mailto:${contact.email}`}>
              {contact.email}
            </ContactRow>
          )}
          <ContactRow icon={<PersonIcon />}>{contact.person}</ContactRow>
        </div>
      </div>
    </div>
  );
};

export default ServiceDetails;
