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
import BloodBankPage from './pages/admin/BloodBankPage';
import DonneurForm from './pages/admin/DonneurForm';
import ServicesLitsPage from './pages/admin/ServicesLitsPage';
import UsersPage from './pages/admin/UsersPage';
import UserForm from './pages/admin/UserForm';

// Doctor pages
import MedecinDashboard from './pages/doctor/MedecinDashboard';

// Nurse pages
import InfirmiereDashboard from './pages/nurse/InfirmiereDashboard';

// Pharmacist pages
import PharmacienDashboard from './pages/pharmacist/PharmacienDashboard';

// Accountant pages
import ComptableDashboard from './pages/accountant/ComptableDashboard';

// Patient pages
import PatientDashboard from './pages/patient/PatientDashboard';

import { ROLES } from './utils/constants';
import MainLayout from './components/Layout/MainLayout';

// Composant pour pages en développement
const ComingSoon = ({ title, description }) => {
  return (
    <MainLayout>
      <div className=\"space-y-6\">
        <div>
          <h2 className=\"text-2xl font-bold text-gray-900 mb-2\">{title}</h2>
          <p className=\"text-gray-600\">{description}</p>
        </div>
        <div className=\"bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center\">
          <div className=\"max-w-md mx-auto\">
            <div className=\"w-20 h-20 bg-gradient-to-br from-sky-100 to-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4\">
              <span className=\"text-3xl\">🚧</span>
            </div>
            <h3 className=\"text-xl font-semibold text-gray-900 mb-2\">En développement</h3>
            <p className=\"text-gray-600\">
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
          <Route path=\"/login\" element={<LoginPage />} />
          
          {/* ===== ADMIN ROUTES ===== */}
          <Route path=\"/admin\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AdminDashboard /></ProtectedRoute>} />
          
          {/* Patients */}
          <Route path=\"/admin/patients\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PatientsList /></ProtectedRoute>} />
          <Route path=\"/admin/patients/new\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PatientForm /></ProtectedRoute>} />
          <Route path=\"/admin/patients/:id/edit\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PatientForm /></ProtectedRoute>} />
          <Route path=\"/admin/patients/:id\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><ComingSoon title=\"Détails du patient\" description=\"Vue détaillée du dossier patient\" /></ProtectedRoute>} />
          
          {/* Rendez-vous */}
          <Route path=\"/admin/appointments\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AppointmentsList /></ProtectedRoute>} />
          <Route path=\"/admin/appointments/new\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AppointmentForm /></ProtectedRoute>} />
          <Route path=\"/admin/appointments/:id/edit\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AppointmentForm /></ProtectedRoute>} />
          
          {/* Pharmacie */}
          <Route path=\"/admin/pharmacy\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PharmacyPage /></ProtectedRoute>} />
          
          {/* Facturation */}
          <Route path=\"/admin/billing\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><BillingPage /></ProtectedRoute>} />
          
          {/* Banque de sang */}
          <Route path=\"/admin/blood-bank\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><BloodBankPage /></ProtectedRoute>} />
          <Route path=\"/admin/blood-bank/donneurs/new\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><DonneurForm /></ProtectedRoute>} />
          <Route path=\"/admin/blood-bank/donneurs/:id/edit\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><DonneurForm /></ProtectedRoute>} />
          
          {/* Services & Lits */}
          <Route path=\"/admin/services\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><ServicesLitsPage /></ProtectedRoute>} />
          <Route path=\"/admin/services/new\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><ComingSoon title=\"Nouveau service\" description=\"Créer un service\" /></ProtectedRoute>} />
          <Route path=\"/admin/services/lits/new\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><ComingSoon title=\"Nouveau lit\" description=\"Ajouter un lit\" /></ProtectedRoute>} />
          
          {/* Utilisateurs */}
          <Route path=\"/admin/users\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><UsersPage /></ProtectedRoute>} />
          <Route path=\"/admin/users/new\" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><UserForm /></ProtectedRoute>} />
          
          {/* ===== MÉDECIN ROUTES ===== */}
          <Route path=\"/medecin\" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinDashboard /></ProtectedRoute>} />
          <Route path=\"/medecin/patients\" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><ComingSoon title=\"Mes patients\" description=\"Liste de vos patients\" /></ProtectedRoute>} />
          <Route path=\"/medecin/appointments\" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><ComingSoon title=\"Mes rendez-vous\" description=\"Vos consultations\" /></ProtectedRoute>} />
          <Route path=\"/medecin/consultations\" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><ComingSoon title=\"Consultations\" description=\"Historique des consultations\" /></ProtectedRoute>} />
          <Route path=\"/medecin/prescriptions\" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><ComingSoon title=\"Prescriptions\" description=\"Vos prescriptions\" /></ProtectedRoute>} />
          
          {/* ===== INFIRMIÈRE ROUTES ===== */}
          <Route path=\"/infirmiere\" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><InfirmiereDashboard /></ProtectedRoute>} />
          <Route path=\"/infirmiere/patients\" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><ComingSoon title=\"Patients\" description=\"Dossiers patients\" /></ProtectedRoute>} />
          <Route path=\"/infirmiere/appointments\" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><ComingSoon title=\"Rendez-vous\" description=\"Gestion des rendez-vous\" /></ProtectedRoute>} />
          <Route path=\"/infirmiere/lits\" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><ComingSoon title=\"Gestion des lits\" description=\"Admissions et libérations\" /></ProtectedRoute>} />
          <Route path=\"/infirmiere/blood-bank\" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><ComingSoon title=\"Banque de sang\" description=\"Gestion des stocks de sang\" /></ProtectedRoute>} />
          
          {/* ===== PHARMACIEN ROUTES ===== */}
          <Route path=\"/pharmacien\" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><PharmacienDashboard /></ProtectedRoute>} />
          <Route path=\"/pharmacien/medicaments\" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><ComingSoon title=\"Médicaments\" description=\"Catalogue des médicaments\" /></ProtectedRoute>} />
          <Route path=\"/pharmacien/stocks\" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><ComingSoon title=\"Stocks\" description=\"Gestion des stocks\" /></ProtectedRoute>} />
          <Route path=\"/pharmacien/prescriptions\" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><ComingSoon title=\"Prescriptions\" description=\"Ordonnances à préparer\" /></ProtectedRoute>} />
          
          {/* ===== COMPTABLE ROUTES ===== */}
          <Route path=\"/comptable\" element={<ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}><ComptableDashboard /></ProtectedRoute>} />
          <Route path=\"/comptable/factures\" element={<ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}><ComingSoon title=\"Factures\" description=\"Gestion des factures\" /></ProtectedRoute>} />
          <Route path=\"/comptable/paiements\" element={<ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}><ComingSoon title=\"Paiements\" description=\"Suivi des paiements\" /></ProtectedRoute>} />
          
          {/* ===== PATIENT ROUTES ===== */}
          <Route path=\"/patient\" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><PatientDashboard /></ProtectedRoute>} />
          <Route path=\"/patient/appointments\" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><ComingSoon title=\"Mes rendez-vous\" description=\"Historique de vos rendez-vous\" /></ProtectedRoute>} />
          <Route path=\"/patient/consultations\" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><ComingSoon title=\"Mes consultations\" description=\"Résultats de consultations\" /></ProtectedRoute>} />
          <Route path=\"/patient/factures\" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><ComingSoon title=\"Mes factures\" description=\"Vos factures et paiements\" /></ProtectedRoute>} />
          
          {/* Default Routes */}
          <Route path=\"/\" element={<Navigate to=\"/login\" replace />} />
          <Route path=\"*\" element={<Navigate to=\"/login\" replace />} />
        </Routes>
        
        <Toaster position=\"top-right\" richColors />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
