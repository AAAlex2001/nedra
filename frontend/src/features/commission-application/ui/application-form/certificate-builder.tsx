"use client";

import classNames from "classnames";
import { useState } from "react";
import type { ExpertCatalog } from "@/entities/expert";
import Chip from "@/shared/ui/chip";
import type { useCommissionApplication } from "../../model/use-commission-application";
import styles from "./style.module.scss";

type CertificateBuilderProps = {
  catalog: ExpertCatalog;
  application: ReturnType<typeof useCommissionApplication>;
};

const STEPS = ["Область аттестации", "Объект экспертизы", "Категория"];
const LAST_STEP = STEPS.length - 1;

const CertificateBuilder = ({ catalog, application }: CertificateBuilderProps) => {
  const [step, setStep] = useState(0);
  const { state, area, availableObjects, draftComplete } = application;

  const areaChosen = state.draft.areaCode !== "";
  const objectChosen = state.draft.objectCode !== "";
  const stepReady = step === 0 ? areaChosen : objectChosen;

  const addCertificate = () => {
    application.addItem();
    setStep(0);
  };

  return (
    <div className={styles.builder}>
      <div className={styles.steps}>
        <span className={styles.stepTitle}>
          Шаг {step + 1} из {STEPS.length} · {STEPS[step]}
        </span>
        <span className={styles.stepBar} aria-hidden="true">
          {STEPS.map((title, index) => (
            <span
              key={title}
              className={classNames(styles.stepSegment, index <= step && styles.stepDone)}
            />
          ))}
        </span>
      </div>

      {step === 0 && (
        <div className={styles.group}>
          <div className={styles.chips} role="group" aria-label="Область аттестации">
            {catalog.areas.map((item) => (
              <Chip
                key={item.code}
                className={styles.chip}
                active={state.draft.areaCode === item.code}
                title={item.title}
                onClick={() => application.selectArea(item.code)}
              >
                {item.code}
              </Chip>
            ))}
          </div>
          {area && <p className={styles.note}>{area.title}</p>}
        </div>
      )}

      {step === 1 && (
        <div className={styles.group}>
          <div className={styles.chips} role="group" aria-label="Объект экспертизы">
            {availableObjects.map((item) => (
              <Chip
                key={item.code}
                className={styles.chip}
                active={state.draft.objectCode === item.code}
                title={item.title}
                onClick={() => application.selectObject(item.code)}
              >
                {item.label}
              </Chip>
            ))}
          </div>
          {area && <p className={styles.note}>Объекты, доступные для области {area.code}</p>}
        </div>
      )}

      {step === LAST_STEP && (
        <div className={styles.group}>
          <div className={styles.chips} role="group" aria-label="Категория">
            {catalog.categories.map((category) => (
              <Chip
                key={category}
                className={styles.chip}
                active={state.draft.category === category}
                onClick={() => application.selectCategory(category)}
              >
                {category} категория
              </Chip>
            ))}
          </div>
        </div>
      )}

      <div className={styles.stepNav}>
        {step > 0 && (
          <button type="button" className={styles.back} onClick={() => setStep(step - 1)}>
            Назад
          </button>
        )}

        {step < LAST_STEP ? (
          <button
            type="button"
            className={styles.add}
            disabled={!stepReady}
            onClick={() => setStep(step + 1)}
          >
            Далее
          </button>
        ) : (
          <button
            type="button"
            className={styles.add}
            disabled={!draftComplete}
            onClick={addCertificate}
          >
            Добавить аттестацию
          </button>
        )}
      </div>
    </div>
  );
};

export default CertificateBuilder;
