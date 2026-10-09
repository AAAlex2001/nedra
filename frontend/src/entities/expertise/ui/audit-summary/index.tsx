import { formatShortDate } from "@/shared/lib/date";
import { DetailsRow } from "@/shared/ui/details-table";
import {
  AUDIT_ELEMENT_LABELS,
  AUDIT_KIND_TITLES,
  AUDIT_SCOPE_LABELS,
  AUDIT_STAGE_TITLES,
  HAZARD_SIGN_LABELS,
  NEGOTIATION_LABELS,
  TIMING_LABELS,
  type AuditDetails,
  type AuditObject,
  type AuditTiming,
} from "../../model/audit";
import styles from "./style.module.scss";

type AuditSummaryProps = {
  details: AuditDetails;
};

const timingText = (timing: AuditTiming): string => {
  if (timing.kind !== "custom") return TIMING_LABELS[timing.kind];

  return `с ${formatShortDate(timing.start)} по ${formatShortDate(timing.end)}`;
};

const ObjectItem = ({ item }: { item: AuditObject }) => (
  <li className={styles.item}>
    <span className={styles.strong}>
      {item.name}, рег. № {item.reg_number}, {item.hazard_class} класс
    </span>
    <span>{item.address}</span>
    <span>Вид деятельности: {item.industry}</span>
    <span>
      Признаки опасности: {item.hazard_signs.map((sign) => HAZARD_SIGN_LABELS[sign]).join("; ")}
    </span>
  </li>
);

const AuditSummary = ({ details }: AuditSummaryProps) => {
  const { applicant, params, budget, fleet } = details;

  return (
    <>
      <DetailsRow label="Заявитель">
        <span className={styles.lines}>
          <span className={styles.strong}>
            {applicant.full_name}, {applicant.position}
          </span>
          <span>
            {applicant.organization}, ИНН {applicant.inn}
          </span>
          <span>
            {applicant.phone} · {applicant.email}
          </span>
          <span>{applicant.by_proxy ? "Действует по доверенности" : "Руководитель организации"}</span>
        </span>
      </DetailsRow>

      <DetailsRow label="Масштаб аудита">{AUDIT_SCOPE_LABELS[details.scope]}</DetailsRow>

      <DetailsRow label={fleet ? "Все ОПО" : "ОПО"}>
        {fleet ? (
          <span className={styles.lines}>
            <span>Количество ОПО: {fleet.count}</span>
            <span>Основной отраслевой профиль: {fleet.profile}</span>
            <span>ОПО в разных субъектах РФ: {fleet.multi_region ? "да" : "нет"}</span>
          </span>
        ) : (
          <ul className={styles.list}>
            {details.objects.map((item) => (
              <ObjectItem key={`${item.reg_number}-${item.name}`} item={item} />
            ))}
          </ul>
        )}
      </DetailsRow>

      <DetailsRow label="Этапы аудита">
        {details.stages.map((stage) => AUDIT_STAGE_TITLES[stage]).join(", ")}
      </DetailsRow>

      <DetailsRow label="Тип аудита">
        <span className={styles.lines}>
          <span>{AUDIT_KIND_TITLES[params.kind]}</span>
          {params.use_sto === true && <span>Учитывать СТО: {params.sto_name}</span>}
          {params.use_sto === false && <span>Только требования законодательства</span>}
          {params.elements.length > 0 && (
            <ul className={styles.list}>
              {params.elements.map((element) => (
                <li key={element} className={styles.item}>
                  {AUDIT_ELEMENT_LABELS[element]}
                </li>
              ))}
            </ul>
          )}
        </span>
      </DetailsRow>

      <DetailsRow label="Сроки">{timingText(details.timing)}</DetailsRow>

      <DetailsRow label="Торг">
        {budget.mode === "none" && <span className={styles.block}>Бюджет не установлен</span>}
        {NEGOTIATION_LABELS[budget.negotiation]}
      </DetailsRow>
    </>
  );
};

export default AuditSummary;
