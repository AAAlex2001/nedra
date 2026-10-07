"use client";

import type { ExpertCatalog } from "@/entities/expert";
import FilesField from "@/shared/ui/files-field";
import TextField from "@/shared/ui/text-field";
import { useExpertiseOrder } from "../../model/use-expertise-order";
import AreaSection from "../area-section";
import CustomerSection from "../customer-section";
import DeadlineSection from "../deadline-section";
import KindSection from "../kind-section";
import ObjectSection from "../object-section";
import OrderShell from "../order-shell";
import PriceSection from "../price-section";
import RequirementSection from "../requirement-section";

type ExpertiseFormProps = {
  catalog: ExpertCatalog;
};

const ACCEPT = ".pdf,.doc,.docx,.jpg,.jpeg,.png";

const ExpertiseForm = ({ catalog }: ExpertiseFormProps) => {
  const expertise = useExpertiseOrder(catalog);
  const { order } = expertise;
  const { state } = order;

  return (
    <OrderShell
      order={order}
      executors="Эксперты"
      submitText="Отправить на экспертизу"
      canSubmit={expertise.canSubmit}
      onSubmit={expertise.submit}
    >
      <ObjectSection
        objects={catalog.objects}
        value={state.objectCode}
        onSelect={expertise.selectObject}
      />

      {expertise.contractKinds.length > 1 && (
        <KindSection
          kinds={expertise.contractKinds}
          value={state.contractKind}
          onSelect={expertise.selectKind}
        />
      )}

      <TextField
        label="Наименование документации"
        required
        placeholder="Как на титульном листе проекта"
        maxLength={500}
        value={state.objectName}
        onChange={order.changeObjectName}
      />

      <RequirementSection
        hazardClasses={catalog.hazard_classes}
        categories={catalog.categories}
        mode={state.mode}
        hazardClass={state.hazardClass}
        category={state.category}
        requiredCategory={expertise.requiredCategory}
        onMode={expertise.setMode}
        onHazard={expertise.selectHazard}
        onCategory={expertise.selectCategory}
      />

      <AreaSection
        areas={catalog.areas}
        available={expertise.availableAreas}
        value={state.areaCode}
        onSelect={expertise.selectArea}
      />

      <DeadlineSection
        label="Когда нужно заключение"
        executor="эксперта"
        value={state.deadline}
        onSelect={order.selectDeadline}
      />

      <PriceSection
        label="Ваша цена за экспертизу, ₽"
        executors="Эксперты"
        value={state.price}
        onChange={order.changePrice}
      />

      <FilesField
        label="Документация"
        required
        files={state.files}
        accept={ACCEPT}
        hint="PDF, Word, JPG или PNG, до 50 МБ каждый. Можно приложить несколько файлов. Если документации нет — приложите техническое задание."
        onAdd={expertise.addFiles}
        onRemove={expertise.removeFile}
      />

      <CustomerSection order={order} />

      <TextField
        label="Комментарий"
        multiline
        placeholder="Что важно знать эксперту: сроки, особенности объекта, на что обратить внимание"
        maxLength={4000}
        value={state.comment}
        onChange={order.changeComment}
      />
    </OrderShell>
  );
};

export default ExpertiseForm;
