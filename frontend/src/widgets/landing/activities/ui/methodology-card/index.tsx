import Image from "next/image";
import AccentLine from "@/shared/ui/accent-line";
import { CheckIcon } from "@/shared/ui/icons";
import OutlineButton from "@/shared/ui/outline-button";
import { METHODOLOGY_CARD } from "./data";
import styles from "./style.module.scss";

const MethodologyCard = () => {
  return (
    <div className={styles.card}>
      <div className={styles.imageWrap}>
        <Image
          src={METHODOLOGY_CARD.image}
          alt={METHODOLOGY_CARD.title}
          fill
          sizes="230px"
          className={styles.image}
        />
      </div>

      <div className={styles.content}>
        <h3 className={styles.title}>{METHODOLOGY_CARD.title}</h3>
        <AccentLine width={50} />
        <p className={styles.number}>{METHODOLOGY_CARD.number}</p>

        <ul className={styles.points}>
          {METHODOLOGY_CARD.points.map((point) => (
            <li key={point} className={styles.point}>
              <CheckIcon className={styles.check} />
              <span>{point}</span>
            </li>
          ))}
        </ul>

        <OutlineButton href={METHODOLOGY_CARD.button.href}>
          {METHODOLOGY_CARD.button.text}
        </OutlineButton>
      </div>
    </div>
  );
};

export default MethodologyCard;
