"use client";

import Image from "next/image";
import { useState } from "react";
import { DIRECTION_OPTIONS } from "@/entities/service";
import { RequestForm } from "@/features/request-form";
import BlockHeading from "@/shared/ui/block-heading";
import { CheckIcon } from "@/shared/ui/icons";
import { REQUEST_SECTION_DATA } from "./data";
import styles from "./style.module.scss";

const RequestSection = () => {
  const [directionId, setDirectionId] = useState("");

  const direction = DIRECTION_OPTIONS.find((item) => item.id === directionId);
  const image = direction?.image ?? REQUEST_SECTION_DATA.fallbackImage;

  return (
    <section id="request" className={styles.section}>
      <BlockHeading
        title={REQUEST_SECTION_DATA.title}
        subtitle={REQUEST_SECTION_DATA.subtitle}
      />

      <div className={styles.card}>
        <div className={styles.formColumn}>
          <RequestForm
            directions={DIRECTION_OPTIONS}
            onDirectionChange={setDirectionId}
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
