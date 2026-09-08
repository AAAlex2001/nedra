"use client";

import { useState } from "react";
import styles from "./style.module.scss";

const ShareButton = () => {
  const [copied, setCopied] = useState(false);

  const copyLink = async () => {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button type="button" className={styles.button} onClick={() => void copyLink()}>
      {copied ? "Ссылка скопирована" : "Поделиться"}
    </button>
  );
};

export default ShareButton;
