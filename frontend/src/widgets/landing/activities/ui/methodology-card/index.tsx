import Image from "next/image";
import AccentLine from "@/shared/ui/accent-line";
import { CheckIcon } from "@/shared/ui/icons";
import OutlineButton from "@/shared/ui/outline-button";
import type { MethodologyCardData } from "../../data";
import styles from "./style.module.scss";

type MethodologyCardProps = {
  card: MethodologyCardData;
};

const MethodologyCard = ({ card }: MethodologyCardProps) => {
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

        <OutlineButton href={card.button.href}>{card.button.text}</OutlineButton>
      </div>
    </div>
  );
};

export default MethodologyCard;
