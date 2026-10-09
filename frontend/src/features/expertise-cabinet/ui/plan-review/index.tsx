"use client";

import classNames from "classnames";
import { useState } from "react";
import { expertiseDocumentUrl, type ExpertiseDocument } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import Checkbox from "@/shared/ui/checkbox";
import TextField from "@/shared/ui/text-field";
import styles from "./style.module.scss";

type PlanReviewProps = {
  expertiseId: number;
  plan: ExpertiseDocument | null;
  pending: boolean;
  onApprove: () => void;
  onRequestChanges: (comment: string) => void;
};

const PlanReview = ({ expertiseId, plan, pending, onApprove, onRequestChanges }: PlanReviewProps) => {
  const [agreed, setAgreed] = useState(false);
  const [changing, setChanging] = useState(false);
  const [comment, setComment] = useState("");

  return (
    <div className={styles.form}>
      {plan && (
        <a
          className={styles.document}
          href={expertiseDocumentUrl(expertiseId, plan.id)}
          target="_blank"
          rel="noreferrer"
        >
          {plan.original_name}
        </a>
      )}

      <Checkbox checked={agreed} onChange={setAgreed}>
        Я ознакомился с Планом аудита и согласую его. Нажатие кнопки «Согласовать» —
        юридически значимое действие
      </Checkbox>

      <div className={styles.buttons}>
        <button
          type="button"
          className={classNames(styles.secondary, changing && styles.secondaryActive)}
          disabled={pending}
          onClick={() => setChanging(!changing)}
        >
          Запросить корректировки
        </button>
        <Button disabled={!agreed} loading={pending} onClick={onApprove}>
          Согласовать
        </Button>
      </div>

      {changing && (
        <div className={styles.changes}>
          <TextField
            label="Что скорректировать"
            multiline
            rows={4}
            maxLength={4000}
            placeholder="Например: прошу перенести выездной этап на неделю позже из-за остановки производства"
            value={comment}
            onChange={setComment}
          />
          <Button
            disabled={comment.trim().length < 3}
            loading={pending}
            onClick={() => onRequestChanges(comment.trim())}
          >
            Отправить руководителю группы
          </Button>
        </div>
      )}
    </div>
  );
};

export default PlanReview;
