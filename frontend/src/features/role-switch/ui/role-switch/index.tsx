"use client";

import { ROLE_LABELS, type UserRole } from "@/entities/user";
import Spinner from "@/shared/ui/spinner";
import { useRoleSwitch } from "../../model/use-role-switch";
import styles from "./style.module.scss";

const ROLES: UserRole[] = ["customer", "expert"];

type RoleSwitchProps = {
  active: UserRole;
};

const RoleSwitch = ({ active }: RoleSwitchProps) => {
  const { select, pending, error } = useRoleSwitch();

  return (
    <div className={styles.root}>
      <div className={styles.switch} role="radiogroup" aria-label="Активная роль">
        {ROLES.map((role) => (
          <button
            key={role}
            type="button"
            role="radio"
            aria-checked={active === role}
            disabled={pending}
            className={`${styles.option} ${active === role ? styles.optionActive : ""}`}
            onClick={() => void select(role)}
          >
            {pending && active !== role ? <Spinner size={14} /> : ROLE_LABELS[role]}
          </button>
        ))}
      </div>

      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
};

export default RoleSwitch;
