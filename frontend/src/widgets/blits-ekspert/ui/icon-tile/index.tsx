import {
  CheckIcon,
  ClockIcon,
  DirectorIcon,
  DocumentIcon,
  PeopleIcon,
  ProcedureDocumentIcon,
} from "@/shared/ui/icons";
import type { IconKey } from "../../data";
import styles from "./style.module.scss";

type IconTileProps = {
  icon: IconKey;
};

const IconTile = ({ icon }: IconTileProps) => (
  <span className={styles.tile} aria-hidden="true">
    {icon === "document" && <DocumentIcon className={styles.icon} />}
    {icon === "clock" && <ClockIcon className={styles.icon} />}
    {icon === "check" && <CheckIcon className={styles.icon} />}
    {icon === "people" && <PeopleIcon className={styles.icon} />}
    {icon === "certificate" && <DirectorIcon className={styles.icon} />}
    {icon === "shield" && <ProcedureDocumentIcon className={styles.icon} />}
  </span>
);

export default IconTile;
