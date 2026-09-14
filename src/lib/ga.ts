/**
 * Send a GA4 event that survives a cold page load.
 *
 * `sendGAEvent` from @next/third-parties pushes onto `window.dataLayer`, and
 * drops the event with a console warning when that array does not exist yet:
 *
 *     @next/third-parties: GA dataLayer dataLayer does not exist
 *
 * On a client-side navigation the GA script is long since loaded, so it works.
 * On a **cold load of a deep link** the page's mount effect runs during
 * hydration, before the `<GoogleAnalytics>` script at the end of the tree has
 * created the array, and the event is simply lost.
 *
 * That is not a rare edge. It is every QR scan, every link shared into a chat
 * app, and every social or search click that lands straight on `/screener` or
 * `/results` rather than on the home page. It is why `screener_completed`
 * outran `screener_started` and the completion rate read over 100%: visitors
 * who land deep fire the completion (by then GA has loaded) but never the
 * start. The 2026-08-17 Indonesian traffic was 83 of 103 sessions landing
 * directly on `/screener`, and it recorded 25 starts against 75 completions.
 *
 * So: push immediately when GA is ready, otherwise hold the event and flush it
 * as soon as the array appears. Give up after ~10s rather than leaking a timer
 * on a page where GA is blocked outright, which is a real outcome with an ad
 * blocker and not worth retrying forever.
 */
type GAEventArgs = [string, string, Record<string, unknown>?];

const PENDING: GAEventArgs[] = [];
const POLL_MS = 250;
const GIVE_UP_MS = 10_000;
let polling = false;

function dataLayer(): unknown[] | null {
  if (typeof window === "undefined") return null;
  const dl = (window as unknown as { dataLayer?: unknown[] }).dataLayer;
  return Array.isArray(dl) ? dl : null;
}

/**
 * Push in the exact shape @next/third-parties uses: gtag reads an `arguments`
 * object, not a plain array, and the two are not interchangeable to it. Making
 * this identical to the library keeps GA4's parsing on the proven path.
 */
function push(dl: unknown[], [event, name, params]: GAEventArgs) {
  const asArguments = function (this: void, ..._a: unknown[]) {
    // eslint-disable-next-line prefer-rest-params
    dl.push(arguments);
  };
  asArguments(event, name, params ?? {});
}

function flush(dl: unknown[]) {
  while (PENDING.length) {
    const args = PENDING.shift();
    if (args) push(dl, args);
  }
}

function startPolling() {
  if (polling) return;
  polling = true;
  const started = Date.now();
  const tick = () => {
    const dl = dataLayer();
    if (dl) {
      flush(dl);
      polling = false;
      return;
    }
    if (Date.now() - started >= GIVE_UP_MS) {
      // GA is blocked or failed to load. Drop the queue rather than hold it.
      PENDING.length = 0;
      polling = false;
      return;
    }
    setTimeout(tick, POLL_MS);
  };
  setTimeout(tick, POLL_MS);
}

/**
 * Drop-in replacement for `sendGAEvent("event", name, params)`.
 * Same push shape, so GA4 reads it identically.
 */
export function gaEvent(name: string, params: Record<string, unknown> = {}) {
  const args: GAEventArgs = ["event", name, params];
  const dl = dataLayer();
  if (dl) {
    push(dl, args);
    return;
  }
  PENDING.push(args);
  startPolling();
}
