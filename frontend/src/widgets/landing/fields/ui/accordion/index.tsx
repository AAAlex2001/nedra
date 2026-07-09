import { ChevronIcon } from "@/shared/ui/icons";
import { FIELDS_ITEMS, formatServiceCount } from "../../data";
import styles from "./style.module.scss";

type FieldsAccordionProps = {
  activeId: string;
  onSelect: (id: string) => void;
};

const FieldsAccordion = ({ activeId, onSelect }: FieldsAccordionProps) => {
  return (
    <div className={styles.accordion} role="tablist">
      {FIELDS_ITEMS.map((item) => {
        const isActive = item.id === activeId;

        return (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            className={`${styles.item} ${isActive ? styles.itemActive : ""}`}
            onClick={() => onSelect(item.id)}
          >
            <span className={styles.number}>{item.id}</span>
            <span className={styles.title}>{item.title}</span>
            <span className={styles.count}>
              {formatServiceCount(item.serviceCount)}
            </span>
            <ChevronIcon
              className={`${styles.chevron} ${isActive ? styles.chevronActive : ""}`}
            />
          </button>
        );
      })}
    </div>
  );
};

export default FieldsAccordion;
