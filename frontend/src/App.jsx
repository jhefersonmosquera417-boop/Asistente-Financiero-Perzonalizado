import { useState } from 'react'
import AsistenteFinancieroInteligente from './components/AsistenteFinancieroInteligente'
import DashboardFinanciero from './pages/DashboardFinanciero'
import './components/AsistenteFinancieroInteligente.css'
import './pages/DashboardFinanciero.css'

function App() {
  const [showDashboard, setShowDashboard] = useState(false)
  const [dashboardData, setDashboardData] = useState(null)

  const handleCompleteAdvanced = (data) => {
    setDashboardData(data)
    setShowDashboard(true)
  }

  const handleCloseDashboard = () => {
    setShowDashboard(false)
    setDashboardData(null)
  }

  return (
    <div className="app">
      {!showDashboard ? (
        <AsistenteFinancieroInteligente onBack={undefined} onComplete={handleCompleteAdvanced} />
      ) : (
        <DashboardFinanciero data={dashboardData} onBack={handleCloseDashboard} />
      )}
    </div>
  )
}

export default App
