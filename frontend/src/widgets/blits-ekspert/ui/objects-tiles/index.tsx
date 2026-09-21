import Image from "next/image";
import type { ExpertCatalog } from "@/entities/expert";
import { OBJECT_IMAGES } from "../../data";
import styles from "./style.module.scss";

type ObjectsTilesProps = {
  catalog: ExpertCatalog;
};

const ObjectsTiles = ({ catalog }: ObjectsTilesProps) => (
  <section className={styles.objects} id="obekty">
    <h2 className={styles.title}>Что проверяем</h2>

    <div className={styles.grid}>
      {catalog.objects.map((item) => (
        <article key={item.code} className={styles.tile}>
          <div className={styles.picture}>
            <Image
              className={styles.image}
              src={OBJECT_IMAGES[item.code] ?? OBJECT_IMAGES.kl}
              alt={item.title}
              width={800}
              height={800}
              sizes="(min-width: 1440px) 220px, (min-width: 768px) 30vw, 45vw"
            />
          </div>
          <h3 className={styles.name}>{item.title}</h3>
        </article>
      ))}
    </div>
  </section>
);

export default ObjectsTiles;
