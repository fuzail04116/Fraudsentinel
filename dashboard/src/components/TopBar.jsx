export default function TopBar({ title }) {
  const dateStr = new Intl.DateTimeFormat('en-US', { 
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
  }).format(new Date());

  return (
    <div className="topbar">
      <div>
        <h1 className="topbar-title">{title}</h1>
        <div className="topbar-date">{dateStr}</div>
      </div>
      <div className="live-badge">
        <div className="live-dot"></div> Live
      </div>
    </div>
  );
}
