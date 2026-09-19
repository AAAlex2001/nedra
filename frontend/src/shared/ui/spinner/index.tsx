import styles from "./style.module.scss";

type SpinnerProps = {
  size?: number;
  tone?: "dark" | "light";
  className?: string;
};

const Spinner = ({ size = 20, tone = "dark", className }: SpinnerProps) => (
  <span
    role="status"
    aria-label="Загрузка"
    className={`${styles.spinner} ${tone === "light" ? styles.light : ""} ${className ?? ""}`}
    style={{ width: size, height: size }}
  />
);

export default Spinner;
