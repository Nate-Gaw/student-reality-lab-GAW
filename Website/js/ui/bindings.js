export function wireBindings(selectors, handlers) {
  const { onRecompute, onStartExplore, onCompareScenario } = handlers;

  const rangeKeys = Object.keys(selectors.ranges);

  rangeKeys.forEach((key) => {
    const range = selectors.ranges[key];
    const number = selectors.numbers[key];

    if (range) {
      range.addEventListener('input', () => {
        if (number) number.value = range.value;
        onRecompute();
      });
    }

    if (number && range) {
      number.addEventListener('input', () => {
        const raw = number.value.replace(/[^0-9.-]/g, '');
        const numeric = Number(raw || 0);
        const min = Number(range.min);
        const max = Number(range.max);
        const clamped = Math.max(min, Math.min(max, numeric));
        range.value = clamped;
        onRecompute();
      });
    }
  });

  Object.values(selectors.selects).forEach((element) => {
    if (element) element.addEventListener('change', onRecompute);
  });

  Object.values(selectors.toggles).forEach((element) => {
    if (element) element.addEventListener('change', onRecompute);
  });

  if (selectors.actions.startExplore) {
    selectors.actions.startExplore.addEventListener('click', onStartExplore);
  }

  if (selectors.actions.compareScenario) {
    selectors.actions.compareScenario.addEventListener('click', onCompareScenario);
  }
}
