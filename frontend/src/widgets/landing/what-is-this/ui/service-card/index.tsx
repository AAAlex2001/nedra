"use client";

import Image from "next/image";
import { useState } from "react";
import type { ServiceCardItem } from "../../data";
import styles from "./style.module.scss";

type ServiceCardsProps = {
  cards: ServiceCardItem[];
};

const ServiceCards = ({ cards }: ServiceCardsProps) => {
  const [openTitle, setOpenTitle] = useState<string | null>(null);

  return (
    <>
      {cards.map((item) => {
        const isOpen = openTitle === item.title;

        return (
          <button
            key={item.title}
            type="button"
            className={`${styles.card} ${isOpen ? styles.open : ""}`}
            aria-expanded={isOpen}
            onClick={() => setOpenTitle(isOpen ? null : item.title)}
          >
            <span className={styles.imageWrap}>
              <Image
                src={item.image}
                alt={item.title}
                fill
                sizes="(min-width: 1440px) 440px, 320px"
                className={styles.image}
              />
              <span className={styles.label}>{item.title}</span>
            </span>

            <span className={styles.overlay}>
              <span className={styles.overlayTitle}>{item.title}</span>
              <span className={styles.overlayText}>{item.description}</span>
            </span>
          </button>
        );
      })}
    </>
  );
};

export default ServiceCards;
