import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Stethoscope } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const PatientConsultationsList = () => {
  const { user } = useAuth();
  const [consultations, setConsultations] = useState([]);
  const [medecins, setMedecins] = useState({});
  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const patientsRes = await api.get('/patients');
      const myPatient = patientsRes.data.find(p => p.user_id === user.id);
      setPatientData(myPatient);

      if (myPatient) {
        const [consultationsRes, medecinsRes] = await Promise.all([
          api.get('/consultations', { params: { patient_id: myPatient.id } }),
          api.get('/users?role=médecin')
        ]);
        
        setConsultations(consultationsRes.data);
        
        const medecinsMap = {};
        medecinsRes.data.forEach(m => { medecinsMap[m.id] = m; });
        setMedecins(medecinsMap);
      }
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Mes consultations</h2>
          <p className="text-gray-600 mt-1">Historique de vos consultations médicales</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : consultations.length === 0 ? (
            <div className="text-center py-12">
              <Stethoscope className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune consultation</p>
            </div>
          ) : (
            <div className="p-6 space-y-4">
              {consultations.map((consultation) => {
                const medecin = medecins[consultation.medecin_id];
                return (
                  <div key={consultation.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div className="flex items-center space-x-3 mb-2">
                          <Stethoscope className="w-5 h-5 text-sky-600" />
                          <span className="text-lg font-semibold text-gray-900">
                            {new Date(consultation.date_consultation).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600">
                          Dr. {medecin?.nom} {medecin?.prenom} {medecin?.specialite && `- ${medecin.specialite}`}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {consultation.motif && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Motif de consultation</h4>
                          <p className="text-sm text-gray-600">{consultation.motif}</p>
                        </div>
                      )}

                      {consultation.symptomes && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Symptômes</h4>
                          <p className="text-sm text-gray-600">{consultation.symptomes}</p>
                        </div>
                      )}

                      {consultation.diagnostic && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Diagnostic</h4>
                          <p className="text-sm text-gray-600">{consultation.diagnostic}</p>
                        </div>
                      )}

                      {consultation.traitement && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Traitement prescrit</h4>
                          <p className="text-sm text-gray-600">{consultation.traitement}</p>
                        </div>
                      )}

                      {consultation.examens_demandes && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Examens demandés</h4>
                          <p className="text-sm text-gray-600">{consultation.examens_demandes}</p>
                        </div>
                      )}

                      {consultation.notes && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Notes</h4>
                          <p className="text-sm text-gray-600">{consultation.notes}</p>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default PatientConsultationsList;