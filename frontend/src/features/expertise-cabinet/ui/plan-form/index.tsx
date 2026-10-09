"use client";

import { useState } from "react";
import type { AuditPlanInput, Expertise } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import Checkbox from "@/shared/ui/checkbox";
import TextField from "@/shared/ui/text-field";
import {
  hasOnsite,
  initialPlanFields,
  planProblem,
  toPlanInput,
  type PlanFields,
} from "../../model/plan-fields";
import styles from "./style.module.scss";

type PlanFormProps = {
  expertise: Expertise;
  pending: boolean;
  onSubmit: (plan: AuditPlanInput) => void;
};

const PlanForm = ({ expertise, pending, onSubmit }: PlanFormProps) => {
  const [fields, setFields] = useState<PlanFields>(() => initialPlanFields(expertise));
  const onsite = hasOnsite(expertise);
  const problem = planProblem(fields, onsite);

  const toggleMeetings = (withoutMeetings: boolean) =>
    setFields({ ...fields, meetings: !withoutMeetings });

  return (
    <div className={styles.form}>
      <p className={styles.title}>Программа аудита СУПБ</p>
      <p className={styles.hint}>
        Цели и критерии аудита стоят в Программе по шаблону института. Укажите график и ресурсы.
      </p>

      <span className={styles.label}>Документарный этап</span>
      <div className={styles.row}>
        <TextField
          label="С"
          type="date"
          value={fields.documentsStart}
          onChange={(value) => setFields({ ...fields, documentsStart: value })}
        />
        <TextField
          label="По"
          type="date"
          min={fields.documentsStart || undefined}
          value={fields.documentsEnd}
          onChange={(value) => setFields({ ...fields, documentsEnd: value })}
        />
      </div>

      {onsite && (
        <>
          <span className={styles.label}>Выездной этап</span>
          <div className={styles.row}>
            <TextField
              label="С"
              type="date"
              value={fields.onsiteStart}
              onChange={(value) => setFields({ ...fields, onsiteStart: value })}
            />
            <TextField
              label="По"
              type="date"
              min={fields.onsiteStart || undefined}
              value={fields.onsiteEnd}
              onChange={(value) => setFields({ ...fields, onsiteEnd: value })}
            />
          </div>
          <TextField
            label="Доступ к цехам и участкам"
            multiline
            rows={2}
            maxLength={2000}
            placeholder="Котельная, участок газопотребления, склад ГСМ"
            value={fields.workshops}
            onChange={(value) => setFields({ ...fields, workshops: value })}
          />
        </>
      )}

      <Checkbox checked={!fields.meetings} onChange={toggleMeetings}>
        Провести аудит без вступительного и заключительного совещаний
      </Checkbox>

      {fields.meetings && (
        <div className={styles.row}>
          <TextField
            label="Вступительное совещание"
            type="datetime-local"
            value={fields.openingAt}
            onChange={(value) => setFields({ ...fields, openingAt: value })}
          />
          <TextField
            label="Заключительное совещание"
            type="datetime-local"
            value={fields.closingAt}
            onChange={(value) => setFields({ ...fields, closingAt: value })}
          />
        </div>
      )}

      <TextField
        label="Ссылка на видеосвязь"
        placeholder="Если совещания проходят онлайн"
        maxLength={500}
        value={fields.meetingLink}
        onChange={(value) => setFields({ ...fields, meetingLink: value })}
      />
      <TextField
        label="Должностные лица для интервью"
        multiline
        rows={2}
        maxLength={2000}
        placeholder="Главный инженер, специалист по промышленной безопасности, начальник участка"
        value={fields.interviewees}
        onChange={(value) => setFields({ ...fields, interviewees: value })}
      />

      {problem && <p className={styles.hint}>{problem}</p>}

      <Button
        className={styles.submit}
        disabled={problem !== null}
        loading={pending}
        onClick={() => onSubmit(toPlanInput(fields, onsite))}
      >
        Отправить План заказчику
      </Button>
    </div>
  );
};

export default PlanForm;
