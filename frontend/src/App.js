import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import LoginPage from './pages/auth/LoginPage';
import AdminDashboard from './pages/admin/AdminDashboard';
import MedecinDashboard from './pages/doctor/MedecinDashboard';
import PatientDashboard from './pages/patient/PatientDashboard';
import { ROLES } from './utils/constants';

// Composant simple pour les autres dashboards (à développer plus tard)
const SimpleDashboard = ({ title }) => {
  const MainLayout = require('./components/Layout/MainLayout').default;
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600">Tableau de bord en développement</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
          <p className="text-gray-600">
            Cette section sera bientôt disponible. Utilisez le menu de navigation pour accéder aux autres fonctionnalités.
          </p>
        </div>
      </div>
    </MainLayout>
  );
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <SimpleDashboard title="Administration" />
              </ProtectedRoute>
            }
          />
          
          {/* Médecin Routes */}
          <Route
            path="/medecin"
            element={
              <ProtectedRoute allowedRoles={[ROLES.MEDECIN]}>
                <MedecinDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/medecin/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.MEDECIN]}>
                <SimpleDashboard title="Espace Médecin" />
              </ProtectedRoute>
            }
          />
          
          {/* Infirmière Routes */}
          <Route
            path="/infirmiere/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}>
                <SimpleDashboard title="Espace Infirmière" />
              </ProtectedRoute>
            }
          />
          
          {/* Pharmacien Routes */}
          <Route
            path="/pharmacien/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}>
                <SimpleDashboard title="Espace Pharmacien" />
              </ProtectedRoute>
            }
          />
          
          {/* Comptable Routes */}
          <Route
            path="/comptable/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}>
                <SimpleDashboard title="Espace Comptable" />
              </ProtectedRoute>
            }
          />
          
          {/* Patient Routes */}
          <Route
            path="/patient"
            element={
              <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
                <PatientDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/patient/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.PATIENT]}>
                <SimpleDashboard title="Mon Espace" />
              </ProtectedRoute>
            }
          />
          
          {/* Default Route */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
