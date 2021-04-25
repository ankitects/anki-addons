const fs = require("fs");
const esbuild = require("esbuild");
const sveltePlugin = require("esbuild-svelte");

if (!fs.existsSync("./dist/")) {
  fs.mkdirSync("./dist/");
}
fs.copyFileSync("__init__.py", "dist/__init__.py");

esbuild
  .build({
    entryPoints: ["./addon.js"],
    outdir: "dist",
    format: "esm",
    minify: false,
    bundle: true,
    splitting: false,
    plugins: [sveltePlugin()],
  })
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
