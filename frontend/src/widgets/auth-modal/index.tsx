"use client";

import { useState } from "react";
import { LoginForm, RegisterForm, useAuthModal, type AuthMode } from "@/features/auth";
import Modal from "@/shared/ui/modal";

const TITLES: Record<AuthMode, string> = {
  login: "Вход",
  register: "Регистрация",
};

const AuthModal = () => {
  const { open, closeModal } = useAuthModal();
  const [mode, setMode] = useState<AuthMode>("login");

  return (
    <Modal open={open} title={TITLES[mode]} onClose={closeModal}>
      {mode === "login" ? (
        <LoginForm onSuccess={closeModal} onSwitchToRegister={() => setMode("register")} />
      ) : (
        <RegisterForm
          onSuccess={closeModal}
          onSwitchToLogin={() => setMode("login")}
          onClose={closeModal}
        />
      )}
    </Modal>
  );
};

export default AuthModal;
