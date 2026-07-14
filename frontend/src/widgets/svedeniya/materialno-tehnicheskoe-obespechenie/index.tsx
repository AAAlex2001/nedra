import Card from "@/shared/ui/card";
import SectionHeading from "@/shared/ui/section-heading";
import { MATERIALNO } from "./data";
import styles from "./style.module.scss";

const SvedeniyaMaterialno = () => {
  const { title, sections } = MATERIALNO;

  return (
    <>
      <SectionHeading title={title} />

      <Card gap={0}>
        {sections.map((section, index) => (
          <div
            key={section.number}
            className={`${styles.section} ${
              index < sections.length - 1 ? styles.divider : ""
            }`}
          >
            <div className={styles.head}>
              <span className={styles.number}>{section.number}.</span>
              <h2 className={styles.sectionTitle}>{section.title}</h2>
            </div>

            <p className={styles.desc}>{section.description}</p>

            <div className={styles.items}>
              {section.items.map((item, itemIndex) => {
                const isFull =
                  section.items.length % 2 === 1 &&
                  itemIndex === section.items.length - 1;

                return (
                  <div
                    key={item.code}
                    className={`${styles.item} ${isFull ? styles.itemFull : ""}`}
                  >
                    <div className={styles.itemHead}>
                      <span className={styles.itemCode}>{item.code}.</span>
                      <span className={styles.itemTitle}>{item.title}</span>
                    </div>

                    {item.intro ? (
                      <p className={styles.itemText}>{item.intro}</p>
                    ) : null}

                    {item.bullets ? (
                      <ul className={styles.itemList}>
                        {item.bullets.map((bullet, bulletIndex) => (
                          <li key={bulletIndex}>{bullet}</li>
                        ))}
                      </ul>
                    ) : null}

                    {item.outro ? (
                      <p className={styles.itemText}>{item.outro}</p>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </Card>
    </>
  );
};

export default SvedeniyaMaterialno;
