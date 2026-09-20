"use client";

import {
  areaTitle,
  objectLabel,
  objectTitle,
  type ExpertCatalog,
} from "@/entities/expert";
import {
  EXPERTISE_RESULT_LABELS,
  EXPERTISE_STATUS_LABELS,
  EXPERTISE_STATUS_TONES,
  expertiseDocumentUrl,
  type Expertise,
  type ExpertiseDocument,
} from "@/entities/expertise";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";
import { DocumentIcon } from "@/shared/ui/icons";
import ExpertiseActions from "../expertise-actions";
import ExpertiseProgress from "../expertise-progress";
import styles from "./style.module.scss";

type ExpertiseCardProps = {
  expertise: Expertise;
  catalog: ExpertCatalog;
  role: "customer" | "expert";
  onChange: (item: Expertise) => void;
};

type FilesListProps = {
  expertiseId: number;
  documents: ExpertiseDocument[];
};

const FilesList = ({ expertiseId, documents }: FilesListProps) => (
  <ul className={styles.files}>
    {documents.map((document) => (
      <li key={document.id}>
        <a
          className={styles.file}
          href={expertiseDocumentUrl(expertiseId, document.id)}
          target="_blank"
          rel="noreferrer"
          title={document.original_name}
        >
          <span className={styles.fileTile}>
            <DocumentIcon className={styles.fileIcon} />
          </span>
          <span className={styles.fileName}>{document.original_name}</span>
        </a>
      </li>
    ))}
  </ul>
);

type MessageProps = {
  expertiseId: number;
  author: "Эксперт" | "Заказчик";
  date: string;
  text: string | null;
  documents: ExpertiseDocument[];
};

const Message = ({ expertiseId, author, date, text, documents }: MessageProps) => {
  const tone = author === "Эксперт" ? styles.fromExpert : styles.fromCustomer;
  const fallback = documents.length === 0 ? "Исправленная документация отправлена повторно" : null;

  return (
    <div className={styles.message}>
      <span className={`${styles.avatar} ${tone}`} aria-hidden="true">
        {author[0]}
      </span>

      <div className={styles.messageBody}>
        <p className={styles.messageMeta}>
          <span className={styles.author}>{author}</span> · {formatRequestDate(date)}
        </p>
        {(text ?? fallback) && <p className={styles.messageText}>{text ?? fallback}</p>}
        {documents.length > 0 && <FilesList expertiseId={expertiseId} documents={documents} />}
      </div>
    </div>
  );
};

const ExpertiseCard = ({ expertise, catalog, role, onChange }: ExpertiseCardProps) => {
  const documents = expertise.documents ?? [];
  const remarks = expertise.remarks ?? [];

  const shownInRemarks = new Set(remarks.flatMap((remark) => remark.documents.map((item) => item.id)));

  const documentation = documents.filter((item) => item.kind === "documentation");
  const revisions = documents.filter(
    (item) => item.kind === "revision" && !shownInRemarks.has(item.id),
  );
  const conclusion = documents.filter((item) => item.kind === "conclusion");

  const lastRemark = remarks[remarks.length - 1];
  const remarksResolved = lastRemark !== undefined && lastRemark.resolved_at !== null;

  return (
    <article className={styles.card}>
      <div className={styles.head}>
        <span className={styles.badge}>{objectLabel(catalog, expertise.object_code)}</span>
        <div className={styles.heading}>
          <h3 className={styles.title}>{objectTitle(catalog, expertise.object_code)}</h3>
          <p className={styles.meta}>
            Заявка №{expertise.id} · {formatRequestDate(expertise.created_at)}
          </p>
        </div>
        <span className={`${styles.status} ${styles[EXPERTISE_STATUS_TONES[expertise.status]]}`}>
          {EXPERTISE_STATUS_LABELS[expertise.status]}
        </span>
      </div>

      <ExpertiseProgress status={expertise.status} />

      <DetailsTable>
        <DetailsRow label="Область аттестации">
          <span className={styles.code}>{expertise.area_code}</span>
          {areaTitle(catalog, expertise.area_code)}
        </DetailsRow>
        {expertise.hazard_class !== null && (
          <DetailsRow label="Класс опасности ОПО">{expertise.hazard_class}</DetailsRow>
        )}
        <DetailsRow label="Категория эксперта">{expertise.expert_category}</DetailsRow>
        <DetailsRow label="Стоимость">{formatRub(expertise.price)}</DetailsRow>
        {role === "expert" && <DetailsRow label="Заказчик">{expertise.customer_name}</DetailsRow>}
        {role === "customer" && expertise.expert_name && (
          <DetailsRow label="Эксперт">{expertise.expert_name}</DetailsRow>
        )}
        {expertise.comment && (
          <DetailsRow label="Комментарий">
            <span className={styles.comment}>{expertise.comment}</span>
          </DetailsRow>
        )}
        <DetailsRow label="Документация">
          <FilesList expertiseId={expertise.id} documents={documentation} />
        </DetailsRow>
        {revisions.length > 0 && (
          <DetailsRow label="Исправленная документация">
            <FilesList expertiseId={expertise.id} documents={revisions} />
          </DetailsRow>
        )}
        {expertise.result && (
          <DetailsRow label="Результат">{EXPERTISE_RESULT_LABELS[expertise.result]}</DetailsRow>
        )}
        {conclusion.length > 0 && (
          <DetailsRow label="Заключение">
            <FilesList expertiseId={expertise.id} documents={conclusion} />
          </DetailsRow>
        )}
      </DetailsTable>

      {remarks.length > 0 && (
        <section className={styles.remarks}>
          <header className={styles.remarksHead}>
            <h4 className={styles.remarksTitle}>
              Рекомендации по приведению объекта экспертизы в соответствие с требованиями
              промышленной безопасности
            </h4>
            <span className={remarksResolved ? styles.remarksDone : styles.remarksWait}>
              {remarksResolved ? "Исправления отправлены" : "Ждём исправления"}
            </span>
          </header>

          <ol className={styles.thread}>
            {remarks.map((remark) => (
              <li key={remark.id} className={styles.round}>
                <Message
                  expertiseId={expertise.id}
                  author="Эксперт"
                  date={remark.created_at}
                  text={remark.text}
                  documents={remark.documents.filter((item) => item.kind === "remarks")}
                />
                {remark.resolved_at && (
                  <Message
                    expertiseId={expertise.id}
                    author="Заказчик"
                    date={remark.resolved_at}
                    text={remark.response_text}
                    documents={remark.documents.filter((item) => item.kind === "revision")}
                  />
                )}
              </li>
            ))}
          </ol>
        </section>
      )}

      <ExpertiseActions expertise={expertise} role={role} onChange={onChange} />
    </article>
  );
};

export default ExpertiseCard;
