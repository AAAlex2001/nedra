"use client";

import classNames from "classnames";
import Image from "next/image";
import Link from "next/link";
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
        const content = (
          <>
            <span className={styles.imageWrap}>
              <Image
                src={item.image}
                alt={item.title}
                fill
                sizes="(min-width: 1440px) 433px, (min-width: 768px) calc(100vw - 100px), calc(100vw - 40px)"
                quality={82}
                loading="lazy"
                decoding="async"
                className={styles.image}
              />
              <span className={styles.label}>{item.title}</span>
            </span>

            <span className={styles.overlay}>
              <span className={styles.overlayTitle}>{item.title}</span>
              <span className={styles.overlayText}>{item.description}</span>
              {item.href && (
                <span className={styles.linkHint}>
                  Перейти
                  <svg
                    width="20"
                    height="20"
                    viewBox="0 0 20 20"
                    fill="none"
                    aria-hidden="true"
                  >
                    <path
                      d="M4.167 10h11.666m-4.166-4.167L15.833 10l-4.166 4.167"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
              )}
            </span>
          </>
        );

        if (item.href) {
          return (
            <Link key={item.title} className={styles.card} href={item.href}>
              {content}
            </Link>
          );
        }

        return (
          <button
            key={item.title}
            type="button"
            className={classNames(styles.card, isOpen && styles.open)}
            aria-expanded={isOpen}
            onClick={() => setOpenTitle(isOpen ? null : item.title)}
          >
            {content}
          </button>
        );
      })}
    </>
  );
};

export default ServiceCards;
