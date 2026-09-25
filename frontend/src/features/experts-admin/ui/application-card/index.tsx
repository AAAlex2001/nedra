"use client";

import {
  APPLICATION_STATUS_LABELS,
  areaTitle,
  directionTitle,
  formatCategory,
  objectLabel,
  type ExpertApplicationRecord,
  type ExpertCatalog,
} from "@/entities/expert";
import { useState } from "react";
import { formatRequestDate } from "@/entities/request";
import { formatDate } from "@/shared/lib/date";
import Spinner from "@/shared/ui/spinner";
import { scanUrl } from "../../api/applications";
import ExpertEditor from "../expert-editor";
import styles from "./style.module.scss";

type ApplicationCardProps = {
  application: ExpertApplicationRecord;
  catalog: ExpertCatalog | null;
  basePath: string;
  pending: boolean;
  onApprove: (id: number) => void;
  onReject: (id: number, comment: string) => void;
  onDeleteExpert: (application: ExpertApplicationRecord) => void;
  onUpdated: () => void;
};

const STATUS_CLASS = {
  pending: "statusPending",
  approved: "statusApproved",
  rejected: "statusRejected",
} as const;

const ApplicationCard = ({
  application,
  catalog,
  basePath,
  pending,
  onApprove,
  onReject,
  onDeleteExpert,
  onUpdated,
}: ApplicationCardProps) => {
  const [editing, setEditing] = useState(false);

  const handleApprove = () => {
    if (window.confirm(`Одобрить заявку №${application.id} и создать аккаунт эксперта?`)) {
      onApprove(application.id);
    }
  };

  const handleReject = () => {
    const comment = window.prompt("Причина отклонения. Её увидит эксперт в письме:");
    if (comment && comment.trim().length >= 3) {
      onReject(application.id, comment.trim());
    }
  };

  const handleDeleteExpert = () => {
    if (
      window.confirm(
        `Удалить аккаунт эксперта ${application.full_name}? Удостоверения и доступ в кабинет пропадут.`,
      )
    ) {
      onDeleteExpert(application);
    }
  };

  const canDeleteExpert = application.status === "approved" && application.user_id !== null;

  return (
    <article className={`${styles.card} ${pending ? styles.cardPending : ""}`}>
      <header className={styles.head}>
        <div className={styles.headMain}>
          <span className={styles.id}>№{application.id}</span>
          <time className={styles.date} dateTime={application.created_at}>
            {formatRequestDate(application.created_at)}
          </time>
          <span className={`${styles.status} ${styles[STATUS_CLASS[application.status]]}`}>
            {APPLICATION_STATUS_LABELS[application.status]}
          </span>
        </div>

        {application.status === "pending" && (
          <div className={styles.actions}>
            <button
              type="button"
              className={styles.approve}
              disabled={pending}
              onClick={handleApprove}
            >
              {pending ? <Spinner size={14} tone="light" /> : "Одобрить"}
            </button>
            <button
              type="button"
              className={styles.reject}
              disabled={pending}
              onClick={handleReject}
            >
              Отклонить
            </button>
          </div>
        )}

        {canDeleteExpert && (
          <div className={styles.actions}>
            <button
              type="button"
              className={styles.edit}
              disabled={pending}
              onClick={() => setEditing(!editing)}
            >
              {editing ? "Скрыть правку" : "Изменить"}
            </button>
            <button
              type="button"
              className={styles.reject}
              disabled={pending}
              onClick={handleDeleteExpert}
            >
              {pending ? <Spinner size={14} /> : "Удалить эксперта"}
            </button>
          </div>
        )}
      </header>

      <dl className={styles.details}>
        <div className={styles.detail}>
          <dt className={styles.term}>Эксперт</dt>
          <dd className={styles.value}>{application.full_name}</dd>
        </div>
        <div className={styles.detail}>
          <dt className={styles.term}>Email</dt>
          <dd className={styles.value}>
            <a className={styles.link} href={`mailto:${application.email}`}>
              {application.email}
            </a>
          </dd>
        </div>
        <div className={styles.detail}>
          <dt className={styles.term}>Телефон</dt>
          <dd className={styles.value}>
            <a className={styles.link} href={`tel:${application.phone}`}>
              {application.phone}
            </a>
          </dd>
        </div>
      </dl>

      <div className={styles.block}>
        <span className={styles.blockTitle}>Направления</span>
        <div className={styles.tags}>
          {application.directions.map((code) => (
            <span key={code} className={styles.tag}>
              {catalog ? directionTitle(catalog, code) : code}
            </span>
          ))}
        </div>
      </div>

      <div className={styles.block}>
        <span className={styles.blockTitle}>Удостоверения</span>
        <ul className={styles.certificates}>
          {application.certificates.map((item) => (
            <li key={item.id} className={styles.certificate}>
              <div className={styles.certificateHead}>
                <span className={styles.code}>{item.area_code}</span>
                <span className={styles.object}>
                  {catalog ? objectLabel(catalog, item.object_code) : item.object_code}
                </span>
                <span className={styles.meta}>{formatCategory(item.category)}</span>
                <span className={styles.meta}>до {formatDate(item.valid_until)}</span>
                {item.number && <span className={styles.meta}>№ {item.number}</span>}
                {item.scan_name && (
                  <a
                    className={styles.scanLink}
                    href={scanUrl(basePath, application.id, item.id)}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Скан
                  </a>
                )}
              </div>
              {catalog && (
                <p className={styles.certificateTitle}>{areaTitle(catalog, item.area_code)}</p>
              )}
            </li>
          ))}
        </ul>
      </div>

      {editing && application.user_id !== null && (
        <ExpertEditor
          userId={application.user_id}
          fullName={application.full_name}
          phone={application.phone}
          directions={application.directions}
          certificates={application.certificates}
          catalog={catalog}
          basePath={basePath}
          onUpdated={onUpdated}
        />
      )}

      {application.admin_comment && (
        <p className={styles.comment}>Причина отклонения: {application.admin_comment}</p>
      )}
    </article>
  );
};

export default ApplicationCard;
