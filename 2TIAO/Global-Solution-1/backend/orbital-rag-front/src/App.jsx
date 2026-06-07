import { useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { ChatOrbital } from './components/ChatOrbital';

function App() {
  // O estado começa mostrando o dashboard
  const [telaAtiva, setTelaAtiva] = useState('dashboard');

  return (
    <div style={{ fontFamily: 'sans-serif' }}>
      {/* Menu Superior MOCKADO */}
      <nav style={{ 
  backgroundColor: '#0b3d91', 
  padding: '10px 40px', 
  color: 'white', 
  display: 'flex', 
  gap: '30px', 
  alignItems: 'center',
  borderBottom: '4px solid #fc3d21' // O famoso detalhe vermelho da NASA
}}>
  <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 'bold', letterSpacing: '2px' }}>ORBITAL RAG</h1>
  <button onClick={() => setTelaAtiva('dashboard')} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', textTransform: 'uppercase', fontSize: '14px' }}>Dashboard</button>
  <button onClick={() => setTelaAtiva('chat')} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', textTransform: 'uppercase', fontSize: '14px' }}>Centro de Comando</button>
</nav>

      {/* O React vai renderizar apenas a tela escolhida aqui embaixo */}
      <main>
        {telaAtiva === 'dashboard' && <Dashboard />}
        {telaAtiva === 'chat' && <ChatOrbital />}
      </main>
    </div>
  );
}

export default App;