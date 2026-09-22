"use client";

import Image from "next/image";
import Marquee from "react-fast-marquee";
import type { ExpertCatalog } from "@/entities/expert";
import { OBJECT_IMAGES } from "../../data";
import styles from "./style.module.scss";

type ObjectItem = ExpertCatalog["objects"][number];

type ObjectsTilesProps = {
  catalog: ExpertCatalog;
};

const Tile = ({ item }: { item: ObjectItem }) => (
  <article className={styles.tile}>
    <div className={styles.picture}>
      <Image
        className={styles.image}
        src={OBJECT_IMAGES[item.code] ?? OBJECT_IMAGES.kl}
        alt={item.title}
        width={800}
        height={800}
        sizes="(min-width: 1440px) 220px, (min-width: 768px) 200px, 150px"
      />
    </div>
    <h3 className={styles.name}>{item.title}</h3>
  </article>
);

const ObjectsTiles = ({ catalog }: ObjectsTilesProps) => (
  <section className={styles.objects} id="obekty">
    <h2 className={styles.title}>Что проверяем</h2>

    <div className={styles.line}>
      <Marquee className={styles.marquee} speed={40} autoFill pauseOnHover>
        {catalog.objects.map((item) => (
          <Tile key={item.code} item={item} />
        ))}
      </Marquee>
    </div>

    <div className={styles.grid}>
      {catalog.objects.map((item) => (
        <Tile key={item.code} item={item} />
      ))}
    </div>
  </section>
);

export default ObjectsTiles;
