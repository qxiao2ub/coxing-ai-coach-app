import { createFileRoute } from "@tanstack/react-router";
import rowingLake from "../assets/rowing-lake.jpg";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "GLIDE — AI Coxing Coach" },
      { name: "description", content: "Real-time AI coaching for rowing coxswains. Rhythm, breath, sync." },
      { property: "og:title", content: "GLIDE — AI Coxing Coach" },
      { property: "og:description", content: "Real-time AI coaching for rowing coxswains. Rhythm, breath, sync." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <div
      className="relative min-h-screen overflow-hidden bg-background font-body text-ink antialiased selection:bg-ice/30"
      style={{
        backgroundImage: `linear-gradient(rgba(255, 255, 255, 0.74), rgba(255, 255, 255, 0.84)), url(${rowingLake})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
      }}
    >
      {/* Ambient glow layers */}
      <div className="pointer-events-none fixed inset-0 frost-glow" aria-hidden="true" />
      <div
        className="pointer-events-none fixed inset-0"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(90% 60% at 10% 110%, rgba(125, 170, 220, 0.16), transparent 60%)",
        }}
      />

      <div className="relative mx-auto max-w-6xl px-5 sm:px-8">
        {/* Header */}
        <header className="animate-rise flex items-center justify-between py-5">
          <div className="flex items-center gap-3">
            <div className="grid size-9 place-items-center rounded-xl bg-frost font-display text-lg text-ice ring-1 ring-frostline">
              G
            </div>
            <div>
              <p className="font-display text-xl leading-none tracking-wide">GLIDE</p>
              <p className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted">coxing coach</p>
            </div>
          </div>
          <nav className="hidden items-center gap-6 font-mono text-[11px] uppercase tracking-[0.18em] text-muted sm:flex">
            <span className="text-ice">Console</span>
            <span className="cursor-pointer transition-colors hover:text-ice">Sessions</span>
            <span className="cursor-pointer transition-colors hover:text-ice">Calls</span>
            <span className="cursor-pointer transition-colors hover:text-ice">Progress</span>
          </nav>
          <div className="flex items-center gap-2">
            <span className="pulse-ring hidden size-2 rounded-full bg-ice text-ice sm:inline-block" />
            <span className="hidden font-mono text-[11px] uppercase tracking-[0.16em] text-muted sm:inline">
              On the water
            </span>
            <button className="rounded-xl bg-ice px-4 py-2 text-sm font-semibold text-background transition-colors hover:bg-ice/85">
              New session
            </button>
          </div>
        </header>

        {/* Main content */}
        <main className="grid grid-cols-1 gap-5 pb-4 lg:grid-cols-12">
          {/* Left column */}
          <section className="space-y-5 lg:col-span-7">
            {/* Upload recording */}
            <div
              className="animate-rise edge-glow rounded-3xl bg-frost/50 p-5 ring-1 ring-frostline backdrop-blur-xl sm:p-6"
              style={{ animationDelay: "60ms" }}
            >
              <div className="flex flex-wrap items-center gap-3">
                <button className="flex items-center gap-2 rounded-xl bg-ice px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-ice/85">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="size-4"
                    aria-hidden="true"
                  >
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  Upload recording
                </button>
                <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
                  Specialized Coach Feedback
                </span>
              </div>
            </div>

            {/* Today's outing card */}
            <div
              className="animate-rise edge-glow rounded-3xl bg-frost/40 ring-1 ring-frostline backdrop-blur-xl"
              style={{ animationDelay: "140ms" }}
            >
              <div className="p-5 sm:p-6">
                <div className="flex items-end justify-between">
                  <div>
                    <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                      Today's outing
                    </p>
                    <h2 className="mt-1 font-display text-3xl leading-none tracking-wide">
                      Flat water · Lake 2k
                    </h2>
                  </div>
                  <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ice">
                    Reviewed
                  </span>
                </div>
                <div className="mt-4 grid grid-cols-3 gap-3">
                  <div className="rounded-xl bg-background/40 px-3 py-3 ring-1 ring-frostline">
                    <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
                      Avg rate
                    </p>
                    <p className="mt-1 font-display text-2xl leading-none">
                      28 <span className="text-sm text-muted">spm</span>
                    </p>
                  </div>
                  <div className="rounded-xl bg-background/40 px-3 py-3 ring-1 ring-frostline">
                    <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
                      Split
                    </p>
                    <p className="mt-1 font-display text-2xl leading-none">
                      1:39 <span className="text-sm text-muted">/500</span>
                    </p>
                  </div>
                  <div className="rounded-xl bg-background/40 px-3 py-3 ring-1 ring-frostline">
                    <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
                      Call sync
                    </p>
                    <p className="mt-1 font-display text-2xl leading-none">
                      94<span className="text-sm text-ice">%</span>
                    </p>
                  </div>
                </div>
                <div className="mt-4 aspect-[16/6] w-full overflow-hidden rounded-2xl bg-background/50 outline-1 -outline-offset-1 outline-black/5">
                  <img
                    src={rowingLake}
                    alt="Rowing shell gliding across a misty dawn lake"
                    className="h-full w-full object-cover"
                    width={1920}
                    height={720}
                    loading="lazy"
                  />
                </div>
              </div>
            </div>
          </section>

          {/* Right column */}
          <aside className="space-y-5 lg:col-span-5">
            {/* Recent sessions */}
            <div
              className="animate-rise rounded-3xl bg-frost/40 p-5 ring-1 ring-frostline backdrop-blur-xl"
              style={{ animationDelay: "110ms" }}
            >
              <div className="flex items-center justify-between">
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                  Recent sessions
                </p>
                <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-ice">
                  3 new
                </span>
              </div>
              <div className="mt-3 space-y-2">
                <SessionRow
                  initial="S"
                  highlighted
                  title="Sprint review · Headwater"
                  meta="22m · 6 calls flagged"
                />
                <SessionRow
                  initial="C"
                  title="Conditioning · Tempo row"
                  meta="45m · transcript"
                />
                <SessionRow
                  initial="R"
                  title="Race plan · Sectionals"
                  meta="saved · 4k build"
                />
              </div>
            </div>

            {/* Live crew */}
            <div
              className="animate-rise rounded-3xl bg-frost/40 p-5 ring-1 ring-frostline backdrop-blur-xl"
              style={{ animationDelay: "180ms" }}
            >
              <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                Live crew
              </p>
              <div className="mt-4 flex items-end gap-3">
                <div className="flex h-24 items-end gap-1.5">
                  <div className="w-2 rounded-full bg-frostline/60" style={{ height: "40%" }} />
                  <div className="w-2 rounded-full bg-frostline/60" style={{ height: "55%" }} />
                  <div className="w-2 rounded-full bg-frostline/60" style={{ height: "70%" }} />
                  <div className="w-2 rounded-full bg-ice" style={{ height: "92%" }} />
                  <div className="w-2 rounded-full bg-frostline/60" style={{ height: "60%" }} />
                  <div className="w-2 rounded-full bg-frostline/60" style={{ height: "35%" }} />
                </div>
                <div className="ml-auto text-right">
                  <p className="font-display text-4xl leading-none">32</p>
                  <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-ice">
                    live rate
                  </p>
                </div>
              </div>
            </div>
          </aside>
        </main>

        {/* Footer */}
        <footer className="mt-2 flex flex-wrap items-center justify-between gap-3 border-t border-frostline/50 py-6">
          <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
            GLIDE · rhythm, breath, sync
          </p>
          <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
            Crew of eight · dock 4
          </p>
        </footer>
      </div>
    </div>
  );
}

function SessionRow({
  initial,
  title,
  meta,
  highlighted = false,
}: {
  initial: string;
  title: string;
  meta: string;
  highlighted?: boolean;
}) {
  return (
    <div className="flex cursor-pointer items-center gap-3 rounded-2xl bg-background/40 px-3 py-3 ring-1 ring-frostline transition-colors hover:bg-background/60">
      <div
        className={`grid size-10 place-items-center rounded-xl font-display text-base ${
          highlighted ? "bg-ice/12 text-ice" : "bg-frostline/40 text-ink/70"
        }`}
      >
        {initial}
      </div>
      <div className="min-w-0">
        <p className="truncate text-sm font-medium">{title}</p>
        <p className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted">{meta}</p>
      </div>
      <span className="ml-auto text-muted">→</span>
    </div>
  );
}
