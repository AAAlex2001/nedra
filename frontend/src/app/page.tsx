import styles from "./page.module.scss";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <h1>Nedra</h1>
        <p>Next.js + TypeScript + SCSS</p>
      </main>
    </div>
  );
}
