
const TextField = ({ label, value, onChange, placeholder }) => (
  <div className="mb-2">
    <label className="form-label fw-semibold">{label}</label>
    <input
      className="form-control form-control-sm"
      type="text"
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  </div>
);

const TextArea = ({ label, value, onChange, rows = 4, placeholder }) => (
  <div className="mb-2">
    <label className="form-label fw-semibold">{label}</label>
    <textarea
      className="form-control form-control-sm"
      rows={rows}
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  </div>
);

function CustomSectionEditorSingle({ index, data, setData, onDelete }) {
  const sec = (Array.isArray(data.custom_sections) ? data.custom_sections : [])[index]
           ?? { label: "Custom", type: "rich", items: [] };

  const updateSection = (updater) => {
    setData(prev => {
      const arr = Array.isArray(prev.custom_sections) ? [...prev.custom_sections] : [];
      const cur = arr[index] ?? { label: "Custom", type: "rich", items: [] };
      const nextSec = typeof updater === "function" ? updater(cur) : updater;
      arr[index] = nextSec;
      return { ...prev, custom_sections: arr };
    });
  };

  const setField = (k, v) => updateSection(cur => ({ ...cur, [k]: v }));

  const addItem = () =>
    updateSection(cur => ({
      ...cur,
      items: [...(cur.items || []), { title: "", date: "", description: "" }],
    }));

  const rmItem = (idx) =>
    updateSection(cur => {
      const items = [...(cur.items || [])];
      items.splice(idx, 1);
      return { ...cur, items };
    });

  const setItemField = (idx, k, v) =>
    updateSection(cur => {
      const items = [...(cur.items || [])];
      const base = items[idx] ?? { title: "", date: "", description: "" };
      items[idx] = { ...base, [k]: v };
      return { ...cur, items };
    });

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-2">
        <button className="btn btn-sm btn-outline-danger" onClick={onDelete}>Remove section</button>
      </div>

      {/* Make sure to use your renamed component, e.g. TextField (not Text) */}
      <TextField
        label="Section name"
        value={sec.label ?? ""}
        onChange={(v) => setField("label", v)}
      />

      <div className="d-flex align-items-center justify-content-between mt-2 mb-1">
        <label className="form-label fw-semibold m-0">Items</label>
        <button className="btn btn-sm btn-outline-primary" onClick={addItem}>+ Add item</button>
      </div>

      {(sec.items || []).map((it, idx) => (
        <div key={idx} className="border rounded-3 p-2 mb-2">
          <TextField label="Title" value={it.title ?? ""} onChange={(v) => setItemField(idx, "title", v)} />
          <TextField label="Date" value={it.date ?? ""} onChange={(v) => setItemField(idx, "date", v)} />
          <TextArea  label="Description" value={it.description ?? ""} onChange={(v) => setItemField(idx, "description", v)} rows={3} />
          <div className="text-end">
            <button className="btn btn-sm btn-outline-danger" onClick={() => rmItem(idx)}>Remove item</button>
          </div>
        </div>
      ))}
    </div>
  );
} export default CustomSectionEditorSingle;
