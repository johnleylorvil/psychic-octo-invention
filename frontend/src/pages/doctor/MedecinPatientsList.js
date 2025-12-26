import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Users, User, Calendar } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const MedecinPatientsList = () => {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      // Récupérer tous les patients (le médecin peut voir tous les patients)
      const response = await api.get('/patients');
      setPatients(response.data);
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
          <h2 className="text-2xl font-bold text-gray-900">Mes patients</h2>
          <p className="text-gray-600 mt-1">Liste des patients de la clinique</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Users className="w-6 h-6 text-sky-600" />
              <h3 className="text-lg font-semibold text-gray-900">Total : {patients.length} patients</h3>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : patients.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucun patient</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {patients.map((patient) => (
                <div key={patient.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sky-500 to-emerald-500 flex items-center justify-center text-white font-semibold flex-shrink-0">
                      <User className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-semibold text-gray-900 truncate">{patient.numero_dossier}</p>
                        {patient.groupe_sanguin && (
                          <Badge variant="info" className="ml-2">{patient.groupe_sanguin}</Badge>
                        )}
                      </div>
                      <div className="space-y-1 text-xs text-gray-600">
                        <p>Sexe: {patient.sexe}</p>
                        <p>Né(e) le: {new Date(patient.date_naissance).toLocaleDateString('fr-FR')}</p>
                        {patient.allergies && (
                          <p className="text-red-600">⚠️ Allergies: {patient.allergies}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default MedecinPatientsList;