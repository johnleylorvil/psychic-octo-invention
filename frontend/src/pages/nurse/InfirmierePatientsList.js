import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Users, Search, User } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';

const InfirmierePatientsList = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => { loadPatients(); }, []);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const response = await api.get('/patients');
      setPatients(response.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const filtered = patients.filter(p =>
    !search || p.numero_dossier?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="infirmiere-patients-page">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Patients</h2>
          <p className="text-gray-600 mt-1">Dossiers patients de la clinique</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par numéro de dossier..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              data-testid="patient-search-input"
            />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Users className="w-6 h-6 text-sky-600" />
            <h3 className="text-lg font-semibold text-gray-900">Total : {filtered.length} patients</h3>
          </div>
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : filtered.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Aucun patient</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filtered.map((patient) => (
                <div key={patient.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow" data-testid={`patient-card-${patient.id}`}>
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-sky-500 to-emerald-500 flex items-center justify-center text-white flex-shrink-0">
                      <User className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-semibold text-gray-900 truncate">{patient.numero_dossier}</p>
                        {patient.groupe_sanguin && <Badge variant="info">{patient.groupe_sanguin}</Badge>}
                      </div>
                      <div className="space-y-1 text-xs text-gray-600">
                        <p>Sexe : {patient.sexe}</p>
                        <p>Né(e) le : {new Date(patient.date_naissance).toLocaleDateString('fr-FR')}</p>
                        {patient.allergies && <p className="text-red-600">Allergies : {patient.allergies}</p>}
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

export default InfirmierePatientsList;
