// node build.mjs  (three and esbuild come from the anatomy3d build's node_modules; set NODE_MODULES to move them)
const NM = process.env.NODE_MODULES || "/private/tmp/claude-501/-Users-ianharris-projects-OralCheck/634f3aef-ed1c-43ea-a1d2-663a14401869/scratchpad/proto3d/node_modules";
const { build } = await import(NM + "/esbuild/lib/main.js");
await build({ entryPoints: ["src/plate.js"], bundle: true, minify: true, format: "iife", outfile: "plate.bundle.js", nodePaths: [NM], logLevel: "warning" });
