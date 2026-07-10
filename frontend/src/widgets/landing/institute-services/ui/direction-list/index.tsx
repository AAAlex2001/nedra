import { ChevronIcon } from "@/shared/ui/icons";
import { type Direction, formatServiceCount } from "../../data";
import styles from "./style.module.scss";

type DirectionListProps = {
  directions: Direction[];
  activeId: string;
  onSelect: (id: string) => void;
};

const DirectionList = ({ directions, activeId, onSelect }: DirectionListProps) => (
  <div className={styles.list} role="tablist">
    {directions.map((direction) => {
      const isActive = direction.id === activeId;

      return (
        <button
          key={direction.id}
          type="button"
          role="tab"
          aria-selected={isActive}
          className={`${styles.item} ${isActive ? styles.itemActive : ""}`}
          onClick={() => onSelect(direction.id)}
        >
          <span className={styles.number}>{direction.id}</span>
          <span className={styles.title}>{direction.title}</span>
          <span className={styles.count}>
            {formatServiceCount(direction.serviceCount)}
          </span>
          <ChevronIcon
            className={`${styles.chevron} ${isActive ? styles.chevronActive : ""}`}
          />
        </button>
      );
    })}
  </div>
);

export default DirectionList;
