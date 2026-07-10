import { DIRECTIONS, SERVICES_DATA } from "./data";
import Catalog from "./ui/catalog";
import styles from "./style.module.scss";

const InstituteServices = () => (
  <section className={styles.section}>
    <Catalog directions={DIRECTIONS} heading={SERVICES_DATA} />
  </section>
);

export default InstituteServices;
