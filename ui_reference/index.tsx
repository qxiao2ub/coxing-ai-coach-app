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
    <div className="relative min-h-screen overflow-hidden bg-background font-body text-ink antialiased selection:bg-ice/30">
      {/* Ambient glow layers */}
      <div className="pointer-events-none fixed inset-0 frost-glow" aria-hidden="true" />
      <div
        className="pointer-events-none fixed inset-0"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(90% 60% at 10% 110%, rgba(44, 72, 103, 0.5), transparent 60%)",
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
            {/* Coach chat card */}
            <div
              className="animate-rise edge-glow frost-glow rounded-3xl bg-frost/50 ring-1 ring-frostline backdrop-blur-xl"
              style={{ animationDelay: "60ms" }}
            >
              <div className="p-5 sm:p-6">
                <div className="flex items-center gap-3">
                  <div className="grid size-10 place-items-center rounded-full bg-ice/15 font-display text-lg text-ice ring-1 ring-ice/30">
                    A
                  </div>
                  <div>
                    <p className="font-semibold leading-tight">Coach Anders</p>
                    <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ice">
                      Ready · 8s shell
                    </p>
                  </div>
                  <span className="ml-auto font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
                    dawn · 05:40
                  </span>
                </div>

                <div className="mt-5 space-y-4">
                  <div className="ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-ice/12 px-4 py-3 text-sm text-ink/90">
                    We're running flat water at the lake. Walk me through a calm-start to 32.
                  </div>
                  <div className="max-w-[92%] rounded-2xl rounded-bl-md bg-frostline/30 px-4 py-3 text-sm leading-relaxed text-ink/85">
                    Good. Set the body first — long and laid back to the catch. Count the build out
                    loud so the crew hears it:{" "}
                    <span className="font-medium text-ice">"Easy… easy… building at four."</span> Two
                    strokes to settle the length, then push the rate. Watch the handle stay quiet.
                  </div>
                  <div className="max-w-[70%] rounded-2xl rounded-bl-md bg-frostline/30 px-4 py-3 text-sm leading-relaxed text-ink/85">
                    At 32, drop a <span className="font-medium text-ice">"Breathe."</span> between
                    calls. Let the boat find its glide before you ask for more.
                  </div>
                </div>

                <div className="mt-5 rounded-2xl bg-background/50 px-4 py-3 ring-1 ring-frostline">
                  <div className="flex items-center gap-2">
                    <span className="size-1.5 animate-breathe rounded-full bg-ice" />
                    <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">
                      Coach is listening…
                    </span>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="flex flex-wrap gap-2">
                    <button className="rounded-full bg-frostline/30 px-3 py-1.5 text-xs text-ink/80 transition-colors hover:bg-frostline/50">
                      Calm start
                    </button>
                    <button className="rounded-full bg-frostline/30 px-3 py-1.5 text-xs text-ink/80 transition-colors hover:bg-frostline/50">
                      Build at four
                    </button>
                    <button className="rounded-full bg-frostline/30 px-3 py-1.5 text-xs text-ink/80 transition-colors hover:bg-frostline/50">
                      Breathe
                    </button>
                    <button className="rounded-full bg-frostline/30 px-3 py-1.5 text-xs text-ink/80 transition-colors hover:bg-frostline/50">
                      Hold the length
                    </button>
                  </div>
                  <div className="mt-3 flex items-center gap-2 rounded-2xl bg-background/60 px-3 py-2 ring-1 ring-frostline">
                    <span className="font-mono text-sm text-muted">⌄</span>
                    <span className="text-sm text-muted">Ask the coach a question…</span>
                    <span className="ml-auto font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
                      ⌘↵
                    </span>
                  </div>
                </div>
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
                    width={1200}
                    height={450}
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
