import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Edit, User, Calendar, Stethoscope } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';

const PatientDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [consultations, setConsultations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, [id]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pRes, aRes, cRes] = await Promise.all([
        api.get(`/patients/${id}`),
        api.get('/appointments', { params: { patient_id: id } }),
        api.get('/consultations', { params: { patient_id: id } })
      ]);
      setPatient(pRes.data);
      setAppointments(aRes.data);
      setConsultations(cRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <MainLayout><div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div></div></MainLayout>;
  }

  if (!patient) {
    return <MainLayout><p className="text-center text-gray-500 py-12">Patient introuvable</p></MainLayout>;
  }

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="patient-detail-page">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/admin/patients')} className="p-2 hover:bg-gray-100 rounded-lg transition-colors" data-testid="back-btn"><ArrowLeft className="w-5 h-5" /></button>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Dossier {patient.numero_dossier}</h2>
              <p className="text-gray-600 mt-1">Détails du patient</p>
            </div>
          </div>
          <button onClick={() => navigate(`/admin/patients/${id}/edit`)} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium flex items-center space-x-2 shadow-lg" data-testid="edit-patient-btn">
            <Edit className="w-5 h-5" /><span>Modifier</span>
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-4 mb-6">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-sky-500 to-emerald-500 flex items-center justify-center text-white"><User className="w-8 h-8" /></div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{patient.numero_dossier}</h3>
              {patient.groupe_sanguin && <Badge variant="info">{patient.groupe_sanguin}</Badge>}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex justify-between border-b border-gray-100 py-2"><span className="text-gray-600">Sexe</span><span className="font-medium">{patient.sexe}</span></div>
            <div className="flex justify-between border-b border-gray-100 py-2"><span className="text-gray-600">Date de naissance</span><span className="font-medium">{new Date(patient.date_naissance).toLocaleDateString('fr-FR')}</span></div>
            <div className="flex justify-between border-b border-gray-100 py-2"><span className="text-gray-600">Adresse</span><span className="font-medium">{patient.adresse || 'N/A'}</span></div>
            <div className="flex justify-between border-b border-gray-100 py-2"><span className="text-gray-600">Contact urgence</span><span className="font-medium">{patient.contact_urgence_nom || 'N/A'} {patient.contact_urgence_tel || ''}</span></div>
            <div className="flex justify-between border-b border-gray-100 py-2"><span className="text-gray-600">Allergies</span><span className="font-medium text-red-600">{patient.allergies || 'Aucune'}</span></div>
            <div className="flex justify-between border-b border-gray-100 py-2"><span className="text-gray-600">Historique médical</span><span className="font-medium">{patient.historique_medical || 'N/A'}</span></div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center"><Calendar className="w-5 h-5 mr-2 text-sky-600" />Rendez-vous ({appointments.length})</h3>
            {appointments.length === 0 ? <p className="text-sm text-gray-500">Aucun rendez-vous</p> : (
              <div className="space-y-2">
                {appointments.slice(0, 8).map(a => (
                  <div key={a.id} className="flex items-center justify-between text-sm border-b border-gray-100 py-2">
                    <span>{new Date(a.date_rdv).toLocaleDateString('fr-FR')}</span>
                    <Badge variant="info">{a.statut}</Badge>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center"><Stethoscope className="w-5 h-5 mr-2 text-emerald-600" />Consultations ({consultations.length})</h3>
            {consultations.length === 0 ? <p className="text-sm text-gray-500">Aucune consultation</p> : (
              <div className="space-y-2">
                {consultations.slice(0, 8).map(c => (
                  <div key={c.id} className="text-sm border-b border-gray-100 py-2">
                    <p className="font-medium text-gray-900">{c.motif}</p>
                    <p className="text-gray-500 text-xs">{new Date(c.date_consultation).toLocaleDateString('fr-FR')} · {c.diagnostic || 'Sans diagnostic'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default PatientDetail;
