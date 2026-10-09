"use client";

import { useEffect, useReducer, useState } from "react";
import { fetchMyExpertises, usesCompany, type CustomerType } from "@/entities/expertise";
import { customerErrors } from "./customer-validation";
import { INITIAL_STATE, orderReducer } from "./reducer";
import type { CompanyField, Deadline, IndividualField } from "./types";

type OrderRequest = (formData: FormData) => Promise<unknown>;

const SUBMIT_FAILED = "Не удалось отправить заявку. Попробуйте ещё раз.";

const DEFAULT_CUSTOMER_TYPES: CustomerType[] = ["legal", "individual"];

const parsePrice = (value: string): number => Number(value.replace(/\s/g, "").replace(",", "."));

export const useOrder = (customerTypes: CustomerType[] = DEFAULT_CUSTOMER_TYPES) => {
  const [state, dispatch] = useReducer(orderReducer, {
    ...INITIAL_STATE,
    customerType: customerTypes[0],
  });
  const [attempted, setAttempted] = useState(false);

  useEffect(() => {
    const fillFromLastOrder = async () => {
      try {
        const items = await fetchMyExpertises();
        const lastCompany = items.find((item) => item.company !== null)?.company;
        const lastIndividual = items.find((item) => item.individual !== null)?.individual;
        const lastType = items[0]?.customer_type;

        if (lastCompany) dispatch({ type: "company/fill", company: lastCompany });
        if (lastIndividual) dispatch({ type: "individual/fill", individual: lastIndividual });
        if (lastType && customerTypes.includes(lastType)) {
          dispatch({ type: "customer/select", customerType: lastType });
        }
      } catch {
        return;
      }
    };

    void fillFromLastOrder();
  }, [customerTypes]);

  const price = parsePrice(state.price);
  const company = usesCompany(state.customerType);
  const customerProblems = customerErrors(state);

  const kpp = state.customerType === "entrepreneur" ? null : state.company.kpp.trim() || null;

  const payload = {
    price,
    customer_type: state.customerType,
    company: company ? { ...state.company, kpp } : null,
    individual: company ? null : state.individual,
    deadline: state.deadline,
    comment: state.comment.trim() || null,
  };

  const changeObjectName = (value: string) => dispatch({ type: "objectName/change", value });
  const selectDeadline = (value: Deadline) => dispatch({ type: "deadline/select", value });
  const changePrice = (value: string) => dispatch({ type: "price/change", value });
  const selectCustomerType = (customerType: CustomerType) =>
    dispatch({ type: "customer/select", customerType });
  const changeCompany = (field: CompanyField, value: string) =>
    dispatch({ type: "company/change", field, value });
  const changeIndividual = (field: IndividualField, value: string) =>
    dispatch({ type: "individual/change", field, value });
  const removeCard = () => dispatch({ type: "card/remove" });
  const changeComment = (value: string) => dispatch({ type: "comment/change", value });
  const closeSuccess = () => dispatch({ type: "success/close" });

  const setCard = (files: File[]) => {
    const [file] = files;
    if (file) dispatch({ type: "card/set", file });
  };

  const send = async (formData: FormData, request: OrderRequest): Promise<boolean> => {
    dispatch({ type: "submit/start" });

    if (company && state.companyCard) {
      formData.append("company_card", state.companyCard);
    }

    try {
      await request(formData);
      dispatch({ type: "submit/success" });
      setAttempted(false);
      return true;
    } catch (error) {
      const message = error instanceof Error && error.message ? error.message : SUBMIT_FAILED;
      dispatch({ type: "submit/error", message });
      return false;
    }
  };

  return {
    state,
    dispatch,
    price,
    customerProblems,
    customerTypes,
    attempted,
    markAttempted: () => setAttempted(true),
    payload,
    changeObjectName,
    selectDeadline,
    changePrice,
    selectCustomerType,
    changeCompany,
    changeIndividual,
    setCard,
    removeCard,
    changeComment,
    closeSuccess,
    send,
  };
};

export type Order = ReturnType<typeof useOrder>;
