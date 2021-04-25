import MyAddon from "./addon.svelte";

$deckOptions.then((options) => {
  options.addSvelteAddon({ component: MyAddon });
});
