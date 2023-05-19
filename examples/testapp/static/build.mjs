import * as esbuild from "esbuild"
import { copy } from "esbuild-plugin-copy"
import { entryPoints } from "./entryPoints.mjs"

await esbuild.build({
    entryPoints: entryPoints,
    bundle: true,
    minify: true,
    write: true,
    treeShaking: true,
    sourcemap: true,
    logLevel: "info",
    outdir: "dist",
    legalComments: "none",
    allowOverwrite: true,
    plugins: [
        copy({
            assets: [
                {
                    from: ["./node_modules/bootstrap/dist/js/*.min.js"],
                    to: ["./bootstrap/js"],
                },
                {
                    from: ["./node_modules/bootstrap/dist/css/*.min.css"],
                    to: ["./bootstrap/css"],
                },
            ],
        }),
    ],
})

