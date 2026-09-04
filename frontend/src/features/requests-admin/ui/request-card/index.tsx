"use client";

import { formatRequestDate, type RequestRecord } from "@/entities/request";
import { findByActivity } from "@/entities/service";
import styles from "./style.module.scss";

type RequestCardProps = {
  request: RequestRecord;
  pending: boolean;
  onDelete: (id: number) => void;
};

const RequestCard = ({ request, pending, onDelete }: RequestCardProps) => {
  const match = findByActivity(request.activity);

  return (
    <article className={`${styles.card} ${pending ? styles.cardPending : ""}`}>
      <header className={styles.head}>
        <div className={styles.headMain}>
          <span className={styles.id}>№{request.request_id}</span>
          <time className={styles.date} dateTime={request.created_at}>
            {formatRequestDate(request.created_at)}
          </time>
        </div>

        <button
          type="button"
          className={styles.delete}
          disabled={pending}
          onClick={() => {
            if (window.confirm(`Удалить заявку №${request.request_id}?`)) {
              onDelete(request.request_id);
            }
          }}
        >
          {pending ? "Удаляем…" : "Удалить"}
        </button>
      </header>

      <div className={styles.tags}>
        <span className={styles.tagDirection}>
          {match?.direction.title ?? `Направление ${request.direction}`}
        </span>
        <span className={styles.tagService}>
          {match?.service.label ?? `Услуга ${request.activity}`}
        </span>
      </div>

      <p className={styles.comment}>{request.comment}</p>

      <dl className={styles.details}>
        <div className={styles.detail}>
          <dt className={styles.term}>Имя</dt>
          <dd className={styles.value}>{request.name}</dd>
        </div>

        <div className={styles.detail}>
          <dt className={styles.term}>Телефон</dt>
          <dd className={styles.value}>
            <a className={styles.link} href={`tel:${request.telephone}`}>
              {request.telephone}
            </a>
          </dd>
        </div>

        <div className={styles.detail}>
          <dt className={styles.term}>Email</dt>
          <dd className={styles.value}>
            <a className={styles.link} href={`mailto:${request.email}`}>
              {request.email}
            </a>
          </dd>
        </div>

        <div className={styles.detail}>
          <dt className={styles.term}>Организация</dt>
          <dd className={styles.value}>{request.company_name || "—"}</dd>
        </div>

        <div className={styles.detail}>
          <dt className={styles.term}>ИНН</dt>
          <dd className={styles.value}>{request.inn || "—"}</dd>
        </div>
      </dl>
    </article>
  );
};

export default RequestCard;
