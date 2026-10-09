"use client";

import classNames from "classnames";
import { useState } from "react";
import type { OfferAnswer as Answer } from "@/entities/expertise";
import { formatRub } from "@/shared/lib/money";
import Button from "@/shared/ui/button";
import PriceForm from "../price-form";
import styles from "./style.module.scss";

type OfferAnswerProps = {
  offer: number;
  negotiable: boolean;
  pending: boolean;
  onAnswer: (answer: Answer, price?: number) => void;
};

const OfferAnswer = ({ offer, negotiable, pending, onAnswer }: OfferAnswerProps) => {
  const [countering, setCountering] = useState(false);

  return (
    <div className={styles.root}>
      <div className={styles.buttons}>
        <button
          type="button"
          className={styles.secondary}
          disabled={pending}
          onClick={() => onAnswer("decline")}
        >
          Отказаться
        </button>
        {negotiable && (
          <button
            type="button"
            className={classNames(styles.secondary, countering && styles.secondaryActive)}
            disabled={pending}
            onClick={() => setCountering(!countering)}
          >
            Предложить свою цену
          </button>
        )}
        <Button loading={pending} onClick={() => onAnswer("accept")}>
          Принять {formatRub(offer)}
        </Button>
      </div>

      {countering && (
        <PriceForm
          label="Ваша цена, ₽"
          submitText="Отправить аудитору"
          pending={pending}
          below={offer}
          onSubmit={(price) => onAnswer("counter", price)}
        />
      )}
    </div>
  );
};

export default OfferAnswer;
