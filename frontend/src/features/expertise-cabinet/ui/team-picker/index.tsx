"use client";

import { useState } from "react";
import type { AuditTeamMember } from "@/entities/expertise";
import Button from "@/shared/ui/button";
import Checkbox from "@/shared/ui/checkbox";
import { useAuditors } from "../../model/use-auditors";
import styles from "./style.module.scss";

type TeamPickerProps = {
  team: AuditTeamMember[];
  pending: boolean;
  onSave: (userIds: number[]) => void;
};

const TeamPicker = ({ team, pending, onSave }: TeamPickerProps) => {
  const { auditors, error } = useAuditors();
  const [selected, setSelected] = useState<number[]>(
    team.filter((member) => !member.lead).map((member) => member.user_id),
  );

  const toggle = (userId: number) =>
    setSelected(
      selected.includes(userId) ? selected.filter((id) => id !== userId) : [...selected, userId],
    );

  return (
    <div className={styles.form}>
      <p className={styles.title}>Аудиторская группа</p>
      <p className={styles.note}>
        Вы руководитель группы. Отметьте аудиторов, которые будут работать с вами: их ФИО
        и области аттестации войдут в План аудита.
      </p>

      {error && <p className={styles.error}>{error}</p>}
      {!error && auditors.length === 0 && (
        <p className={styles.note}>Других аудиторов пока нет — можно провести аудит одному.</p>
      )}

      <div className={styles.list}>
        {auditors.map((auditor) => (
          <Checkbox
            key={auditor.user_id}
            checked={selected.includes(auditor.user_id)}
            onChange={() => toggle(auditor.user_id)}
          >
            {auditor.full_name}
            {auditor.areas.length > 0 && (
              <span className={styles.areas}> · {auditor.areas.join(", ")}</span>
            )}
          </Checkbox>
        ))}
      </div>

      <Button className={styles.save} loading={pending} onClick={() => onSave(selected)}>
        Сохранить группу
      </Button>
    </div>
  );
};

export default TeamPicker;
