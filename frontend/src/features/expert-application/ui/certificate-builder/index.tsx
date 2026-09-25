"use client";

import type { AttestationArea, ExpertCatalog, ExpertiseObject } from "@/entities/expert";
import Chip from "@/shared/ui/chip";
import TextField from "@/shared/ui/text-field";
import type { CertificateDraft } from "../../model/types";
import styles from "./style.module.scss";

type CertificateBuilderProps = {
  catalog: ExpertCatalog;
  draft: CertificateDraft;
  area: AttestationArea | null;
  availableObjects: ExpertiseObject[];
  complete: boolean;
  onArea: (code: string) => void;
  onObject: (code: string) => void;
  onCategory: (category: number) => void;
  onDate: (value: string) => void;
  onNumber: (value: string) => void;
  onAdd: () => void;
};

const today = (): string => new Date().toISOString().slice(0, 10);

const CertificateBuilder = ({
  catalog,
  draft,
  area,
  availableObjects,
  complete,
  onArea,
  onObject,
  onCategory,
  onDate,
  onNumber,
  onAdd,
}: CertificateBuilderProps) => (
  <div className={styles.builder}>
    <div className={styles.group}>
      <span className={styles.label}>Область аттестации</span>
      <div className={styles.chips} role="group" aria-label="Область аттестации">
        {catalog.areas.map((item) => (
          <Chip
            key={item.code}
            active={draft.areaCode === item.code}
            title={item.title}
            onClick={() => onArea(item.code)}
          >
            {item.code}
          </Chip>
        ))}
      </div>
      {area && <p className={styles.areaTitle}>{area.title}</p>}
    </div>

    <div className={styles.group}>
      <span className={styles.label}>Объект экспертизы</span>
      <div className={styles.chips} role="group" aria-label="Объект экспертизы">
        {catalog.objects.map((item) => {
          const allowed = availableObjects.some((object) => object.code === item.code);

          return (
            <Chip
              key={item.code}
              active={draft.objectCode === item.code}
              disabled={!allowed}
              title={item.title}
              onClick={() => onObject(item.code)}
            >
              {item.label}
            </Chip>
          );
        })}
      </div>
      <p className={styles.note}>
        {area
          ? "Доступны объекты, по которым выдаётся удостоверение для выбранной области."
          : "Сначала выберите область аттестации."}
      </p>
    </div>

    <div className={styles.group}>
      <span className={styles.label}>Категория</span>
      <div className={styles.chips} role="group" aria-label="Категория">
        {catalog.categories.map((category) => (
          <Chip
            key={category}
            active={draft.category === category}
            onClick={() => onCategory(category)}
          >
            {category}
          </Chip>
        ))}
      </div>
    </div>

    <div className={styles.row}>
      <TextField
        label="Дата окончания срока действия квалификационного удостоверения"
        type="date"
        min={today()}
        value={draft.validUntil}
        onChange={onDate}
      />
      <TextField
        label="Номер квалификационного удостоверения либо номер регистрации в ЕРУЛ"
        maxLength={64}
        value={draft.number}
        onChange={onNumber}
      />
    </div>

    <button type="button" className={styles.add} disabled={!complete} onClick={onAdd}>
      Добавить удостоверение
    </button>
  </div>
);

export default CertificateBuilder;
