import type { AuditBlockProps } from "../../model/audit-form";
import ApplicantBlock from "./applicant-block";
import BudgetBlock from "./budget-block";
import ObjectsBlock from "./objects-block";
import ParamsBlock from "./params-block";
import StagesBlock from "./stages-block";
import TimingBlock from "./timing-block";

type AuditDetailsProps = AuditBlockProps & {
  price: string;
  onPriceChange: (value: string) => void;
};

const AuditDetails = ({ form, errors, onChange, price, onPriceChange }: AuditDetailsProps) => (
  <>
    <ApplicantBlock form={form} errors={errors} onChange={onChange} />
    <ObjectsBlock form={form} errors={errors} onChange={onChange} />
    <StagesBlock form={form} errors={errors} onChange={onChange} />
    <ParamsBlock form={form} errors={errors} onChange={onChange} />
    <TimingBlock form={form} errors={errors} onChange={onChange} />
    <BudgetBlock
      form={form}
      errors={errors}
      onChange={onChange}
      price={price}
      onPriceChange={onPriceChange}
    />
  </>
);

export default AuditDetails;
