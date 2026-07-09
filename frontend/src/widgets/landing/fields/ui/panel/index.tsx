"use client";

import { useState } from "react";
import { FIELDS_ITEMS } from "../../data";
import FieldsAccordion from "../accordion";
import FieldsDrawer from "../drawer";
import FieldsHeading from "../heading";
import styles from "./style.module.scss";

const FieldsPanel = () => {
  const [activeId, setActiveId] = useState(FIELDS_ITEMS[0]?.id ?? "01");
  const activeItem =
    FIELDS_ITEMS.find((item) => item.id === activeId) ?? FIELDS_ITEMS[0];

  if (!activeItem) {
    return null;
  }

  return (
    <div className={styles.main}>
      <div className={styles.left}>
        <FieldsHeading />
        <FieldsAccordion activeId={activeId} onSelect={setActiveId} />
      </div>

      <FieldsDrawer item={activeItem} />
    </div>
  );
};

export default FieldsPanel;
