import { AUDIT_FILES_ACCEPT } from "@/entities/expertise";
import { keepDigits } from "@/shared/lib/text";
import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import type { AuditBlockProps } from "../../model/audit-form";
import FieldGroup from "../field-group";
import Segments from "../segments";
import { APPLICANT_INPUTS, PROXY_OPTIONS, type ApplicantField } from "./inputs";
import styles from "./style.module.scss";

const ApplicantBlock = ({ form, errors, onChange }: AuditBlockProps) => {
  const { applicant } = form;

  const changeField = (field: ApplicantField, value: string) =>
    onChange({ ...form, applicant: { ...applicant, [field]: value } });

  const changeProxy = (answer: string) =>
    onChange({ ...form, applicant: { ...applicant, by_proxy: answer === "yes" } });

  return (
    <FieldGroup label="Сведения о заявителе">
      <div className={styles.fields}>
        {APPLICANT_INPUTS.map((input) => (
          <TextField
            key={input.field}
            label={input.label}
            required
            type={input.type ?? "text"}
            inputMode={input.numeric ? "numeric" : undefined}
            placeholder={input.placeholder}
            maxLength={input.numeric ? 12 : 500}
            invalid={Boolean(errors[input.field])}
            value={applicant[input.field]}
            onChange={(value) => changeField(input.field, input.numeric ? keepDigits(value) : value)}
          />
        ))}
      </div>

      <div className={styles.question}>
        <span className={styles.questionLabel}>Полномочия заявителя</span>
        <Segments
          label="Полномочия заявителя"
          options={PROXY_OPTIONS}
          value={applicant.by_proxy ? "yes" : "no"}
          onChange={changeProxy}
        />
      </div>

      {applicant.by_proxy && (
        <FilesField
          label="Доверенность заявителя"
          required
          files={form.proxyFile ? [form.proxyFile] : []}
          accept={AUDIT_FILES_ACCEPT}
          invalid={Boolean(errors.proxyFile)}
          hint="Скан доверенности в PDF или файл с электронной подписью."
          onAdd={(files) => onChange({ ...form, proxyFile: files[0] })}
          onRemove={() => onChange({ ...form, proxyFile: null })}
        />
      )}
    </FieldGroup>
  );
};

export default ApplicantBlock;
