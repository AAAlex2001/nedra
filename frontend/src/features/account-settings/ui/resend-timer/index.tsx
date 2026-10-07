import styles from "./style.module.scss";

const RADIUS = 9;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

type ResendTimerProps = {
  left: number;
  total: number;
  caption: string;
};

const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const rest = String(seconds % 60).padStart(2, "0");

  return `${minutes}:${rest}`;
};

const ResendTimer = ({ left, total, caption }: ResendTimerProps) => {
  const share = Math.min(1, left / total);
  const offset = CIRCUMFERENCE * (1 - share);

  return (
    <div className={styles.root} role="timer">
      <span className={styles.pill}>
        <svg className={styles.ring} viewBox="0 0 22 22" aria-hidden="true">
          <circle className={styles.track} cx="11" cy="11" r={RADIUS} />
          <circle
            className={styles.progress}
            cx="11"
            cy="11"
            r={RADIUS}
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
          />
        </svg>
        <span className={styles.time}>{formatTime(left)}</span>
      </span>
      <span className={styles.caption}>{caption}</span>
    </div>
  );
};

export default ResendTimer;
