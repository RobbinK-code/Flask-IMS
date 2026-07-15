async function request(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json();
}

function InventoryForm({ onCreated }) {
  const [values, setValues] = React.useState({ name: '', sku: '', quantity: 1, price: 0.0 });

  const handleChange = (event) => {
    const { name, value } = event.target;
    setValues((prev) => ({
      ...prev,
      [name]: name === 'quantity' || name === 'price' ? Number(value) : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    await request('/inventory', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(values),
    });
    setValues({ name: '', sku: '', quantity: 1, price: 0.0 });
    onCreated();
  };

  return (
    <section className="card form-card">
      <div className="section-header">
        <h2>Add Item</h2>
      </div>
      <form className="form-grid" onSubmit={handleSubmit}>
        <label>
          Name
          <input name="name" value={values.name} onChange={handleChange} required />
        </label>
        <label>
          SKU
          <input name="sku" value={values.sku} onChange={handleChange} required />
        </label>
        <label>
          Quantity
          <input name="quantity" type="number" min="1" value={values.quantity} onChange={handleChange} required />
        </label>
        <label>
          Price
          <input name="price" type="number" min="0" step="0.01" value={values.price} onChange={handleChange} required />
        </label>
        <button className="primary-button" type="submit">Add Item</button>
      </form>
    </section>
  );
}

function InventoryTable({ items, onDelete, onUpdate }) {
  const [drafts, setDrafts] = React.useState({});

  React.useEffect(() => {
    const initialDrafts = items.reduce((acc, item) => {
      acc[item.id] = item;
      return acc;
    }, {});
    setDrafts(initialDrafts);
  }, [items]);

  const handleChange = (id, field, value) => {
    setDrafts((prev) => ({
      ...prev,
      [id]: { ...prev[id], [field]: field === 'quantity' || field === 'price' ? Number(value) : value },
    }));
  };

  return (
    <section className="card table-card">
      <div className="section-header">
        <h2>Items</h2>
      </div>
      <div className="table-scroll">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>SKU</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>
                  <input value={drafts[item.id]?.name || ''} onChange={(event) => handleChange(item.id, 'name', event.target.value)} />
                </td>
                <td>
                  <input value={drafts[item.id]?.sku || ''} onChange={(event) => handleChange(item.id, 'sku', event.target.value)} />
                </td>
                <td>
                  <input type="number" min="0" value={drafts[item.id]?.quantity || 0} onChange={(event) => handleChange(item.id, 'quantity', event.target.value)} />
                </td>
                <td>
                  <input type="number" min="0" step="0.01" value={drafts[item.id]?.price || 0} onChange={(event) => handleChange(item.id, 'price', event.target.value)} />
                </td>
                <td className="actions-cell">
                  <button className="secondary-button" onClick={() => onUpdate(item.id, drafts[item.id])} type="button">Save</button>
                  <button className="danger-button" onClick={() => onDelete(item.id)} type="button">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const [items, setItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(null);

  const fetchItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await request('/inventory');
      setItems(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchItems();
  }, []);

  const handleDelete = async (id) => {
    await request(`/inventory/${id}`, { method: 'DELETE' });
    fetchItems();
  };

  const handleUpdate = async (id, item) => {
    await request(`/inventory/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item),
    });
    fetchItems();
  };

  const headerButtons = React.useMemo(
    () => (
      <div className="hero-actions">
        <a className="link-button" href="/inventory">View API</a>
        <button className="secondary-button" type="button" onClick={fetchItems}>Refresh</button>
      </div>
    ),
    [fetchItems]
  );

  return (
    <div className="app-shell">
      <header className="hero-card">
        <div>
          <p className="eyebrow">Flask IMS</p>
          <h1>Inventory management in React</h1>
          <p className="subtitle">Use the Flask backend API to create, edit, and delete inventory items.</p>
        </div>
        {headerButtons}
      </header>

      {error && <div className="alert">{error}</div>}
      <InventoryForm onCreated={fetchItems} />
      {loading ? <div className="loading">Loading inventory...</div> : <InventoryTable items={items} onDelete={handleDelete} onUpdate={handleUpdate} />}
    </div>
  );
}

const rootElement = document.getElementById('root');
const root = ReactDOM.createRoot(rootElement);
root.render(<App />);
