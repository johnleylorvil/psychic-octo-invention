import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { FileText, Plus } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const MedecinPrescriptionsList = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [prescriptions, setPrescriptions] = useState([]);
  const [patients, setPatients] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [prescriptionsRes, patientsRes] = await Promise.all([
        api.get('/consultations/prescriptions', { params: { medecin_id: user.id } }),
        api.get('/patients')
      ]);
      
      setPrescriptions(prescriptionsRes.data);
      
      const patientsMap = {};
      patientsRes.data.forEach(p => { patientsMap[p.id] = p; });
      setPatients(patientsMap);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Mes prescriptions</h2>
            <p className="text-gray-600 mt-1">Ordonnances émises</p>
          </div>
          <button
            onClick={() => navigate('/medecin/prescriptions/new')}
            className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
          >
            <Plus className="w-5 h-5" />
            <span>Nouvelle prescription</span>
          </button>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : prescriptions.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune prescription</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
              {prescriptions.map((prescription) => {
                const patient = patients[prescription.patient_id];
                return (
                  <div key={prescription.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-5 h-5 text-sky-600" />
                        <span className="text-sm font-semibold text-gray-900">
                          {new Date(prescription.created_at).toLocaleDateString('fr-FR')}
                        </span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Patient:</span>
                        <span className="font-medium text-gray-900">{patient?.numero_dossier || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Médicaments:</span>
                        <span className="font-medium text-gray-900">{prescription.medicaments?.length || 0}</span>
                      </div>
                      {prescription.instructions_generales && (
                        <p className="text-xs text-gray-500 mt-2 line-clamp-2">
                          {prescription.instructions_generales}
                        </p>
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

export default MedecinPrescriptionsList;