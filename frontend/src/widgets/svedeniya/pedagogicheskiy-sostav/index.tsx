import Card from "@/shared/ui/card";
import { UserCircleIcon } from "@/shared/ui/icons";
import SectionHeading from "@/shared/ui/section-heading";
import { PEDAGOGICHESKIY_SOSTAV } from "./data";
import styles from "./style.module.scss";

const SvedeniyaPedagogicheskiySostav = () => {
  const { title, teachers } = PEDAGOGICHESKIY_SOSTAV;

  const staffJsonLd = {
    "@context": "https://schema.org",
    "@type": "ItemList",
    name: title,
    itemListElement: teachers.map((teacher, index) => ({
      "@type": "ListItem",
      position: index + 1,
      item: {
        "@type": "Person",
        name: teacher.name,
        jobTitle: teacher.role,
        worksFor: {
          "@type": "Organization",
          name: "НПИ «Недра»",
        },
      },
    })),
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(staffJsonLd) }}
      />
      <SectionHeading title={title} />

      <div className={styles.cards}>
        {teachers.map((teacher) => (
          <Card key={teacher.name} gap={20}>
            <div className={styles.person}>
              <UserCircleIcon className={styles.personIcon} />
              <div className={styles.personInfo}>
                <span className={styles.personName}>{teacher.name}</span>
                <span className={styles.personRole}>{teacher.role}</span>
              </div>
            </div>

            <p className={styles.diploma}>{teacher.diploma}</p>

            <div className={styles.download}>
              <span className={styles.downloadLabel}>Диплом:</span>
              <a
                className={styles.downloadLink}
                href={teacher.href}
                target="_blank"
                rel="noopener noreferrer"
              >
                Скачать
              </a>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
};

export default SvedeniyaPedagogicheskiySostav;
