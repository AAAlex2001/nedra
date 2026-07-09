import { SERVICE_CARDS } from "./data";
import Image from "next/image";
import styles from "./style.module.scss";

const ServiceCards = () => {
  return (
    <>
      {SERVICE_CARDS.map((item) => (
        <article key={item.title} className={styles.card}>
          <div className={styles.imageWrap}>
            <Image
              src={item.image}
              alt={item.title}
              fill
              sizes="440px"
              className={styles.image}
            />
            <span className={styles.label}>{item.title}</span>
          </div>

          <div className={styles.overlay}>
            <h3 className={styles.overlayTitle}>{item.title}</h3>
            <p className={styles.overlayText}>{item.description}</p>
          </div>
        </article>
      ))}
    </>
  );
};

export default ServiceCards;
