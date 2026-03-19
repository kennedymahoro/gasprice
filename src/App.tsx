import { CountyMap } from './components/CountyMap';
import './index.css';

function App() {
  return (
    <div className="app-container">
      <header className="header">
        <h1>US Gas Prices</h1>
        <p className="subtitle">Interactive county-level price map</p>
      </header>
      
      <main className="main-content">
        <div className="map-panel">
          <CountyMap />
        </div>
        
        <div className="legend-panel">
          <h3>National Average Regular Gas Price</h3>
          <div className="legend-scale">
            <span className="legend-label">$2.00</span>
            <div className="color-gradient"></div>
            <span className="legend-label">$5.00+</span>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
