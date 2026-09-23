"use client";

import {
  areaTitle,
  objectLabel,
  objectTitle,
  type ExpertCatalog,
} from "@/entities/expert";
import {
  DEADLINE_LABELS,
  EXPERTISE_RESULT_LABELS,
  EXPERTISE_STATUS_LABELS,
  EXPERTISE_STATUS_TONES,
  type Expertise,
} from "@/entities/expertise";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";
import ExpertiseActions from "../expertise-actions";
import ExpertiseProgress from "../expertise-progress";
import FilesList from "../files-list";
import RemarksThread from "../remarks-thread";
import styles from "./style.module.scss";

type ExpertiseCardProps = {
  expertise: Expertise;
  catalog: ExpertCatalog;
  role: "customer" | "expert";
  onChange: (item: Expertise) => void;
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

  return (
    <article className={styles.card}>
      <div className={styles.head}>
        <span className={styles.badge}>
          {expertise.object_code ? objectLabel(catalog, expertise.object_code) : "—"}
        </span>
        <div className={styles.heading}>
          <h3 className={styles.title}>
            {expertise.object_code
              ? objectTitle(catalog, expertise.object_code)
              : "Объект определит эксперт"}
          </h3>
          <p className={styles.meta}>
            Заявка №{expertise.id} · {formatRequestDate(expertise.created_at)}
          </p>
        </div>
        <span className={`${styles.status} ${styles[EXPERTISE_STATUS_TONES[expertise.status]]}`}>
          {EXPERTISE_STATUS_LABELS[expertise.status]}
        </span>
      </div>

      <ExpertiseProgress expertise={expertise} />

      <DetailsTable>
        <DetailsRow label="Область аттестации">
          {expertise.area_code ? (
            <>
              <span className={styles.code}>{expertise.area_code}</span>
              {areaTitle(catalog, expertise.area_code)}
            </>
          ) : (
            "Определит эксперт"
          )}
        </DetailsRow>
        {expertise.hazard_class !== null && (
          <DetailsRow label="Класс опасности ОПО">{expertise.hazard_class}</DetailsRow>
        )}
        {expertise.expert_category !== null && (
          <DetailsRow label="Категория эксперта">{expertise.expert_category}</DetailsRow>
        )}
        {expertise.deadline && (
          <DetailsRow label="Желаемый срок">{DEADLINE_LABELS[expertise.deadline]}</DetailsRow>
        )}
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

      {remarks.length > 0 && <RemarksThread expertiseId={expertise.id} remarks={remarks} />}

      <ExpertiseActions expertise={expertise} role={role} onChange={onChange} />
    </article>
  );
};

export default ExpertiseCard;
