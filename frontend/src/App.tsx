import { useState } from 'react';
import './App.css';
import { ProvaUpload } from './components/ProvaUpload';

function App() {
  const [modo, setModo] = useState<'gabarito' | 'redacao'>('gabarito');

  return (
    <div className="container">
      <h1>🚀 AnalisaEdu <span style={{fontSize: '0.5em', color: '#888'}}>SaaS Municipal</span></h1>
      
      <div className="tabs" style={{ marginBottom: '20px' }}>
        <button 
            onClick={() => setModo('gabarito')}
            style={{ opacity: modo === 'gabarito' ? 1 : 0.5, marginRight: '10px' }}
        >
            Objetiva (OMR)
        </button>
        <button 
            onClick={() => setModo('redacao')}
            style={{ opacity: modo === 'redacao' ? 1 : 0.5 }}
        >
            Redação (IA)
        </button>
      </div>

      <ProvaUpload modo={modo} />
    </div>
  );
}

export default App;