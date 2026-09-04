import styles from "./style.module.scss";

type TextFieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: "text" | "tel" | "email";
  required?: boolean;
  maxLength?: number;
  inputMode?: "text" | "numeric" | "tel" | "email";
  multiline?: boolean;
  rows?: number;
};

const TextField = ({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  required,
  maxLength,
  inputMode,
  multiline,
  rows = 4,
}: TextFieldProps) => (
  <label className={styles.field}>
    <span className={styles.label}>
      {label}
      {required && <span className={styles.required}> *</span>}
    </span>

    {multiline ? (
      <textarea
        className={styles.textarea}
        rows={rows}
        placeholder={placeholder}
        value={value}
        required={required}
        maxLength={maxLength}
        onChange={(event) => onChange(event.target.value)}
      />
    ) : (
      <input
        className={styles.input}
        type={type}
        inputMode={inputMode}
        placeholder={placeholder}
        value={value}
        required={required}
        maxLength={maxLength}
        onChange={(event) => onChange(event.target.value)}
      />
    )}
  </label>
);

export default TextField;
