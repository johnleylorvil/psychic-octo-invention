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
import PatientDetail from './pages/admin/PatientDetail';
import AppointmentsList from './pages/admin/AppointmentsList';
import AppointmentForm from './pages/admin/AppointmentForm';
import PharmacyPage from './pages/admin/PharmacyPage';
import BillingPage from './pages/admin/BillingPage';
import BloodBankPage from './pages/admin/BloodBankPage';
import DonneurForm from './pages/admin/DonneurForm';
import ServicesLitsPage from './pages/admin/ServicesLitsPage';
import ServiceForm from './pages/admin/ServiceForm';
import LitForm from './pages/admin/LitForm';
import UsersPage from './pages/admin/UsersPage';
import UserForm from './pages/admin/UserForm';
import FactureForm from './pages/admin/FactureForm';

// Doctor pages
import MedecinDashboard from './pages/doctor/MedecinDashboard';
import MedecinPatientsList from './pages/doctor/MedecinPatientsList';
import MedecinAppointmentsList from './pages/doctor/MedecinAppointmentsList';
import MedecinConsultationsList from './pages/doctor/MedecinConsultationsList';
import MedecinConsultationForm from './pages/doctor/MedecinConsultationForm';
import MedecinPrescriptionsList from './pages/doctor/MedecinPrescriptionsList';
import MedecinPrescriptionForm from './pages/doctor/MedecinPrescriptionForm';

// Nurse pages
import InfirmiereDashboard from './pages/nurse/InfirmiereDashboard';
import InfirmierePatientsList from './pages/nurse/InfirmierePatientsList';
import InfirmiereAppointmentsList from './pages/nurse/InfirmiereAppointmentsList';
import InfirmiereLitsPage from './pages/nurse/InfirmiereLitsPage';
import InfirmiereBloodBankPage from './pages/nurse/InfirmiereBloodBankPage';

// Pharmacist pages
import PharmacienDashboard from './pages/pharmacist/PharmacienDashboard';
import PharmacienMedicamentsList from './pages/pharmacist/PharmacienMedicamentsList';
import PharmacienStocksPage from './pages/pharmacist/PharmacienStocksPage';
import PharmacienPrescriptionsList from './pages/pharmacist/PharmacienPrescriptionsList';

// Accountant pages
import ComptableDashboard from './pages/accountant/ComptableDashboard';
import ComptableFacturesList from './pages/accountant/ComptableFacturesList';
import ComptablePaiementsList from './pages/accountant/ComptablePaiementsList';

// Patient pages
import PatientDashboard from './pages/patient/PatientDashboard';
import PatientAppointmentsList from './pages/patient/PatientAppointmentsList';
import PatientConsultationsList from './pages/patient/PatientConsultationsList';
import PatientFacturesList from './pages/patient/PatientFacturesList';

import { ROLES } from './utils/constants';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* ADMIN ROUTES */}
          <Route path="/admin" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/patients" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PatientsList /></ProtectedRoute>} />
          <Route path="/admin/patients/new" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PatientForm /></ProtectedRoute>} />
          <Route path="/admin/patients/:id/edit" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PatientForm /></ProtectedRoute>} />
          <Route path="/admin/patients/:id" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PatientDetail /></ProtectedRoute>} />
          <Route path="/admin/appointments" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AppointmentsList /></ProtectedRoute>} />
          <Route path="/admin/appointments/new" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AppointmentForm /></ProtectedRoute>} />
          <Route path="/admin/appointments/:id/edit" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><AppointmentForm /></ProtectedRoute>} />
          <Route path="/admin/pharmacy" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><PharmacyPage /></ProtectedRoute>} />
          <Route path="/admin/billing" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><BillingPage /></ProtectedRoute>} />
          <Route path="/admin/billing/new" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><FactureForm /></ProtectedRoute>} />
          <Route path="/admin/blood-bank" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><BloodBankPage /></ProtectedRoute>} />
          <Route path="/admin/blood-bank/donneurs/new" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><DonneurForm /></ProtectedRoute>} />
          <Route path="/admin/blood-bank/donneurs/:id/edit" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><DonneurForm /></ProtectedRoute>} />
          <Route path="/admin/services" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><ServicesLitsPage /></ProtectedRoute>} />
          <Route path="/admin/services/new" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><ServiceForm /></ProtectedRoute>} />
          <Route path="/admin/services/lits/new" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><LitForm /></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><UsersPage /></ProtectedRoute>} />
          <Route path="/admin/users/new" element={<ProtectedRoute allowedRoles={[ROLES.ADMIN]}><UserForm /></ProtectedRoute>} />

          {/* MÉDECIN ROUTES */}
          <Route path="/medecin" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinDashboard /></ProtectedRoute>} />
          <Route path="/medecin/patients" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinPatientsList /></ProtectedRoute>} />
          <Route path="/medecin/appointments" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinAppointmentsList /></ProtectedRoute>} />
          <Route path="/medecin/consultations" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinConsultationsList /></ProtectedRoute>} />
          <Route path="/medecin/consultations/new" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinConsultationForm /></ProtectedRoute>} />
          <Route path="/medecin/prescriptions" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinPrescriptionsList /></ProtectedRoute>} />
          <Route path="/medecin/prescriptions/new" element={<ProtectedRoute allowedRoles={[ROLES.MEDECIN]}><MedecinPrescriptionForm /></ProtectedRoute>} />

          {/* INFIRMIÈRE ROUTES */}
          <Route path="/infirmiere" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><InfirmiereDashboard /></ProtectedRoute>} />
          <Route path="/infirmiere/patients" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><InfirmierePatientsList /></ProtectedRoute>} />
          <Route path="/infirmiere/appointments" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><InfirmiereAppointmentsList /></ProtectedRoute>} />
          <Route path="/infirmiere/lits" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><InfirmiereLitsPage /></ProtectedRoute>} />
          <Route path="/infirmiere/blood-bank" element={<ProtectedRoute allowedRoles={[ROLES.INFIRMIERE]}><InfirmiereBloodBankPage /></ProtectedRoute>} />

          {/* PHARMACIEN ROUTES */}
          <Route path="/pharmacien" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><PharmacienDashboard /></ProtectedRoute>} />
          <Route path="/pharmacien/medicaments" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><PharmacienMedicamentsList /></ProtectedRoute>} />
          <Route path="/pharmacien/stocks" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><PharmacienStocksPage /></ProtectedRoute>} />
          <Route path="/pharmacien/prescriptions" element={<ProtectedRoute allowedRoles={[ROLES.PHARMACIEN]}><PharmacienPrescriptionsList /></ProtectedRoute>} />

          {/* COMPTABLE ROUTES */}
          <Route path="/comptable" element={<ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}><ComptableDashboard /></ProtectedRoute>} />
          <Route path="/comptable/factures" element={<ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}><ComptableFacturesList /></ProtectedRoute>} />
          <Route path="/comptable/factures/new" element={<ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}><FactureForm /></ProtectedRoute>} />
          <Route path="/comptable/paiements" element={<ProtectedRoute allowedRoles={[ROLES.COMPTABLE]}><ComptablePaiementsList /></ProtectedRoute>} />

          {/* PATIENT ROUTES */}
          <Route path="/patient" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><PatientDashboard /></ProtectedRoute>} />
          <Route path="/patient/appointments" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><PatientAppointmentsList /></ProtectedRoute>} />
          <Route path="/patient/consultations" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><PatientConsultationsList /></ProtectedRoute>} />
          <Route path="/patient/factures" element={<ProtectedRoute allowedRoles={[ROLES.PATIENT]}><PatientFacturesList /></ProtectedRoute>} />

          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
