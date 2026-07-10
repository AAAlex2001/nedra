"use client";

import { useState } from "react";
import type { Direction } from "../../data";
import DetailPanel from "../detail-panel";
import DirectionList from "../direction-list";
import Heading from "../heading";
import styles from "./style.module.scss";

type CatalogProps = {
  directions: Direction[];
  heading: { title: string; subtitle: string };
};

const Catalog = ({ directions, heading }: CatalogProps) => {
  const [activeId, setActiveId] = useState(directions[0].id);
  const activeDirection = directions.find((item) => item.id === activeId) ?? directions[0];

  return (
    <div className={styles.catalog}>
      <div className={styles.left}>
        <Heading title={heading.title} subtitle={heading.subtitle} />
        <DirectionList directions={directions} activeId={activeId} onSelect={setActiveId} />
      </div>

      <DetailPanel key={activeDirection.id} direction={activeDirection} />
    </div>
  );
};

export default Catalog;
