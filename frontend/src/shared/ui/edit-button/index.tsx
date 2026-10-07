import { PencilIcon } from "@/shared/ui/icons";
import styles from "./style.module.scss";

type EditButtonProps = {
  label: string;
  disabled?: boolean;
  onClick: () => void;
};

const EditButton = ({ label, disabled, onClick }: EditButtonProps) => (
  <button
    type="button"
    className={styles.button}
    aria-label={label}
    title={label}
    disabled={disabled}
    onClick={onClick}
  >
    <PencilIcon className={styles.icon} />
  </button>
);

export default EditButton;
