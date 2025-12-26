import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Toaster } from './components/ui/sonner';
import ProtectedRoute from './components/common/ProtectedRoute';
import LoginPage from './pages/auth/LoginPage';

// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard';
import PatientsList from './pages/admin/PatientsList';
import PatientForm from './pages/admin/PatientForm';
import AppointmentsList from './pages/admin/AppointmentsList';
import AppointmentForm from './pages/admin/AppointmentForm';
import PharmacyPage from './pages/admin/PharmacyPage';
import BillingPage from './pages/admin/BillingPage';

// Doctor pages
import MedecinDashboard from './pages/doctor/MedecinDashboard';

// Patient pages
import PatientDashboard from './pages/patient/PatientDashboard';

import { ROLES } from './utils/constants';
import MainLayout from './components/Layout/MainLayout';

// Composant simple pour les pages en développement
const ComingSoon = ({ title, description }) => {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600">{description}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <div className="max-w-md mx-auto">
            <div className="w-20 h-20 bg-gradient-to-br from-sky-100 to-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🚧</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">En développement</h3>
            <p className="text-gray-600">
              Cette fonctionnalité est en cours de développement. Elle sera bientôt disponible.
            </p>
          </div>
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
          
          {/* ===== ADMIN ROUTES ===== */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          
          {/* Patients */}
          <Route
            path="/admin/patients"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <PatientsList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/patients/new"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <PatientForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/patients/:id/edit"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <PatientForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/patients/:id"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <ComingSoon title="Détails du patient" description="Vue détaillée du dossier patient" />
              </ProtectedRoute>
            }
          />
          
          {/* Rendez-vous */}
          <Route
            path="/admin/appointments"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <AppointmentsList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/appointments/new"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <AppointmentForm />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/appointments/:id/edit"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <AppointmentForm />
              </ProtectedRoute>
            }
          />
          
          {/* Pharmacie */}
          <Route
            path="/admin/pharmacy"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <PharmacyPage />
              </ProtectedRoute>
            }
          />
          
          {/* Facturation */}
          <Route
            path="/admin/billing"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <BillingPage />
              </ProtectedRoute>
            }
          />
          
          {/* Utilisateurs */}
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <ComingSoon title="Utilisateurs" description="Gestion des utilisateurs et rôles" />
              </ProtectedRoute>
            }
          />
          
          {/* Services & Lits */}
          <Route
            path="/admin/services"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <ComingSoon title="Services & Lits" description="Gestion des services et lits d'hospitalisation" />
              </ProtectedRoute>
            }
          />
          
          {/* Banque de sang */}
          <Route
            path="/admin/blood-bank"
            element={
              <ProtectedRoute allowedRoles={[ROLES.ADMIN]}>
                <ComingSoon title="Banque de sang" description="Gestion des donneurs et stocks de sang" />
              </ProtectedRoute>
            }
          />
          
          {/* ===== MÉDECIN ROUTES ===== */}
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
                <ComingSoon title="Espace Médecin" description="Consultations et prescriptions" />
              </ProtectedRoute>
            }
          />
          
          {/* ===== INFIRMIÈRE ROUTES ===== */}
          <Route
            path="/infirmiere"
            element={
              <ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}>
                <ComingSoon title="Tableau de bord" description="Espace infirmière" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/infirmiere/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}>
                <ComingSoon title="Espace Infirmière" description="Gestion des soins et admissions" />
              </ProtectedRoute>
            }
          />
          
          {/* ===== PHARMACIEN ROUTES ===== */}
          <Route
            path="/pharmacien"
            element={
              <ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}>
                <ComingSoon title="Tableau de bord" description="Espace pharmacien" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/pharmacien/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}>
                <ComingSoon title="Espace Pharmacien" description="Gestion des médicaments" />
              </ProtectedRoute>
            }
          />
          
          {/* ===== COMPTABLE ROUTES ===== */}
          <Route
            path="/comptable"
            element={
              <ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}>
                <ComingSoon title="Tableau de bord" description="Espace comptable" />
              </ProtectedRoute>
            }
          />
          <Route
            path="/comptable/*"
            element={
              <ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}>
                <ComingSoon title="Espace Comptable" description="Facturation et finances" />
              </ProtectedRoute>
            }
          />
          
          {/* ===== PATIENT ROUTES ===== */}
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
                <ComingSoon title="Mon Espace" description="Mes rendez-vous et consultations" />
              </ProtectedRoute>
            }
          />
          
          {/* Default Routes */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
        
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
