import { formatDateTime, formatShortDate } from "@/shared/lib/date";
import { DetailsRow } from "@/shared/ui/details-table";
import type { AuditPlan, AuditTeamMember } from "../../model/audit";
import styles from "./style.module.scss";

type PlanSummaryProps = {
  plan: AuditPlan | null;
  team: AuditTeamMember[];
};

const period = (start: string | null, end: string | null): string =>
  `${formatShortDate(start)} — ${formatShortDate(end)}`;

const memberRole = (member: AuditTeamMember): string => {
  const role = member.lead ? "руководитель группы" : "аудитор";
  const areas = member.areas.length > 0 ? `, области аттестации: ${member.areas.join(", ")}` : "";

  return ` — ${role}${areas}`;
};

const TeamRow = ({ team }: { team: AuditTeamMember[] }) => (
  <DetailsRow label="Аудиторская группа">
    <ul className={styles.list}>
      {team.map((member) => (
        <li key={member.user_id}>
          <span className={styles.strong}>{member.full_name}</span>
          {memberRole(member)}
        </li>
      ))}
    </ul>
  </DetailsRow>
);

const PlanRow = ({ plan }: { plan: AuditPlan }) => (
  <DetailsRow label={`План аудита, версия ${plan.version}`}>
    <span className={styles.lines}>
      <span>Документарный этап: {period(plan.documents_start, plan.documents_end)}</span>
      {plan.onsite_start && <span>Выездной этап: {period(plan.onsite_start, plan.onsite_end)}</span>}
      {plan.meetings ? (
        <>
          <span>Вступительное совещание: {formatDateTime(plan.opening_at)}</span>
          <span>Заключительное совещание: {formatDateTime(plan.closing_at)}</span>
        </>
      ) : (
        <span>Аудит без совещаний</span>
      )}
      {plan.meeting_link && <span>Ссылка на видеосвязь: {plan.meeting_link}</span>}
      {plan.workshops && <span>Цеха и участки: {plan.workshops}</span>}
      <span>Лица для интервью: {plan.interviewees}</span>
    </span>
  </DetailsRow>
);

const PlanSummary = ({ plan, team }: PlanSummaryProps) => (
  <>
    {team.length > 0 && <TeamRow team={team} />}
    {plan && <PlanRow plan={plan} />}
  </>
);

export default PlanSummary;
