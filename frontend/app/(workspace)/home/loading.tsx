export default function HomeLoading() {
  return (
    <div className="space-y-8" aria-label="Loading home workspace">
      <section className="quiet-panel rounded-lg p-5 md:p-7">
        <div className="h-8 w-64 max-w-full animate-pulse rounded bg-[var(--surface-inspector)]" />
        <div className="mt-3 h-4 w-full max-w-2xl animate-pulse rounded bg-[var(--surface-inspector)]" />
        <div className="mt-6 h-32 w-full animate-pulse rounded-lg bg-[var(--surface-inspector)]" />
      </section>
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {Array.from({ length: 6 }, (_, index) => (
          <div className="quiet-panel rounded-lg p-4" key={index}>
            <div className="h-4 w-28 animate-pulse rounded bg-[var(--surface-inspector)]" />
            <div className="mt-3 h-7 w-20 animate-pulse rounded bg-[var(--surface-inspector)]" />
          </div>
        ))}
      </section>
      <div className="grid gap-4 xl:grid-cols-2">
        {Array.from({ length: 4 }, (_, index) => (
          <section className="quiet-panel rounded-lg p-4" key={index}>
            <div className="h-5 w-40 animate-pulse rounded bg-[var(--surface-inspector)]" />
            <div className="mt-4 space-y-2">
              <div className="h-12 animate-pulse rounded-lg bg-[var(--surface-inspector)]" />
              <div className="h-12 animate-pulse rounded-lg bg-[var(--surface-inspector)]" />
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
