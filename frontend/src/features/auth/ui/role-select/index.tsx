import type { UserRole } from "@/entities/user";
import styles from "./style.module.scss";

type RoleOption = {
  role: UserRole;
  title: string;
  hint: string;
};

const ROLE_OPTIONS: RoleOption[] = [
  {
    role: "customer",
    title: "Заказчик",
    hint: "Направляете документацию на экспертизу и получаете заключение.",
  },
  {
    role: "expert",
    title: "Эксперт",
    hint: "Проводите экспертизу и подписываете заключение. Нужна аттестация Ростехнадзора.",
  },
];

type RoleSelectProps = {
  value: UserRole;
  onChange: (role: UserRole) => void;
};

const RoleSelect = ({ value, onChange }: RoleSelectProps) => {
  const current = ROLE_OPTIONS.find((option) => option.role === value);

  return (
    <div className={styles.field}>
      <span className={styles.label}>
        Тип аккаунта<span className={styles.required}> *</span>
      </span>

      <div className={styles.control} role="radiogroup" aria-label="Тип аккаунта">
        {ROLE_OPTIONS.map((option) => (
          <button
            key={option.role}
            type="button"
            role="radio"
            aria-checked={value === option.role}
            className={`${styles.segment} ${value === option.role ? styles.active : ""}`}
            onClick={() => onChange(option.role)}
          >
            {option.title}
          </button>
        ))}
      </div>

      <p className={styles.hint}>
        {current?.hint} Изменить тип после регистрации нельзя.
      </p>
    </div>
  );
};

export default RoleSelect;
