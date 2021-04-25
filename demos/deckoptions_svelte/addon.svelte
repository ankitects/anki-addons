<script>
  const {
    SpinBox,
    SpinBoxFloat,
    EnumSelector,
    CheckBox,
  } = anki.deckConfigComponents;

  export let data;

  const defaults = {
    myNumber: 5,
    myFloat: 3.14,
    myBool: true,
    myEnum: 1,
  };

  // add default values when data changes
  $: {
    const updated = Object.assign({ ...defaults }, data);
    // avoid updating if nothing has changed
    if (JSON.stringify(updated) != JSON.stringify(data)) {
      data = updated;
    }
  }
</script>

<div>This is some text.</div>

<SpinBox
  label="my number"
  tooltip="extra help"
  defaultValue={defaults.myNumber}
  bind:value={data.myNumber}
/>

<SpinBoxFloat
  label="my float"
  tooltip="tooltip"
  min={2}
  max={5}
  defaultValue={defaults.myFloat}
  value={data.myFloat}
  on:changed={(evt) => {
    data = { ...data, myFloat: evt.detail.value };
  }}
/>

<EnumSelector
  label="select something"
  tooltip="tooltip"
  choices={["choice 1", "choice 2", "choice 3"]}
  defaultValue={defaults.myEnum}
  bind:value={data.myEnum}
/>

<CheckBox
  label="my checkbox"
  defaultValue={true}
  bind:value={data["myBool"]}
/>

Debug info:
<div style="white-space: pre-wrap;">{JSON.stringify(data, null, 4)}</div>
