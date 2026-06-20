export default function CreateReportModal({ isOpen, scenario, onClose, onProceed, isGenerating }) {
  if (!isOpen) return null;

  let title = "";
  let message = "";
  let showProceed = false;

  if (scenario === 'A') {
    title = "Confirm Ad-hoc Report";
    message = "Since the report is set to be created every Monday and you want it to be created now, it will consider reviews of the past 8 weeks up until today.";
    showProceed = true;
  } else if (scenario === 'B') {
    title = "Report Scheduled";
    message = "Please wait till 8:00 AM as the report is scheduled to be created at 8:00 AM.";
    showProceed = false;
  } else if (scenario === 'C') {
    title = "Report Already Created";
    message = "Report created today. No new reviews to analyze. Please wait for at least a day.";
    showProceed = false;
  }

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-surface border border-white/10 rounded-2xl shadow-2xl p-6 w-[400px] max-w-[90vw]">
        <h2 className="text-xl font-bold text-on-surface mb-3">{title}</h2>
        <p className="text-on-surface-variant mb-6 text-sm">{message}</p>
        
        <div className="flex justify-end gap-3">
          <button 
            onClick={onClose}
            disabled={isGenerating}
            className="px-4 py-2 rounded border border-white/10 text-on-surface hover:bg-white/5 transition"
          >
            {showProceed ? "Cancel" : "Close"}
          </button>
          
          {showProceed && (
            <button 
              onClick={onProceed}
              disabled={isGenerating}
              className="px-4 py-2 rounded bg-primary text-black font-bold hover:opacity-90 transition flex items-center gap-2 disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>
                  Generating...
                </>
              ) : "Proceed"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
