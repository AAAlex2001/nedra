"use client";

import { useState } from "react";
import {
  confirmEmailChange,
  EmailCooldownError,
  requestEmailChange,
  type User,
} from "@/entities/user";
import { keepDigits } from "@/shared/lib/text";
import { DetailsRow } from "@/shared/ui/details-table";
import EditButton from "@/shared/ui/edit-button";
import RowEditor from "@/shared/ui/row-editor";
import TextField from "@/shared/ui/text-field";
import { useAction } from "../../model/use-action";
import { useCountdown } from "../../model/use-countdown";
import ResendTimer from "../resend-timer";
import styles from "./style.module.scss";

const CODE_LIFETIME = 300;

type Step = "view" | "email" | "code";

type EmailRowProps = {
  email: string;
  onChanged: (user: User) => void;
};

const EmailRow = ({ email, onChanged }: EmailRowProps) => {
  const [step, setStep] = useState<Step>("view");
  const [draft, setDraft] = useState("");
  const [sentTo, setSentTo] = useState("");
  const [code, setCode] = useState("");
  const action = useAction();
  const countdown = useCountdown();

  const open = () => {
    setCode("");
    action.reset();

    if (countdown.running && sentTo) {
      setDraft(sentTo);
      setStep("code");
      return;
    }

    setDraft("");
    setStep("email");
  };

  const sendCode = () =>
    action.run(async () => {
      try {
        const sent = await requestEmailChange(draft.trim());
        countdown.start(sent.resend_in);
        setSentTo(sent.email);
        setStep("code");
      } catch (caught) {
        if (!(caught instanceof EmailCooldownError)) throw caught;
        countdown.start(caught.seconds);
      }
    });

  const confirm = async () => {
    const confirmed = await action.run(async () => {
      const user = await confirmEmailChange(code);
      onChanged(user);
    });

    if (confirmed) {
      setSentTo("");
      setStep("view");
    }
  };

  if (step === "view") {
    return (
      <DetailsRow label="Email" action={<EditButton label="Изменить email" onClick={open} />}>
        {email}
      </DetailsRow>
    );
  }

  if (step === "email") {
    return (
      <DetailsRow label="Email">
        <RowEditor
          pending={action.pending}
          error={action.error}
          saveText="Получить код"
          saveDisabled={countdown.running}
          onSave={() => void sendCode()}
          onCancel={() => setStep("view")}
        >
          <TextField
            type="email"
            inputMode="email"
            placeholder="Новый email"
            maxLength={320}
            value={draft}
            onChange={setDraft}
          />
          {countdown.running && (
            <ResendTimer
              left={countdown.left}
              total={CODE_LIFETIME}
              caption="до запроса нового кода"
            />
          )}
        </RowEditor>
      </DetailsRow>
    );
  }

  return (
    <DetailsRow label="Email">
      <RowEditor
        pending={action.pending}
        error={action.error}
        saveText="Подтвердить"
        onSave={() => void confirm()}
        onCancel={() => setStep("view")}
      >
        <p className={styles.note}>
          Отправили код на <strong>{sentTo}</strong>. Он действует 5 минут.
        </p>
        {countdown.running ? (
          <ResendTimer
            left={countdown.left}
            total={CODE_LIFETIME}
            caption="до повторной отправки"
          />
        ) : (
          <p className={styles.note}>
            Код истёк.{" "}
            <button
              type="button"
              className={styles.resend}
              disabled={action.pending}
              onClick={() => void sendCode()}
            >
              Отправить новый код
            </button>
          </p>
        )}
        <TextField
          inputMode="numeric"
          autoComplete="one-time-code"
          placeholder="Код из письма"
          maxLength={6}
          value={code}
          onChange={(value) => setCode(keepDigits(value))}
        />
      </RowEditor>
    </DetailsRow>
  );
};

export default EmailRow;
