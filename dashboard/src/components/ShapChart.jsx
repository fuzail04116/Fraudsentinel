import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function ShapChart({ shapData }) {
  if (!shapData || Object.keys(shapData).length === 0) return <div>No SHAP data available for this prediction.</div>;
  
  const data = Object.entries(shapData).map(([feature, value]) => ({
    feature,
    value: Number(value)
  })).sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 5);

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F0EBE0" horizontal={true} vertical={false} />
          <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#888' }} />
          <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#1A1A2E', fontWeight: 600 }} />
          <Tooltip cursor={{fill: 'transparent'}} contentStyle={{ borderRadius: 8 }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.value > 0 ? '#C0392B' : '#27AE60'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 16, fontSize: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 12, height: 12, backgroundColor: '#C0392B', borderRadius: 2 }}></div> Increases Fraud Prob
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 12, height: 12, backgroundColor: '#27AE60', borderRadius: 2 }}></div> Decreases Fraud Prob
        </div>
      </div>
    </div>
  );
}
