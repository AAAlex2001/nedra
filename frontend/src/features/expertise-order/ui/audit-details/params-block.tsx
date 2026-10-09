import classNames from "classnames";
import { AUDIT_FILES_ACCEPT, type AuditElement, type AuditKind } from "@/entities/expertise";
import Checkbox from "@/shared/ui/checkbox";
import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import { needsSto, type AuditBlockProps } from "../../model/audit-form";
import ChipOptions from "../chip-options";
import FieldGroup from "../field-group";
import { ELEMENT_OPTIONS, KIND_OPTIONS, STO_OPTIONS, toAnswer } from "./inputs";
import styles from "./style.module.scss";

const ParamsBlock = ({ form, errors, onChange }: AuditBlockProps) => {
  const toggleElement = (element: AuditElement) => {
    const next = form.elements.includes(element)
      ? form.elements.filter((item) => item !== element)
      : [...form.elements, element];

    onChange({ ...form, elements: next });
  };

  return (
    <FieldGroup label="Параметры аудита">
      <span className={styles.questionLabel}>Тип запрашиваемого аудита</span>
      <ChipOptions
        label="Тип запрашиваемого аудита"
        options={KIND_OPTIONS}
        value={form.kind}
        layout="grid"
        invalid={Boolean(errors.kind)}
        onChange={(kind) => onChange({ ...form, kind: kind as AuditKind })}
      />

      {needsSto(form.kind) && (
        <>
          <span className={styles.questionLabel}>
            Учитывать внутренние стандарты организации (СТО)
          </span>
          <ChipOptions
            label="Учитывать внутренние стандарты организации"
            options={STO_OPTIONS}
            value={toAnswer(form.useSto)}
            layout="grid"
            invalid={Boolean(errors.useSto)}
            onChange={(answer) => onChange({ ...form, useSto: answer === "yes" })}
          />
        </>
      )}

      {needsSto(form.kind) && form.useSto && (
        <>
          <TextField
            label="Наименование и реквизиты СТО"
            required
            placeholder="СТО 01-2025 «Порядок проведения аудита СУПБ», утв. приказом от 10.01.2025 № 5"
            maxLength={1000}
            invalid={Boolean(errors.stoName)}
            value={form.stoName}
            onChange={(value) => onChange({ ...form, stoName: value })}
          />
          <FilesField
            label="Файл СТО"
            required
            files={form.stoFile ? [form.stoFile] : []}
            accept={AUDIT_FILES_ACCEPT}
            invalid={Boolean(errors.stoFile)}
            onAdd={(files) => onChange({ ...form, stoFile: files[0] })}
            onRemove={() => onChange({ ...form, stoFile: null })}
          />
        </>
      )}

      {form.kind === "selective" && (
        <>
          <p className={styles.lead}>Выберите направления для аудита на основе пункта 17 Приказа 318:</p>
          <div className={classNames(styles.checks, errors.elements && styles.checksInvalid)}>
            {ELEMENT_OPTIONS.map((option) => (
              <Checkbox
                key={option.value}
                checked={form.elements.includes(option.value)}
                onChange={() => toggleElement(option.value)}
              >
                {option.label}
              </Checkbox>
            ))}
          </div>
        </>
      )}
    </FieldGroup>
  );
};

export default ParamsBlock;
