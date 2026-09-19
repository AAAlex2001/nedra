import Spinner from "@/shared/ui/spinner";
import styles from "./style.module.scss";

const Loader = () => (
  <div className={styles.loader}>
    <Spinner size={28} />
  </div>
);

export default Loader;
