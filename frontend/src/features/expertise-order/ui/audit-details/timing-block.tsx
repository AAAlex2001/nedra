import type { TimingKind } from "@/entities/expertise";
import SelectField from "@/shared/ui/select-field";
import TextField from "@/shared/ui/text-field";
import type { AuditBlockProps } from "../../model/audit-form";
import FieldGroup from "../field-group";
import { TIMING_OPTIONS } from "./inputs";
import styles from "./style.module.scss";

const TimingBlock = ({ form, errors, onChange }: AuditBlockProps) => (
  <FieldGroup label="Сроки">
    <SelectField
      label="Желаемые сроки проведения аудита"
      placeholder="Выберите срок"
      required
      options={TIMING_OPTIONS}
      invalid={Boolean(errors.timing)}
      value={form.timing}
      onChange={(value) => onChange({ ...form, timing: value as TimingKind })}
    />

    {form.timing === "custom" && (
      <div className={styles.fields}>
        <TextField
          label="С"
          required
          type="date"
          invalid={Boolean(errors.start)}
          value={form.start}
          onChange={(value) => onChange({ ...form, start: value })}
        />
        <TextField
          label="По"
          required
          type="date"
          min={form.start}
          invalid={Boolean(errors.end)}
          value={form.end}
          onChange={(value) => onChange({ ...form, end: value })}
        />
      </div>
    )}
  </FieldGroup>
);

export default TimingBlock;
