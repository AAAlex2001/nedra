import styles from "./style.module.scss";

type MenuToggleIconProps = {
  open: boolean;
};

const MenuToggleIcon = ({ open }: MenuToggleIconProps) => (
  <span className={styles.icon} data-open={open} aria-hidden="true">
    <span className={styles.line} />
    <span className={styles.line} />
    <span className={styles.line} />
  </span>
);

export default MenuToggleIcon;
