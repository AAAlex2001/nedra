"use client";

import { useState } from "react";
import { confirmEmailChange, requestEmailChange, type User } from "@/entities/user";
import { keepDigits } from "@/shared/lib/text";
import { DetailsRow } from "@/shared/ui/details-table";
import EditButton from "@/shared/ui/edit-button";
import RowEditor from "@/shared/ui/row-editor";
import TextField from "@/shared/ui/text-field";
import { useAction } from "../../model/use-action";
import styles from "./style.module.scss";

type Step = "view" | "email" | "code";

type EmailRowProps = {
  email: string;
  onChanged: (user: User) => void;
};

const EmailRow = ({ email, onChanged }: EmailRowProps) => {
  const [step, setStep] = useState<Step>("view");
  const [draft, setDraft] = useState("");
  const [code, setCode] = useState("");
  const action = useAction();

  const open = () => {
    setDraft("");
    setCode("");
    action.reset();
    setStep("email");
  };

  const sendCode = async () => {
    const sent = await action.run(() => requestEmailChange(draft.trim()));
    if (sent) setStep("code");
  };

  const confirm = async () => {
    const confirmed = await action.run(async () => {
      const user = await confirmEmailChange(code);
      onChanged(user);
    });

    if (confirmed) setStep("view");
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
          Отправили код на <strong>{draft.trim()}</strong>. Он действует 15 минут.{" "}
          <button
            type="button"
            className={styles.resend}
            disabled={action.pending}
            onClick={() => void sendCode()}
          >
            Отправить ещё раз
          </button>
        </p>
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
