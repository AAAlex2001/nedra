"use client";
import ServiceNavigation from "@/widgets/service-navigation";
import styles from "./style.module.scss";
export default function GuestBar() {
  return <><div className={styles.spacer} aria-hidden="true" /><aside className={styles.bar} aria-label="Онлайн-сервисы НПИ «Недра»"><ServiceNavigation /></aside></>;
}
