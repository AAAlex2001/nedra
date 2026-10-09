"use client";

import classNames from "classnames";
import { useState } from "react";
import type { AuditChecklistItem } from "@/entities/expertise";
import styles from "./style.module.scss";

type ChecklistPreviewProps = {
  checklist: AuditChecklistItem[];
};

const ChecklistPreview = ({ checklist }: ChecklistPreviewProps) => {
  const [number, setNumber] = useState(checklist[0].number);

  const current = checklist.find((item) => item.number === number);

  return (
    <section className={styles.section} id="perechen">
      <div className={styles.heading}>
        <h2 className={styles.title}>Какие документы проверяет аудитор</h2>
        <p className={styles.lead}>
          Перечень из {checklist.length} пунктов повторяет запрос Ростехнадзора при проверке.
          Загружать всё не обязательно — аудит проводится по тому, что вы представите.
        </p>
      </div>

      <div className={styles.widget}>
        <div className={styles.rail}>
          {checklist.map((item) => (
            <button
              key={item.number}
              type="button"
              aria-pressed={item.number === number}
              className={classNames(styles.railItem, item.number === number && styles.railItemActive)}
              onClick={() => setNumber(item.number)}
            >
              <span className={styles.railNumber}>{item.number}</span>
              <span className={styles.railName}>{item.title}</span>
            </button>
          ))}
        </div>

        {current && (
          <div className={styles.panel}>
            <span className={styles.panelBadge}>
              Пункт {current.number} из {checklist.length}
            </span>
            <p className={styles.panelTitle}>{current.title}</p>

            <div className={styles.hint}>
              <span className={styles.hintLabel}>Как загрузить</span>
              <p className={styles.hintText}>
                В заявке у каждого пункта своя кнопка «Прикрепить» — можно приложить несколько
                файлов в PDF, Word, Excel или фото. Если документа нет, пропустите пункт: аудитор
                отметит это в отчёте и подскажет, что подготовить.
              </p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default ChecklistPreview;
