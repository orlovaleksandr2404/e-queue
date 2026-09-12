import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import TerminalPage from './pages/TerminalPage';
import BoardPage from './pages/BoardPage';
import OperatorPage from './pages/OperatorPage';
import AdminPage from './pages/AdminPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/terminal" replace />} />
        <Route path="/terminal" element={<TerminalPage />} />
        <Route path="/board" element={<BoardPage />} />
        <Route path="/operator" element={<OperatorPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </BrowserRouter>
  );
}
