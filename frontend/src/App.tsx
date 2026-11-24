import React, { useState } from 'react';
import { useAuth } from './contexts/AuthContext';
import { Navbar } from './components/layout/Navbar';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { WorkspacePage } from './pages/WorkspacePage';
import { DocumentsPage } from './pages/DocumentsPage';
import { AssistantPage } from './pages/AssistantPage';
import { GraphPage } from './pages/GraphPage';
import { ContradictionsPage } from './pages/ContradictionsPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  const { user, loading } = useAuth();
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [authView, setAuthView] = useState<'landing' | 'login' | 'register'>('landing');

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">
        Initializing EvidenceGraph AI...
      </div>
    );
  }

  // Unauthenticated routing
  if (!user) {
    if (authView === 'login') {
      return (
        <LoginPage
          onSwitchToRegister={() => setAuthView('register')}
          onSuccess={() => setCurrentPage('dashboard')}
        />
      );
    }
    if (authView === 'register') {
      return (
        <RegisterPage
          onSwitchToLogin={() => setAuthView('login')}
          onSuccess={() => setCurrentPage('dashboard')}
        />
      );
    }
    return (
      <LandingPage
        onGetStarted={() => setAuthView('register')}
        onLogin={() => setAuthView('login')}
      />
    );
  }

  // Authenticated Workspace routing
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="flex-1">
        {currentPage === 'dashboard' && <DashboardPage onNavigate={setCurrentPage} />}
        {currentPage === 'workspace' && <WorkspacePage onNavigate={setCurrentPage} />}
        {currentPage === 'documents' && <DocumentsPage />}
        {currentPage === 'assistant' && <AssistantPage />}
        {currentPage === 'graph' && <GraphPage />}
        {currentPage === 'contradictions' && <ContradictionsPage />}
        {currentPage === 'reports' && <ReportsPage />}
        {currentPage === 'settings' && <SettingsPage />}
      </main>
    </div>
  );
};
export default App;
