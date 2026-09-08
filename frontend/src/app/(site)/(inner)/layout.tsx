import RequestSection from "@/widgets/landing/request-form";

export default function InnerPagesLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <RequestSection />
    </>
  );
}
