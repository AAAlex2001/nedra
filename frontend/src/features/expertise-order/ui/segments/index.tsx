import styles from "./style.module.scss";

type SegmentOption<T extends string> = {
  value: T;
  label: string;
  title?: string;
};

type SegmentsProps<T extends string> = {
  label: string;
  options: SegmentOption<T>[];
  value: T;
  onChange: (value: T) => void;
};

const Segments = <T extends string>({ label, options, value, onChange }: SegmentsProps<T>) => (
  <div className={styles.segments} role="tablist" aria-label={label}>
    {options.map((option) => (
      <button
        key={option.value}
        type="button"
        role="tab"
        aria-selected={option.value === value}
        title={option.title}
        className={`${styles.segment} ${option.value === value ? styles.active : ""}`}
        onClick={() => onChange(option.value)}
      >
        {option.label}
      </button>
    ))}
  </div>
);

export type { SegmentOption };

export default Segments;
