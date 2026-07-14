"use client";

import Image from "next/image";
import { useState } from "react";
import AccentLine from "@/shared/ui/accent-line";
import { CheckIcon } from "@/shared/ui/icons";
import Lightbox from "@/shared/ui/lightbox";
import type { MethodologyCardData } from "../../data";
import styles from "./style.module.scss";

type MethodologyCardProps = {
  card: MethodologyCardData;
};

const MethodologyCard = ({ card }: MethodologyCardProps) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.card}>
      <div className={styles.imageWrap}>
        <Image
          src={card.image}
          alt={card.title}
          fill
          sizes="230px"
          className={styles.image}
        />
      </div>

      <div className={styles.content}>
        <h3 className={styles.title}>{card.title}</h3>
        <AccentLine width={50} />
        <p className={styles.number}>{card.number}</p>

        <ul className={styles.points}>
          {card.points.map((point) => (
            <li key={point} className={styles.point}>
              <CheckIcon className={styles.check} />
              <span>{point}</span>
            </li>
          ))}
        </ul>

        <button
          type="button"
          className={styles.docButton}
          onClick={() => setIsOpen(true)}
        >
          {card.button.text}
        </button>
      </div>

      {isOpen && (
        <Lightbox src={card.image} alt={card.title} onClose={() => setIsOpen(false)} />
      )}
    </div>
  );
};

export default MethodologyCard;
