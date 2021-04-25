function setup(options) {
  const store = options.auxData();
  const boolInput = document.getElementById("myBool");
  const numberInput = document.getElementById("myNumber");

  // update html when state changes
  store.subscribe((data) => {
    boolInput.checked = data["myBoolKey"];
    numberInput.value = data["myNumberKey"];

    // and show current data for debugging
    document.getElementById("myDebug").innerText = JSON.stringify(
      data,
      null,
      4
    );
  });

  // update config when check state changes
  boolInput.addEventListener("change", (_) =>
    store.update((data) => {
      return { ...data, myBoolKey: boolInput.checked };
    })
  );
  numberInput.addEventListener("change", (_) => {
    let number = 0;
    try {
      number = parseInt(numberInput.value, 10);
    } catch (err) {}

    return store.update((data) => {
      return { ...data, myNumberKey: number };
    });
  });
}

$deckOptions.then((options) => {
  options.addHtmlAddon(HTML_CONTENT, () => setup(options));
});
