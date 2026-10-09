import { AUDIT_FILES_ACCEPT } from "@/entities/expertise";
import { keepDigits } from "@/shared/lib/text";
import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import type { AuditBlockProps } from "../../model/audit-form";
import ChipOptions from "../chip-options";
import { YES_NO_OPTIONS, toAnswer } from "./inputs";
import styles from "./style.module.scss";

const FleetFields = ({ form, errors, onChange }: AuditBlockProps) => (
  <>
    <div className={styles.fields}>
      <TextField
        label="Общее количество ОПО"
        required
        inputMode="numeric"
        placeholder="Например, 12"
        maxLength={5}
        invalid={Boolean(errors.fleetCount)}
        value={form.fleetCount}
        onChange={(value) => onChange({ ...form, fleetCount: keepDigits(value) })}
      />
      <TextField
        label="Основной отраслевой профиль"
        required
        placeholder="Угольная промышленность"
        maxLength={500}
        invalid={Boolean(errors.fleetProfile)}
        value={form.fleetProfile}
        onChange={(value) => onChange({ ...form, fleetProfile: value })}
      />
    </div>

    <div className={styles.question}>
      <span className={styles.questionLabel}>Наличие ОПО в разных субъектах РФ</span>
      <ChipOptions
        label="Наличие ОПО в разных субъектах РФ"
        options={YES_NO_OPTIONS}
        value={toAnswer(form.multiRegion)}
        layout="row"
        invalid={Boolean(errors.multiRegion)}
        onChange={(answer) => onChange({ ...form, multiRegion: answer === "yes" })}
      />
    </div>

    <FilesField
      label="Свидетельство о регистрации ОПО"
      files={form.certificate ? [form.certificate] : []}
      accept={AUDIT_FILES_ACCEPT}
      onAdd={(files) => onChange({ ...form, certificate: files[0] })}
      onRemove={() => onChange({ ...form, certificate: null })}
    />
  </>
);

export default FleetFields;
