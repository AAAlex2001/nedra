"use client";

import { useState } from "react";
import {
  directionTitle,
  updateMyDirections,
  type ExpertCatalog,
  type ExpertProfile,
} from "@/entities/expert";
import { DetailsRow } from "@/shared/ui/details-table";
import EditButton from "@/shared/ui/edit-button";
import MultiSelectField from "@/shared/ui/multi-select-field";
import RowEditor from "@/shared/ui/row-editor";

type DirectionsRowProps = {
  profile: ExpertProfile;
  catalog: ExpertCatalog;
  onChange: (profile: ExpertProfile) => void;
};

const SAVE_FAILED = "Не удалось сохранить направления. Попробуйте ещё раз.";

const DirectionsRow = ({ profile, catalog, onChange }: DirectionsRowProps) => {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(profile.directions);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const open = () => {
    setDraft(profile.directions);
    setError(null);
    setEditing(true);
  };

  const save = async () => {
    if (draft.length === 0) {
      setError("Выберите хотя бы одно направление");
      return;
    }

    setPending(true);
    setError(null);

    try {
      onChange(await updateMyDirections(draft));
      setEditing(false);
    } catch (caught) {
      setError(caught instanceof Error && caught.message ? caught.message : SAVE_FAILED);
    } finally {
      setPending(false);
    }
  };

  const titles = profile.directions.map((code) => directionTitle(catalog, code));

  if (!editing) {
    return (
      <DetailsRow
        label="Направления работы"
        action={<EditButton label="Изменить направления работы" onClick={open} />}
      >
        {titles.join(", ")}
      </DetailsRow>
    );
  }

  return (
    <DetailsRow label="Направления работы">
      <RowEditor
        pending={pending}
        error={error}
        onSave={() => void save()}
        onCancel={() => setEditing(false)}
      >
        <MultiSelectField
          label="Направления работы"
          placeholder="Выберите направления"
          options={catalog.directions.map((direction) => ({
            value: direction.code,
            label: direction.title,
          }))}
          value={draft}
          onChange={setDraft}
        />
      </RowEditor>
    </DetailsRow>
  );
};

export default DirectionsRow;
