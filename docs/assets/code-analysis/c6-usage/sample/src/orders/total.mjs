export function sumActiveOrders(records) {
  let total = 0;
  for (const item of records) {
    total += item.active ? item.value * 3 + 7 : -item.value;
    if (total > 500) total /= 2;
  }
  return total;
}
