import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Plus, Calendar, Video, User } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { STATUT_RDV } from '../../utils/constants';

const AppointmentsList = () => {
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState({});
  const [medecins, setMedecins] = useState({});
  const [loading, setLoading] = useState(true);
  const [filterStatut, setFilterStatut] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, [filterStatut]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterStatut) params.statut = filterStatut;
      
      const [appointmentsRes, patientsRes, medecinsRes] = await Promise.all([
        api.get('/appointments', { params }),
        api.get('/patients'),
        api.get('/users?role=médecin')
      ]);
      
      setAppointments(appointmentsRes.data);
      
      // Créer des maps pour accès rapide
      const patientsMap = {};
      patientsRes.data.forEach(p => { patientsMap[p.id] = p; });
      setPatients(patientsMap);
      
      const medecinsMap = {};
      medecinsRes.data.forEach(m => { medecinsMap[m.id] = m; });
      setMedecins(medecinsMap);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatutVariant = (statut) => {
    const variants = {
      'planifié': 'info',
      'confirmé': 'success',
      'terminé': 'default',
      'annulé': 'error',
      'en_attente': 'warning'
    };
    return variants[statut] || 'default';
  };

  const getStatutLabel = (statut) => {
    const labels = {
      'planifié': 'Planifié',
      'confirmé': 'Confirmé',
      'terminé': 'Terminé',
      'annulé': 'Annulé',
      'en_attente': 'En attente'
    };
    return labels[statut] || statut;
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Rendez-vous</h2>
            <p className="text-gray-600 mt-1">Gestion des rendez-vous</p>
          </div>
          <button
            onClick={() => navigate('/admin/appointments/new')}
            className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
            data-testid="add-appointment-btn"
          >
            <Plus className="w-5 h-5" />
            <span>Nouveau rendez-vous</span>
          </button>
        </div>

        {/* Filtre */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Statut :</label>
            <select
              value={filterStatut}
              onChange={(e) => setFilterStatut(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            >
              <option value="">Tous les statuts</option>
              <option value="planifié">Planifié</option>
              <option value="confirmé">Confirmé</option>
              <option value="terminé">Terminé</option>
              <option value="annulé">Annulé</option>
              <option value="en_attente">En attente</option>
            </select>
          </div>
        </div>

        {/* Liste */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : appointments.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucun rendez-vous trouvé</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date & Heure
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Patient
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Médecin
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Motif
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {appointments.map((rdv) => {
                    const patient = patients[rdv.patient_id];
                    const medecin = medecins[rdv.medecin_id];
                    
                    return (
                      <tr key={rdv.id} className="hover:bg-gray-50 transition-colors" data-testid={`appointment-row-${rdv.id}`}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {new Date(rdv.date_rdv).toLocaleDateString('fr-FR')}
                              </div>
                              <div className="text-sm text-gray-500">
                                {new Date(rdv.date_rdv).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{patient?.numero_dossier || 'N/A'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <User className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-sm text-gray-900">
                              Dr. {medecin?.nom || 'N/A'}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {rdv.type_rdv === 'en_ligne' ? (
                            <div className="flex items-center text-purple-600">
                              <Video className="w-4 h-4 mr-1" />
                              <span className="text-sm">En ligne</span>
                            </div>
                          ) : (
                            <span className="text-sm text-gray-600">Présentiel</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={getStatutVariant(rdv.statut)}>
                            {getStatutLabel(rdv.statut)}
                          </Badge>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-600 max-w-xs truncate">
                            {rdv.motif || 'Non spécifié'}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-sm text-gray-600">
            Total : <span className="font-semibold text-gray-900">{appointments.length}</span> rendez-vous
          </p>
        </div>
      </div>
    </MainLayout>
  );
};

export default AppointmentsList;