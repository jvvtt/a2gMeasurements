import './App.css'
import { MapToInteract } from './components/MapToInteract'
import { MapProvider } from './context/map'
import { InfoCanvas } from './components/InfoCanvas'

function App() {

  return (
    <MapProvider>
      <header className='header-app'>
        <h1>Wireless Channel Measurements Planner</h1>
        <img src="assets/vtt-logo.png" alt="VTT logo" />
      </header>
      <div className='body-content'>
      <section className='open-info'>
        <h2>Place the coordinates in the order the transceiver will follow</h2>
      </section>
      <MapToInteract></MapToInteract>
      <InfoCanvas></InfoCanvas>
      </div>
    </MapProvider>
  )
}

export default App
