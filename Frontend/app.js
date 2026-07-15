async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  if (!res.ok) {
    const txt = await res.text();
    throw new Error(txt || res.statusText);
  }
  return res.json();
}

async function loadItems() {
  const items = await api('/inventory');
  const tbody = document.querySelector('#items-table tbody');
  tbody.innerHTML = '';
  for (const it of items) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${it.id}</td>
      <td><input data-id="${it.id}" data-field="name" value="${escapeHtml(it.name)}"></td>
      <td><input data-id="${it.id}" data-field="sku" value="${escapeHtml(it.sku)}"></td>
      <td><input data-id="${it.id}" data-field="quantity" type="number" value="${it.quantity}"></td>
      <td><input data-id="${it.id}" data-field="price" type="number" step="0.01" value="${it.price}"></td>
      <td>
        <button data-action="save" data-id="${it.id}">Save</button>
        <button data-action="delete" data-id="${it.id}">Delete</button>
      </td>`;
    tbody.appendChild(tr);
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('create-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    payload.quantity = Number(payload.quantity);
    payload.price = Number(payload.price);
    await api('/inventory', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    form.reset();
    await loadItems();
  });

  document.querySelector('#items-table').addEventListener('click', async (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    const id = btn.dataset.id;
    const action = btn.dataset.action;
    if (action === 'delete') {
      await api(`/inventory/${id}`, {method: 'DELETE'});
      await loadItems();
      return;
    }
    if (action === 'save') {
      const row = btn.closest('tr');
      const inputs = row.querySelectorAll('input[data-field]');
      const payload = {};
      inputs.forEach(i => {
        const f = i.dataset.field;
        payload[f] = (f === 'quantity' || f === 'price') ? Number(i.value) : i.value;
      });
      await api(`/inventory/${id}`, {method: 'PATCH', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
      await loadItems();
    }
  });

  loadItems().catch(err => console.error(err));
});
