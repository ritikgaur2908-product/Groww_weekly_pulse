import { useState, useEffect } from 'react'
import Sidebar from './Sidebar'
import Dashboard from './Dashboard'
import CreateReportModal from './CreateReportModal'
import './index.css'

function App() {
  const [reports, setReports] = useState([])
  const [selectedReportId, setSelectedReportId] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [modalScenario, setModalScenario] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const fetchReports = () => {
    fetch(`${API_BASE_URL}/api/reports`)
      .then(res => res.json())
      .then(data => {
        setReports(data)
        if (data.length > 0 && !selectedReportId) {
          setSelectedReportId(data[0].id)
        }
      })
      .catch(err => console.error("Error fetching reports", err))
  }

  useEffect(() => {
    fetchReports()
  }, [])

  const handleCreateReportClick = () => {
    const now = new Date()
    const day = now.getDay() // 0 is Sunday, 1 is Monday, etc.
    const hours = now.getHours()

    if (day !== 1) {
      setModalScenario('A')
    } else if (hours < 8) {
      setModalScenario('B')
    } else {
      setModalScenario('C')
    }
    setIsModalOpen(true)
  }

  const handleProceed = async () => {
    setIsGenerating(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/reports/generate`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error("Failed to generate report")
      
      fetch(`${API_BASE_URL}/api/reports`)
        .then(res => res.json())
        .then(data => {
          setReports(data)
          if (data.length > 0) setSelectedReportId(data[0].id)
          setIsModalOpen(false)
          setIsGenerating(false)
        })
    } catch (err) {
      console.error(err)
      setIsGenerating(false)
      alert("Failed to generate report")
    }
  }

  const selectedReport = reports.find(r => r.id === selectedReportId)

  return (
    <div className="bg-background text-on-surface h-screen overflow-hidden flex font-body-md text-body-md relative">
      <Sidebar 
        reports={reports} 
        selectedReportId={selectedReportId} 
        onSelect={setSelectedReportId} 
        onCreateReport={handleCreateReportClick}
      />
      
      {selectedReport ? (
        <Dashboard report={selectedReport} />
      ) : (
        <main className="ml-64 flex-1 h-full flex items-center justify-center bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-surface-container-high/40 via-background to-background">
          <p className="text-on-surface-variant font-label-md">Loading reports...</p>
        </main>
      )}

      <CreateReportModal 
        isOpen={isModalOpen}
        scenario={modalScenario}
        isGenerating={isGenerating}
        onClose={() => setIsModalOpen(false)}
        onProceed={handleProceed}
      />
    </div>
  )
}

export default App
