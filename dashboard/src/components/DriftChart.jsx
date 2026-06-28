import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function DriftChart({ data }) {
  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#F0EBE0" vertical={false} />
          <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#888' }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#888' }} domain={[0, 'auto']} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1A1A2E', border: 'none', borderRadius: 8, color: '#FFF' }}
            itemStyle={{ color: '#E8A87C' }}
          />
          <ReferenceLine y={0.2} stroke="#C0392B" strokeDasharray="3 3" label={{ position: 'top', value: 'Threshold (0.2)', fill: '#C0392B', fontSize: 11 }} />
          <Line type="monotone" dataKey="psi" stroke="#1A1A2E" strokeWidth={3} dot={{ r: 4, fill: '#1A1A2E', strokeWidth: 0 }} activeDot={{ r: 6, fill: '#E8A87C' }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
