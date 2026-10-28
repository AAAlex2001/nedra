import type { ReactNode } from "react";
import styles from "./style.module.scss";

type SidebarLayoutProps = {
  sidebar: ReactNode;
  children: ReactNode;
};

const SidebarLayout = ({ sidebar, children }: SidebarLayoutProps) => (
  <div className={styles.layout}>
    <aside className={styles.sidebar}>{sidebar}</aside>
    <div className={styles.content}>{children}</div>
  </div>
);

export default SidebarLayout;
