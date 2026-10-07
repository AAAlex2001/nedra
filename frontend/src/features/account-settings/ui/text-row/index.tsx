"use client";

import { useState } from "react";
import { DetailsRow } from "@/shared/ui/details-table";
import EditButton from "@/shared/ui/edit-button";
import RowEditor from "@/shared/ui/row-editor";
import TextField from "@/shared/ui/text-field";
import { useAction } from "../../model/use-action";

type TextRowProps = {
  label: string;
  value: string;
  type?: "text" | "tel";
  inputMode?: "text" | "tel";
  onSave: (value: string) => Promise<void>;
};

const TextRow = ({ label, value, type = "text", inputMode, onSave }: TextRowProps) => {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const action = useAction();

  const open = () => {
    setDraft(value);
    action.reset();
    setEditing(true);
  };

  const save = async () => {
    const saved = await action.run(() => onSave(draft.trim()));
    if (saved) setEditing(false);
  };

  if (!editing) {
    return (
      <DetailsRow label={label} action={<EditButton label={`Изменить: ${label}`} onClick={open} />}>
        {value}
      </DetailsRow>
    );
  }

  return (
    <DetailsRow label={label}>
      <RowEditor
        pending={action.pending}
        error={action.error}
        onSave={() => void save()}
        onCancel={() => setEditing(false)}
      >
        <TextField
          placeholder={label}
          type={type}
          inputMode={inputMode}
          maxLength={255}
          value={draft}
          onChange={setDraft}
        />
      </RowEditor>
    </DetailsRow>
  );
};

export default TextRow;
