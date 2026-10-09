import type { Expertise, ExpertiseResult } from "./types";
import { isAudit, wordingFor, type ServiceWording } from "./wording";

export type StageState = "done" | "current" | "future";

export type ExpertiseStage = {
  key: string;
  label: string;
  startedAt: string | null;
  endedAt: string | null;
  state: StageState;
};

type StageRow = {
  key: string;
  label: string;
  startedAt: string | null;
};

const sentLabel = (words: ServiceWording, result: ExpertiseResult | null): string => {
  if (result === "positive") return `${words.resultSent}: положительное`;
  if (result === "negative") return `${words.resultSent}: отрицательное`;

  return words.resultSent;
};

const auditPlanRows = (expertise: Expertise): StageRow[] => [
  { key: "plan_sent", label: "План аудита отправлен", startedAt: expertise.plan_sent_at },
  { key: "plan_approved", label: "План аудита согласован", startedAt: expertise.plan_approved_at },
];

const collectRows = (expertise: Expertise): StageRow[] => {
  const words = wordingFor(expertise);
  const audit = isAudit(expertise);

  const rows: StageRow[] = [
    { key: "new", label: "Заявка подана", startedAt: expertise.created_at },
    {
      key: "expert_ready",
      label: `${words.executor} готов провести ${words.work}`,
      startedAt: expertise.expert_ready_at,
    },
    { key: "contract", label: "Договор заключён", startedAt: expertise.contract_at },
    {
      key: "advance",
      label: audit
        ? "Аванс оплачен, готовится План аудита"
        : `Аванс оплачен, ${words.executorLower} в работе`,
      startedAt: expertise.advance_paid_at,
    },
  ];

  if (audit) rows.push(...auditPlanRows(expertise));

  for (const remark of expertise.remarks ?? []) {
    rows.push({
      key: `remarks-${remark.id}`,
      label: words.remarksStage,
      startedAt: remark.created_at,
    });
    rows.push({
      key: `revision-${remark.id}`,
      label: words.revisionStage,
      startedAt: remark.resolved_at,
    });
  }

  rows.push({ key: "conclusion", label: words.resultReady, startedAt: expertise.conclusion_ready_at });
  rows.push({ key: "paid", label: "Остаток оплачен", startedAt: expertise.final_paid_at });
  rows.push({ key: "sent", label: sentLabel(words, expertise.result), startedAt: expertise.sent_at });
  rows.push({ key: "accepted", label: "Работа принята", startedAt: expertise.accepted_at });

  return rows;
};

const lastReachedIndex = (rows: StageRow[]): number => {
  let reached = -1;

  rows.forEach((row, index) => {
    if (row.startedAt !== null) reached = index;
  });

  return reached;
};

const nextStart = (rows: StageRow[], index: number): string | null => {
  for (let position = index + 1; position < rows.length; position += 1) {
    const start = rows[position].startedAt;
    if (start !== null) return start;
  }

  return null;
};

const stageState = (index: number, reached: number, last: number): StageState => {
  if (index < reached) return "done";
  if (index === reached) return index === last ? "done" : "current";

  return "future";
};

export const buildStages = (expertise: Expertise): ExpertiseStage[] => {
  const rows = collectRows(expertise);
  const reached = lastReachedIndex(rows);

  return rows.map((row, index) => ({
    key: row.key,
    label: row.label,
    startedAt: row.startedAt,
    endedAt: nextStart(rows, index),
    state: stageState(index, reached, rows.length - 1),
  }));
};

export const currentStage = (stages: ExpertiseStage[]): ExpertiseStage | null => {
  const reached = stages.filter((stage) => stage.state !== "future");

  return reached.length > 0 ? reached[reached.length - 1] : null;
};

export const doneCount = (stages: ExpertiseStage[]): number =>
  stages.filter((stage) => stage.state !== "future").length;
