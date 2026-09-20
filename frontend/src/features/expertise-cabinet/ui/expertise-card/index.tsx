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

const ExpertiseCard = ({ expertise, catalog, role, onChange }: ExpertiseCardProps) => {
  const documents = expertise.documents ?? [];
  const remarks = expertise.remarks ?? [];

  const shownInRemarks = new Set(remarks.flatMap((remark) => remark.documents.map((item) => item.id)));

  const documentation = documents.filter((item) => item.kind === "documentation");
  const revisions = documents.filter(
    (item) => item.kind === "revision" && !shownInRemarks.has(item.id),
  );
  const conclusion = documents.filter((item) => item.kind === "conclusion");

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
        <span className={styles.status}>{EXPERTISE_STATUS_LABELS[expertise.status]}</span>
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
        <div className={styles.remarks}>
          <p className={styles.remarksTitle}>
            Рекомендации по приведению объекта экспертизы в соответствие с требованиями
            промышленной безопасности
          </p>

          {remarks.map((remark) => {
            const remarkFiles = remark.documents.filter((item) => item.kind === "remarks");
            const revisionFiles = remark.documents.filter((item) => item.kind === "revision");

            return (
              <div key={remark.id} className={styles.remark}>
                <p className={styles.remarkDate}>{formatRequestDate(remark.created_at)}</p>
                {remark.text && <p className={styles.remarkText}>{remark.text}</p>}
                {remarkFiles.length > 0 && (
                  <FilesList expertiseId={expertise.id} documents={remarkFiles} />
                )}

                {remark.resolved_at && (
                  <div className={styles.remarkResponse}>
                    <p className={styles.remarkResponseLabel}>
                      Ответ заказчика · {formatRequestDate(remark.resolved_at)}
                    </p>
                    {remark.response_text && (
                      <p className={styles.remarkText}>{remark.response_text}</p>
                    )}
                    {revisionFiles.length > 0 && (
                      <FilesList expertiseId={expertise.id} documents={revisionFiles} />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      <ExpertiseActions expertise={expertise} role={role} onChange={onChange} />
    </article>
  );
};

export default ExpertiseCard;
