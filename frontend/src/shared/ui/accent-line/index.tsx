import styles from "./style.module.scss";

type AccentLineProps = {
  width: 50 | 30 | 150;
};

const AccentLine = ({ width }: AccentLineProps) => (
  <span className={styles.line} style={{ width }} aria-hidden="true" />
);

export default AccentLine;
