"use client";

import { useRouter } from "next/navigation";
import { useSession } from "@/entities/user";
import { useAuthModal } from "@/features/auth";

export const useStartAction = () => {
  const { status } = useSession();
  const { openModal } = useAuthModal();
  const router = useRouter();

  return () => {
    if (status === "authenticated") {
      router.push("/kabinet");
      return;
    }

    openModal();
  };
};
