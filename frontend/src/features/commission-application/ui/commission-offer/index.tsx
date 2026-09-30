import Image from "next/image";
import Button from "@/shared/ui/button";
import { CheckIcon, CloseIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

const OBJECTS = [
  "Проекты консервации и ликвидации",
  "Проекты технического перевооружения",
  "Декларации промышленной безопасности",
  "Обоснования безопасности",
];

type CommissionOfferProps = {
  onApply: () => void;
  onClose?: () => void;
};

const CommissionOffer = ({ onApply, onClose }: CommissionOfferProps) => (
  <div className={styles.offer}>
    <div className={styles.media}>
      <Image
        className={styles.image}
        src="/services/1.webp"
        alt="Проектная документация, геодезический прибор и лабораторная колба"
        width={1600}
        height={700}
        sizes="(min-width: 768px) 640px, 100vw"
      />
      {onClose && (
        <button type="button" className={styles.close} aria-label="Закрыть" onClick={onClose}>
          <CloseIcon className={styles.closeIcon} />
        </button>
      )}
    </div>

    <div className={styles.content}>
      <span className={styles.badge}>Конкурсный отбор</span>

      <p className={styles.title}>Примем эксперта</p>
      <p className={styles.lead}>
        для выполнения работ по экспертизе промышленной безопасности следующих объектов:
      </p>

      <ul className={styles.points}>
        {OBJECTS.map((item) => (
          <li key={item} className={styles.point}>
            <CheckIcon className={styles.pointIcon} />
            <span className={styles.pointText}>{item}</span>
          </li>
        ))}
      </ul>

      <Button className={styles.cta} onClick={onApply}>
        Оставить заявку в конкурсную комиссию
      </Button>
    </div>
  </div>
);

export default CommissionOffer;
