"use client";

import Image from "next/image";
import { useCallback, useState } from "react";
import { DIRECTION_OPTIONS, type DirectionOption } from "@/entities/service";
import { RequestForm } from "@/features/request-form";
import AccentLine from "@/shared/ui/accent-line";
import { CheckIcon } from "@/shared/ui/icons";
import { REQUEST_SECTION_DATA } from "./data";
import styles from "./style.module.scss";

const RequestSection = () => {
  const [direction, setDirection] = useState<DirectionOption | null>(null);

  const handleDirectionChange = useCallback(
    (next: DirectionOption | null) => setDirection(next),
    [],
  );

  const image = direction?.image ?? REQUEST_SECTION_DATA.fallbackImage;

  return (
    <section id="request" className={styles.section}>
      <div className={styles.heading}>
        <h2 className={styles.title}>{REQUEST_SECTION_DATA.title}</h2>
        <AccentLine width={30} />
        <p className={styles.subtitle}>{REQUEST_SECTION_DATA.subtitle}</p>
      </div>

      <div className={styles.card}>
        <div className={styles.formColumn}>
          <RequestForm
            directions={DIRECTION_OPTIONS}
            onDirectionChange={handleDirectionChange}
          />
        </div>

        <aside className={styles.aside}>
          <div className={styles.imageWrap}>
            <Image
              src={image}
              alt=""
              fill
              sizes="(max-width: 1440px) 100vw, 360px"
              className={styles.image}
            />
          </div>

          <ul className={styles.benefits}>
            {REQUEST_SECTION_DATA.benefits.map((benefit) => (
              <li key={benefit} className={styles.benefit}>
                <CheckIcon className={styles.benefitIcon} />
                <span>{benefit}</span>
              </li>
            ))}
          </ul>
        </aside>
      </div>
    </section>
  );
};

export default RequestSection;
