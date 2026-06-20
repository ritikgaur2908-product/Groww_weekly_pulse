import ThemeCard from './ThemeCard'

export default function Dashboard({ report }) {
  const period = `${new Date(report.start_date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})} - ${new Date(report.end_date).toLocaleDateString('en-US', {month: 'short', day: 'numeric'})}`;
  
  const stats = report.stats || { total_reviews: 0, average_rating: 0 };
  const ratingDist = report.rating_distribution || { stars_5: 0, stars_4: 0, stars_3: 0, stars_2: 0, stars_1: 0 };

  const bars = [
    { stars: 5, percentage: ratingDist.stars_5 },
    { stars: 4, percentage: ratingDist.stars_4 },
    { stars: 3, percentage: ratingDist.stars_3 },
    { stars: 2, percentage: ratingDist.stars_2 },
    { stars: 1, percentage: ratingDist.stars_1 },
  ];

  return (
    <main className="ml-64 flex-1 h-full overflow-y-auto p-container-padding bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-surface-container-high/40 via-background to-background fade-transition" id="main-content">
      <header className="mb-12">
        <h1 className="font-display-lg text-display-lg font-extrabold text-on-surface mb-2">
          Pulse Report: <span id="report-title-app">{report.product_name}</span> <span className="text-primary/70" id="report-title-period">({period})</span>
        </h1>
      </header>
      
      <section className="grid grid-cols-1 md:grid-cols-3 gap-card-gap mb-12">
        <div className="glass-card p-6 flex flex-col justify-between hover:shadow-[0_0_20px_rgba(0,208,156,0.1)] transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <span className="font-label-md text-label-md text-on-surface-variant">Total Reviews</span>
            <span className="material-symbols-outlined text-primary">forum</span>
          </div>
          <div className="flex items-end gap-3">
            <span className="font-headline-lg text-headline-lg text-on-surface">{stats.total_reviews.toLocaleString()}</span>
          </div>
        </div>
        
        <div className="glass-card p-6 flex flex-col justify-between hover:shadow-[0_0_20px_rgba(0,208,156,0.1)] transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <span className="font-label-md text-label-md text-on-surface-variant">Average Rating</span>
            <span className="material-symbols-outlined text-secondary">star</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-headline-lg text-headline-lg text-on-surface">{stats.average_rating.toFixed(1)}</span>
            <span className="font-headline-md text-headline-md text-on-surface-variant">/5</span>
          </div>
        </div>

        <div className="glass-card p-6 flex flex-col justify-between hover:shadow-[0_0_20px_rgba(0,208,156,0.1)] transition-shadow">
          <div className="flex justify-between items-start mb-4">
            <span className="font-label-md text-label-md text-on-surface-variant">Total Themes</span>
            <span className="material-symbols-outlined text-primary-container">category</span>
          </div>
          <div className="flex items-end">
            <span className="font-headline-lg text-headline-lg text-primary-container">{report.themes.length}</span>
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-gutter flex-col">
        <section className="glass-card p-8 self-start">
          <h3 className="font-headline-md text-headline-md text-on-surface mb-6 border-b border-white/10 pb-4">Rating Distribution</h3>
          <div className="space-y-5">
            {bars.map(item => (
              <div key={item.stars} className="flex items-center gap-4">
                <div className="flex items-center gap-1 w-12 justify-end">
                    <span className="font-label-md text-label-md text-on-surface">{item.stars}</span>
                    <span className="material-symbols-outlined text-surface-variant text-sm" style={{fontVariationSettings: "'FILL' 1"}}>star</span>
                </div>
                <div className="flex-1 h-3 bg-surface-variant rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-secondary-container to-primary-container rounded-full" style={{width: `${item.percentage}%`}}></div>
                </div>
                <span className="w-12 text-right font-label-md text-label-md text-on-surface-variant">{item.percentage.toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-6">
          <div className="flex justify-between items-end mb-2">
            <h2 className="font-headline-lg text-headline-lg text-on-surface">Key Themes</h2>
            <span className="font-label-md text-label-md text-on-surface-variant bg-surface-variant/50 px-3 py-1 rounded-full border border-white/5">Auto-categorized by AI</span>
          </div>
          <div className="space-y-4">
            {report.themes?.map((theme, index) => (
              <ThemeCard key={theme.cluster_id || index} theme={theme} isFirst={index === 0} />
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}
