import { DemoWorkspace } from "@/features/demo/demo-workspace";

export const metadata = {
  title: "Interactive Demo",
  description:
    "A guided ContextOS demo with fictional sample data and deterministic prepared responses.",
};

export default function DemoPage() {
  return <DemoWorkspace />;
}
