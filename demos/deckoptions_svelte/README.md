An example of extending the deck options screen using
a Svelte component. Using Svelte will get you access to the
same styling and components that Anki uses natively, but requires
a separate compile step.

Initial setup:

1. Install [node](https://nodejs.org/download/release/latest-v12.x/)
2. Run `npm install -g yarn`
3. Run `yarn`

Each time you modify a file, run the following command
to compile the Svelte into a .js file in dist/:

```
% yarn run build
yarn run v1.22.10
$ node buildscript.js
✨  Done in 0.25s.
```

The `__init__.py` file is also copied to dist/, so the dist
folder can be copied into your add-ons folder to be used.
