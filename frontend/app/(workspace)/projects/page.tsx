import { EmptyState } from "@/components/status/empty-state";

export const metadata = { title: "Projects" };

export default function ProjectsPage() {
  return (
    <>
      <h1 className="text-3xl font-semibold">Projects</h1>
      <div className="mt-8">
        <EmptyState title="Project context is planned for a later milestone">
          Projects are visible in navigation structure only; no workspace data exists yet.
        </EmptyState>
      </div>
    </>
  );
}
