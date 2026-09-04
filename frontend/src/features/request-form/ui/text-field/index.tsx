import styles from "./style.module.scss";

type TextFieldProps = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: "text" | "tel" | "email";
  required?: boolean;
  error?: string;
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
  error,
  maxLength,
  inputMode,
  multiline,
  rows = 4,
}: TextFieldProps) => {
  const controlClass = `${multiline ? styles.textarea : styles.input} ${
    error ? styles.invalid : ""
  }`;

  return (
    <label className={styles.field}>
      <span className={styles.label}>
        {label}
        {required && <span className={styles.required}> *</span>}
      </span>

      {multiline ? (
        <textarea
          className={controlClass}
          rows={rows}
          placeholder={placeholder}
          value={value}
          maxLength={maxLength}
          onChange={(event) => onChange(event.target.value)}
        />
      ) : (
        <input
          className={controlClass}
          type={type}
          inputMode={inputMode}
          placeholder={placeholder}
          value={value}
          maxLength={maxLength}
          onChange={(event) => onChange(event.target.value)}
        />
      )}

      {error && <span className={styles.error}>{error}</span>}
    </label>
  );
};

export default TextField;
