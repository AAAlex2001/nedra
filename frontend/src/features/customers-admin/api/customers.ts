import { readErrorMessage } from "@/shared/api";

export const deleteCustomer = async (basePath: string, userId: number): Promise<void> => {
  const response = await fetch(`${basePath}/api/customers/${userId}`, { method: "DELETE" });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }
};
