"use client";

import classNames from "classnames";
import {
  areaTitle,
  objectLabel,
  objectTitle,
  type ExpertCatalog,
} from "@/entities/expert";
import {
  AUDIT_CHECKLIST_SIZE,
  CONTRACT_KIND_LABELS,
  CUSTOMER_TYPE_LABELS,
  DEADLINE_LABELS,
  EXPERTISE_RESULT_LABELS,
  EXPERTISE_STATUS_TONES,
  SERVICE_LABELS,
  auditDocumentsReportUrl,
  isAudit,
  statusLabel,
  wordingFor,
  type Expertise,
} from "@/entities/expertise";
import { formatRequestDate } from "@/entities/request";
import { formatRub } from "@/shared/lib/money";
import { DetailsRow, DetailsTable } from "@/shared/ui/details-table";
import AuditRows from "../audit-rows";
import ExpertiseActions from "../expertise-actions";
import ExpertiseProgress from "../expertise-progress";
import FilesList from "../files-list";
import RemarksThread from "../remarks-thread";
import styles from "./style.module.scss";

const executorTitle = (expertise: Expertise, executor: string): string | null => {
  if (expertise.expert_name) return expertise.expert_name;
  if (expertise.expert_id === null) return null;

  return `${executor} НПИ «Недра»`;
};

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

  const audit = isAudit(expertise);
  const words = wordingFor(expertise);

  const documentation = documents.filter(
    (item) => item.kind === "documentation" || item.kind === "audit_item",
  );
  const coveredItems = new Set(documentation.map((item) => item.item_number)).size;
  const revisions = documents.filter(
    (item) => item.kind === "revision" && !shownInRemarks.has(item.id),
  );
  const conclusion = documents.filter((item) => item.kind === "conclusion");
  const contract = documents.filter((item) => item.kind === "contract" || item.kind === "nda");
  const company = expertise.company;
  const individual = expertise.individual;
  const executorName = executorTitle(expertise, words.executor);

  return (
    <article className={styles.card}>
      <div className={styles.head}>
        <span className={styles.badge}>
          {audit && SERVICE_LABELS.audit}
          {!audit && (expertise.object_code ? objectLabel(catalog, expertise.object_code) : "—")}
        </span>
        <div className={styles.heading}>
          <h3 className={styles.title}>
            {audit && words.title}
            {!audit &&
              (expertise.object_code
                ? objectTitle(catalog, expertise.object_code)
                : "Объект определит эксперт")}
          </h3>
          <p className={styles.meta}>
            Заявка №{expertise.id} · {formatRequestDate(expertise.created_at)}
          </p>
        </div>
        <span className={classNames(styles.status, styles[EXPERTISE_STATUS_TONES[expertise.status]])}>
          {statusLabel(expertise)}
        </span>
      </div>

      <ExpertiseProgress expertise={expertise} />

      <DetailsTable>
        {expertise.object_name && (
          <DetailsRow label={audit ? "Объект аудита" : "Документация"}>
            {expertise.object_name}
          </DetailsRow>
        )}
        {!audit && (
          <DetailsRow label="Вид договора">
            {expertise.contract_kind
              ? CONTRACT_KIND_LABELS[expertise.contract_kind]
              : "Определит эксперт"}
          </DetailsRow>
        )}
        <DetailsRow label={CUSTOMER_TYPE_LABELS[expertise.customer_type]}>
          {company && `${company.name}, ИНН ${company.inn} · оплата по счёту`}
          {individual && `${individual.full_name} · оплата картой`}
        </DetailsRow>
        {audit && <AuditRows expertise={expertise} />}
        {!audit && (
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
        )}
        {expertise.hazard_class !== null && (
          <DetailsRow label="Класс опасности ОПО">{expertise.hazard_class}</DetailsRow>
        )}
        {expertise.expert_category !== null && (
          <DetailsRow label="Категория эксперта">{expertise.expert_category}</DetailsRow>
        )}
        {expertise.deadline && (
          <DetailsRow label="Желаемый срок">{DEADLINE_LABELS[expertise.deadline]}</DetailsRow>
        )}
        <DetailsRow label="Цена заказчика">{formatRub(expertise.price)}</DetailsRow>
        {role === "expert" && <DetailsRow label="Заказчик">{expertise.customer_name}</DetailsRow>}
        {role === "customer" && executorName && expertise.team.length === 0 && (
          <DetailsRow label={words.executor}>{executorName}</DetailsRow>
        )}
        {expertise.comment && (
          <DetailsRow label="Комментарий">
            <span className={styles.comment}>{expertise.comment}</span>
          </DetailsRow>
        )}
        {contract.length > 0 && (
          <DetailsRow label="Договор">
            <FilesList expertiseId={expertise.id} documents={contract} />
          </DetailsRow>
        )}
        <DetailsRow label={audit ? "Документы по перечню" : "Файлы документации"}>
          {audit && (
            <p className={styles.coverage}>
              Загружены документы по {coveredItems} из {AUDIT_CHECKLIST_SIZE} пунктов перечня
            </p>
          )}
          <FilesList expertiseId={expertise.id} documents={documentation} />
          {audit && role === "expert" && (
            <a
              className={styles.report}
              href={auditDocumentsReportUrl(expertise.id)}
              target="_blank"
              rel="noreferrer"
            >
              Отчёт о представленных документах, Word
            </a>
          )}
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
          <DetailsRow label={words.result}>
            <FilesList expertiseId={expertise.id} documents={conclusion} />
          </DetailsRow>
        )}
      </DetailsTable>

      {remarks.length > 0 && (
        <RemarksThread expertiseId={expertise.id} remarks={remarks} audit={audit} />
      )}

      <ExpertiseActions expertise={expertise} role={role} onChange={onChange} />
    </article>
  );
};

export default ExpertiseCard;
