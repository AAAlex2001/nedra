import classNames from "classnames";
import { AUDIT_STAGE_LABELS, AUDIT_STAGES, type AuditStage } from "@/entities/expertise";
import Checkbox from "@/shared/ui/checkbox";
import type { AuditBlockProps } from "../../model/audit-form";
import FieldGroup from "../field-group";
import styles from "./style.module.scss";

const StagesBlock = ({ form, errors, onChange }: AuditBlockProps) => {
  const { stages } = form;
  const allChosen = stages.length === AUDIT_STAGES.length;

  const toggleStage = (stage: AuditStage) => {
    const next = stages.includes(stage)
      ? stages.filter((item) => item !== stage)
      : [...stages, stage];

    onChange({ ...form, stages: next });
  };

  const toggleAll = () => onChange({ ...form, stages: allChosen ? [] : AUDIT_STAGES });

  return (
    <FieldGroup label="Этапы аудита">
      <p className={styles.lead}>
        Выберите необходимые этапы проведения аудита (на основании п. 15 Руководства по
        безопасности, утв. приказом Ростехнадзора от 12.09.2025 № 318):
      </p>

      <div className={classNames(styles.checks, errors.stages && styles.checksInvalid)}>
        {AUDIT_STAGES.map((stage) => (
          <Checkbox
            key={stage}
            checked={stages.includes(stage)}
            onChange={() => toggleStage(stage)}
          >
            {AUDIT_STAGE_LABELS[stage]}
          </Checkbox>
        ))}

        <Checkbox checked={allChosen} onChange={toggleAll}>
          Все этапы комплексно (рекомендуется для базового/полного аудита СУПБ)
        </Checkbox>
      </div>
    </FieldGroup>
  );
};

export default StagesBlock;
