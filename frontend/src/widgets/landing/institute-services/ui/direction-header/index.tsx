import { ChevronIcon } from "@/shared/ui/icons";
import { type Direction, formatServiceCount } from "../../data";
import styles from "./style.module.scss";

type DirectionHeaderProps = {
  direction: Direction;
  isOpen: boolean;
  onSelect: () => void;
};

const DirectionHeader = ({ direction, isOpen, onSelect }: DirectionHeaderProps) => (
  <button
    type="button"
    aria-expanded={isOpen}
    className={`${styles.header} ${isOpen ? styles.open : ""}`}
    onClick={onSelect}
  >
    <span className={styles.number}>{direction.id}</span>
    <span className={styles.count}>{formatServiceCount(direction.serviceCount)}</span>
    <ChevronIcon
      className={`${styles.chevron} ${isOpen ? styles.chevronOpen : ""}`}
    />
    <span className={styles.title}>{direction.title}</span>
  </button>
);

export default DirectionHeader;
