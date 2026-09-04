import styles from "./style.module.scss";

export type SelectFieldOption = {
  value: string;
  label: string;
};

type SelectFieldProps = {
  label: string;
  placeholder: string;
  options: SelectFieldOption[];
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
};

const SelectField = ({
  label,
  placeholder,
  options,
  value,
  onChange,
  required,
}: SelectFieldProps) => (
  <label className={styles.field}>
    <span className={styles.label}>
      {label}
      {required && <span className={styles.required}> *</span>}
    </span>

    <select
      className={styles.select}
      value={value}
      required={required}
      onChange={(event) => onChange(event.target.value)}
    >
      <option value="">{placeholder}</option>

      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  </label>
);

export default SelectField;
