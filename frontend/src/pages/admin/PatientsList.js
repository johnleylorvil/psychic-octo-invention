import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Plus, Search, Edit, Eye } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { GROUPES_SANGUINS } from '../../utils/constants';

const PatientsList = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterSexe, setFilterSexe] = useState('');
  const [filterGroupe, setFilterGroupe] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadPatients();
  }, [filterSexe, filterGroupe]);

  const loadPatients = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterSexe) params.sexe = filterSexe;
      if (filterGroupe) params.groupe_sanguin = filterGroupe;
      
      const response = await api.get('/patients', { params });
      setPatients(response.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredPatients = patients.filter(patient => {
    if (!search) return true;
    const searchLower = search.toLowerCase();
    return (
      patient.numero_dossier.toLowerCase().includes(searchLower)
    );
  });

  const getGroupeSanguinVariant = (groupe) => {
    if (groupe?.includes('+')) return 'success';
    return 'warning';
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Patients</h2>
            <p className="text-gray-600 mt-1">Gestion des dossiers patients</p>
          </div>
          <button
            onClick={() => navigate('/admin/patients/new')}
            className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
            data-testid="add-patient-btn"
          >
            <Plus className="w-5 h-5" />
            <span>Nouveau patient</span>
          </button>
        </div>

        {/* Filtres */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher par numéro de dossier..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  data-testid="search-input"
                />
              </div>
            </div>
            <div>
              <select
                value={filterSexe}
                onChange={(e) => setFilterSexe(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="">Tous les sexes</option>
                <option value="M">Masculin</option>
                <option value="F">Féminin</option>
                <option value="Autre">Autre</option>
              </select>
            </div>
            <div>
              <select
                value={filterGroupe}
                onChange={(e) => setFilterGroupe(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="">Tous les groupes sanguins</option>
                {GROUPES_SANGUINS.map(g => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Liste des patients */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : filteredPatients.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">Aucun patient trouvé</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Numéro dossier
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sexe
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Groupe sanguin
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date naissance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Téléphone
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredPatients.map((patient) => (
                    <tr key={patient.id} className="hover:bg-gray-50 transition-colors" data-testid={`patient-row-${patient.id}`}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{patient.numero_dossier}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-600">{patient.sexe}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {patient.groupe_sanguin ? (
                          <Badge variant={getGroupeSanguinVariant(patient.groupe_sanguin)}>
                            {patient.groupe_sanguin}
                          </Badge>
                        ) : (
                          <span className="text-sm text-gray-400">Non spécifié</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(patient.date_naissance).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {patient.contact_urgence_tel || 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => navigate(`/admin/patients/${patient.id}`)}
                          className="text-sky-600 hover:text-sky-900 mr-3"
                          data-testid={`view-patient-${patient.id}`}
                        >
                          <Eye className="w-5 h-5 inline" />
                        </button>
                        <button
                          onClick={() => navigate(`/admin/patients/${patient.id}/edit`)}
                          className="text-emerald-600 hover:text-emerald-900"
                          data-testid={`edit-patient-${patient.id}`}
                        >
                          <Edit className="w-5 h-5 inline" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">
            Total : <span className="font-semibold text-gray-900">{filteredPatients.length}</span> patient(s)
          </p>
        </div>
      </div>
    </MainLayout>
  );
};

export default PatientsList;