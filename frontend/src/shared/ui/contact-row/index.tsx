import type { ReactNode } from "react";
import styles from "./style.module.scss";

type ContactRowProps = {
  icon: ReactNode;
  href?: string;
  align?: "center" | "top";
  children: ReactNode;
};

const ContactRow = ({ icon, href, align = "center", children }: ContactRowProps) => (
  <div className={`${styles.row} ${align === "top" ? styles.top : ""}`}>
    {icon}
    {href ? (
      <a className={styles.link} href={href}>
        {children}
      </a>
    ) : (
      <span className={styles.text}>{children}</span>
    )}
  </div>
);

export default ContactRow;
