import { useState } from 'react'

export default function ThemeCard({ theme, isFirst }) {
  const [isOpen, setIsOpen] = useState(isFirst)
  const [activeTab, setActiveTab] = useState('actions')

  const icon = theme.icon || 'category'

  return (
    <div className="glass-card overflow-hidden transition-all duration-300">
      <button 
        className="w-full text-left p-6 flex justify-between items-center hover:bg-white/5 transition-colors" 
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary">{icon}</span>
          </div>
          <h3 className="font-headline-md text-headline-md text-on-surface">{theme.theme_name}</h3>
        </div>
        <span className="material-symbols-outlined text-on-surface-variant transform transition-transform duration-300">
          {isOpen ? 'expand_less' : 'expand_more'}
        </span>
      </button>
      
      {isOpen && (
        <div className="px-6 pb-6 animate-fadeIn">
          <div className="bg-surface-variant/30 border border-white/5 rounded-xl p-5 mb-6">
            <p className="font-body-md text-body-md text-on-surface-variant leading-relaxed">
              <span className="font-bold text-on-surface mr-2">Summary:</span>
              {theme.theme_summary}
            </p>
          </div>

          <div className="border-b border-white/10 flex gap-6 mb-6">
            <button 
              className={`font-label-md text-label-md pb-2 border-b-2 transition-colors ${activeTab === 'actions' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('actions')}
            >
              Actions
            </button>
            <button 
              className={`font-label-md text-label-md pb-2 border-b-2 transition-colors ${activeTab === 'reviews' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant hover:text-on-surface'}`}
              onClick={() => setActiveTab('reviews')}
            >
              Reviews
            </button>
          </div>

          {activeTab === 'actions' && (
            <div className="animate-fadeIn">
              <ul className="space-y-3">
                {theme.action_ideas?.map((action, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="material-symbols-outlined text-secondary-container text-lg mt-0.5">check_circle</span>
                    <span className="font-body-md text-body-md text-on-surface">{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {activeTab === 'reviews' && (
            <div className="animate-fadeIn">
              <div className="space-y-4">
                {theme.quotes?.map((quote, i) => (
                  <div key={i} className="bg-surface/50 border border-white/5 p-4 rounded-lg">
                    <p className="font-body-md text-body-md text-on-surface-variant italic">"{quote}"</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
