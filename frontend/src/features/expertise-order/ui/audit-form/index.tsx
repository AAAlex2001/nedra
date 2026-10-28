"use client";

import {
  AUDIT_FILES_ACCEPT,
  AuditChecklist,
  type AuditChecklistItem,
} from "@/entities/expertise";
import TextField from "@/shared/ui/text-field";
import { useAuditOrder } from "../../model/use-audit-order";
import ApplicantBlock from "../audit-details/applicant-block";
import BudgetBlock from "../audit-details/budget-block";
import ObjectsBlock from "../audit-details/objects-block";
import ParamsBlock from "../audit-details/params-block";
import StagesBlock from "../audit-details/stages-block";
import TimingBlock from "../audit-details/timing-block";
import CustomerSection from "../customer-section";
import OrderShell from "../order-shell";

type AuditFormProps = {
  checklist: AuditChecklistItem[];
};

const CHECKLIST_NOTE =
  "Загрузите имеющиеся документы сейчас или после согласования Плана аудита. Аудитор проанализирует комплектность и направит запрос на недостающие сведения. Принимаются PDF, файлы электронной подписи, фото и видео.";

const AuditForm = ({ checklist }: AuditFormProps) => {
  const audit = useAuditOrder();
  const { order, steps, form, errors } = audit;
  const step = steps.current.key;
  const onChange = audit.changeForm;

  return (
    <OrderShell
      order={order}
      steps={steps}
      executors="Аудиторы"
      submitText="Отправить на аудит"
      errors={errors}
      onSubmit={audit.submit}
      theme="theme-green"
    >
      {step === "applicant" && <ApplicantBlock form={form} errors={errors} onChange={onChange} />}

      {step === "objects" && <ObjectsBlock form={form} errors={errors} onChange={onChange} />}

      {step === "params" && (
        <>
          <StagesBlock form={form} errors={errors} onChange={onChange} />
          <ParamsBlock form={form} errors={errors} onChange={onChange} />
        </>
      )}

      {step === "terms" && (
        <>
          <TimingBlock form={form} errors={errors} onChange={onChange} />
          <BudgetBlock
            form={form}
            errors={errors}
            onChange={onChange}
            price={order.state.price}
            onPriceChange={order.changePrice}
          />
        </>
      )}

      {step === "documents" && (
        <AuditChecklist
          checklist={checklist}
          files={order.state.auditFiles}
          note={CHECKLIST_NOTE}
          onAdd={audit.addFiles}
          onRemove={audit.removeFile}
        />
      )}

      {step === "customer" && (
        <CustomerSection order={order} errors={errors} cardAccept={AUDIT_FILES_ACCEPT} />
      )}

      {step === "comment" && (
        <TextField
          label="Комментарий"
          multiline
          placeholder="Что важно знать аудитору: структура организации, количество ОПО, на что обратить внимание"
          maxLength={4000}
          value={order.state.comment}
          onChange={order.changeComment}
        />
      )}
    </OrderShell>
  );
};

export default AuditForm;
