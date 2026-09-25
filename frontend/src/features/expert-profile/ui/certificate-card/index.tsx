"use client";

import { useState } from "react";
import {
  areaTitle,
  myCertificateScanUrl,
  objectLabel,
  objectTitle,
  type Certificate,
  type ExpertCatalog,
} from "@/entities/expert";
import { formatDate } from "@/shared/lib/date";
import OutlineButton from "@/shared/ui/outline-button";
import styles from "./style.module.scss";

type CertificateCardProps = {
  certificate: Certificate;
  catalog: ExpertCatalog;
  pending: boolean;
  removable: boolean;
  onEdit: () => void;
  onRemove: () => void;
};

const DAY = 24 * 60 * 60 * 1000;
const EXPIRY_WARNING_DAYS = 60;

const daysLeft = (validUntil: string): number => {
  const end = new Date(`${validUntil}T23:59:59`).getTime();

  return Math.ceil((end - Date.now()) / DAY);
};

const CertificateCard = ({
  certificate,
  catalog,
  pending,
  removable,
  onEdit,
  onRemove,
}: CertificateCardProps) => {
  const [confirming, setConfirming] = useState(false);

  const left = daysLeft(certificate.valid_until);
  const expired = left < 0;
  const expiring = !expired && left <= EXPIRY_WARNING_DAYS;

  let termClass = styles.term;
  if (expired) termClass = `${styles.term} ${styles.termExpired}`;
  if (expiring) termClass = `${styles.term} ${styles.termExpiring}`;

  let termText = `до ${formatDate(certificate.valid_until)}`;
  if (expired) termText = `истёк ${formatDate(certificate.valid_until)}`;
  if (expiring) termText = `до ${formatDate(certificate.valid_until)} · осталось ${left} дн.`;

  return (
    <article className={styles.card}>
      <span className={styles.code}>{certificate.area_code}</span>

      <div className={styles.body}>
        <p className={styles.title}>{areaTitle(catalog, certificate.area_code)}</p>
        <p className={styles.object}>
          <span className={styles.objectLabel}>{objectLabel(catalog, certificate.object_code)}</span>
          {objectTitle(catalog, certificate.object_code)}
        </p>

        <div className={styles.meta}>
          <span className={styles.chip}>{certificate.category} категория</span>
          <span className={termClass}>{termText}</span>
          {certificate.number ? (
            <span className={styles.chip}>№ {certificate.number}</span>
          ) : (
            <span className={`${styles.chip} ${styles.chipMissing}`}>Номер не указан</span>
          )}
          {certificate.scan_name && (
            <a
              className={styles.scan}
              href={myCertificateScanUrl(certificate.id)}
              target="_blank"
              rel="noreferrer"
            >
              Скан
            </a>
          )}
        </div>
      </div>

      <div className={styles.actions}>
        {confirming ? (
          <>
            <span className={styles.confirmText}>Удалить удостоверение?</span>
            <button
              type="button"
              className={styles.danger}
              disabled={pending}
              onClick={() => {
                setConfirming(false);
                onRemove();
              }}
            >
              Удалить
            </button>
            <button
              type="button"
              className={styles.ghost}
              disabled={pending}
              onClick={() => setConfirming(false)}
            >
              Оставить
            </button>
          </>
        ) : (
          <>
            <OutlineButton className={styles.edit} disabled={pending} onClick={onEdit}>
              Изменить
            </OutlineButton>
            <button
              type="button"
              className={styles.ghost}
              disabled={pending || !removable}
              title={removable ? undefined : "Должно остаться хотя бы одно удостоверение"}
              onClick={() => setConfirming(true)}
            >
              Удалить
            </button>
          </>
        )}
      </div>
    </article>
  );
};

export default CertificateCard;
