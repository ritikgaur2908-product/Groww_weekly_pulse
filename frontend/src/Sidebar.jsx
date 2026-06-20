export default function Sidebar({ reports, selectedReportId, onSelect, onCreateReport }) {
  return (
    <aside className="fixed left-0 top-0 h-full w-64 border-r border-white/10 bg-surface/80 backdrop-blur-xl shadow-2xl flex flex-col p-base z-50">
      <div className="mb-4 p-4">
        <h1 className="font-display-lg text-display-lg font-extrabold text-primary tracking-tighter text-[32px] leading-tight">Pulse</h1>
      </div>
      <div className="px-4 mb-4">
        <button 
          onClick={onCreateReport}
          className="w-full bg-primary-container text-on-primary-container font-label-md text-label-md py-3 rounded-lg font-bold hover:opacity-90 transition-opacity flex items-center justify-center gap-2">
          <span className="material-symbols-outlined">add</span>
          Create Report
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-2">
        {reports.map((report) => {
          const isActive = report.id === selectedReportId;
          const activeClasses = isActive
            ? 'bg-primary/10 text-primary shadow-[0_0_20px_rgba(68,237,183,0.1)] border-r-2 border-primary'
            : 'text-on-surface-variant hover:bg-white/5 hover:text-on-surface border-r-2 border-transparent';
          
          return (
            <button 
              key={report.id}
              className={`w-full text-left flex flex-col gap-1 px-4 py-3 rounded-lg font-medium transition-all duration-300 mb-1 ${activeClasses}`}
              onClick={() => onSelect(report.id)}
            >
              <span className={`font-label-md text-label-md ${isActive ? 'text-primary font-bold' : 'text-on-surface'}`}>{report.product_name}</span>
              <span className="font-label-sm text-label-sm opacity-80">
                {new Date(report.start_date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})} - {new Date(report.end_date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}
              </span>
            </button>
          )
        })}
      </div>
      <div className="mt-auto pt-4 border-t border-white/10">
        <div className="flex items-center gap-3 px-4 pb-4">
          <div className="w-10 h-10 rounded-full bg-surface-variant border border-white/10 flex items-center justify-center overflow-hidden">
            <span className="material-symbols-outlined text-on-surface-variant">person</span>
          </div>
          <div>
            <p className="font-label-md text-label-md text-on-surface">Pulse Report</p>
            <p className="font-label-sm text-label-sm text-on-surface-variant">Premium Analytics</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
