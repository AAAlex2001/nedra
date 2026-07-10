"use client";

import { useState } from "react";
import { DIRECTIONS, SERVICES_DATA } from "../../data";
import DetailPanel from "../detail-panel";
import DirectionList from "../direction-list";
import Heading from "../heading";
import styles from "./style.module.scss";

const Catalog = () => {
  const [activeId, setActiveId] = useState(DIRECTIONS[0].id);
  const activeDirection = DIRECTIONS.find((item) => item.id === activeId) ?? DIRECTIONS[0];

  return (
    <div className={styles.catalog}>
      <div className={styles.left}>
        <Heading title={SERVICES_DATA.title} subtitle={SERVICES_DATA.subtitle} />
        <DirectionList directions={DIRECTIONS} activeId={activeId} onSelect={setActiveId} />
      </div>

      <DetailPanel key={activeDirection.id} direction={activeDirection} />
    </div>
  );
};

export default Catalog;
