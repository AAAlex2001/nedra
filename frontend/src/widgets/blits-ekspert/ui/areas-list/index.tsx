"use client";

import { useState } from "react";
import type { ExpertCatalog } from "@/entities/expert";
import styles from "./style.module.scss";

type AreasListProps = {
  catalog: ExpertCatalog;
};

const AreasList = ({ catalog }: AreasListProps) => {
  const [areaCode, setAreaCode] = useState(catalog.areas[0].code);

  const current = catalog.areas.find((area) => area.code === areaCode);
  const objects = catalog.objects.filter((object) => current?.objects.includes(object.code));

  return (
    <section className={styles.areas} id="oblasti">
      <div className={styles.heading}>
        <h2 className={styles.title}>Работаем по всем областям аттестации</h2>
        <p className={styles.lead}>
          Э1–Э15 — группы опасных производственных объектов, по которым аттестуется эксперт.
          Выберите свою и посмотрите, что можно отправить на экспертизу.
        </p>
      </div>

      <div className={styles.widget}>
        <div className={styles.rail}>
          {catalog.areas.map((area) => (
            <button
              key={area.code}
              type="button"
              aria-pressed={area.code === areaCode}
              className={`${styles.railItem} ${area.code === areaCode ? styles.railItemActive : ""}`}
              onClick={() => setAreaCode(area.code)}
            >
              <span className={styles.railCode}>{area.code}</span>
              <span className={styles.railName}>{area.title}</span>
            </button>
          ))}
        </div>

        {current && (
          <div className={styles.panel}>
            <p className={styles.panelTitle}>{current.title}</p>

            <div className={styles.objects}>
              <span className={styles.objectsLabel}>Объекты экспертизы</span>
              <ul className={styles.objectsList}>
                {objects.map((object) => (
                  <li key={object.code} className={styles.object}>
                    <span className={styles.objectLabel}>{object.label}</span>
                    <span className={styles.objectTitle}>{object.title}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default AreasList;
