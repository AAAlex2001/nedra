"use client";

import { useState } from "react";
import { expertiseSigningUrl, type ServiceKind } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import { DocumentIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type ContractConsentProps = {
  service: ServiceKind;
  expertiseId: number;
  pending: boolean;
  onSign: () => void;
};

const DOCUMENTS = [
  { kind: "contract", title: "Договор на экспертизу" },
  { kind: "nda", title: "Соглашение о конфиденциальности" },
] as const;

const ContractConsent = ({ expertiseId, service, pending, onSign }: ContractConsentProps) => {
  const [agreed, setAgreed] = useState(false);

  return (
    <div className={styles.consent}>
      <div className={styles.documents}>
        {DOCUMENTS.map((document) => (
          <a
            key={document.kind}
            className={styles.document}
            href={expertiseSigningUrl(expertiseId, document.kind, service)}
            target="_blank"
            rel="noreferrer"
          >
            <span className={styles.tile}>
              <DocumentIcon className={styles.icon} />
            </span>
            <span className={styles.caption}>
              <span className={styles.title}>{document.kind === "contract" && service === "audit" ? "Договор на аудит" : document.title}</span>
              <span className={styles.hint}>Word · заполнен по вашей заявке</span>
            </span>
          </a>
        ))}
      </div>

      <div className={styles.footer}>
        <label className={styles.checkbox}>
          <input
            type="checkbox"
            className={styles.input}
            checked={agreed}
            onChange={(event) => setAgreed(event.target.checked)}
          />
          <span className={styles.box} aria-hidden="true">
            <svg className={styles.mark} viewBox="0 0 16 16" fill="none">
              <path
                d="M3.5 8.5L6.5 11.5L12.5 5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <span className={styles.label}>
            Я прочитал договор и соглашение о конфиденциальности и согласен с их условиями
          </span>
        </label>

        <Button className={styles.button} disabled={!agreed} loading={pending} onClick={onSign}>
          Подписать
        </Button>
      </div>
    </div>
  );
};

export default ContractConsent;
