import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Calendar, Video, User } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';

const InfirmiereAppointmentsList = () => {
  const [appointments, setAppointments] = useState([]);
  const [patients, setPatients] = useState({});
  const [medecins, setMedecins] = useState({});
  const [loading, setLoading] = useState(true);
  const [filterStatut, setFilterStatut] = useState('');

  useEffect(() => { loadData(); }, [filterStatut]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterStatut) params.statut = filterStatut;
      const [aRes, pRes, mRes] = await Promise.all([
        api.get('/appointments', { params }),
        api.get('/patients'),
        api.get('/users?role=médecin')
      ]);
      setAppointments(aRes.data);
      const pMap = {}; pRes.data.forEach(p => { pMap[p.id] = p; }); setPatients(pMap);
      const mMap = {}; mRes.data.forEach(m => { mMap[m.id] = m; }); setMedecins(mMap);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const getVariant = (s) => ({ 'planifié': 'info', 'confirmé': 'success', 'terminé': 'default', 'annulé': 'error', 'en_attente': 'warning' }[s] || 'default');

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="infirmiere-appointments-page">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Rendez-vous</h2>
          <p className="text-gray-600 mt-1">Planning des consultations de la clinique</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Statut :</label>
            <select value={filterStatut} onChange={(e) => setFilterStatut(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
              data-testid="statut-filter">
              <option value="">Tous</option>
              <option value="planifié">Planifié</option>
              <option value="confirmé">Confirmé</option>
              <option value="terminé">Terminé</option>
              <option value="annulé">Annulé</option>
            </select>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : appointments.length === 0 ? (
            <p className="text-center text-gray-500 py-12">Aucun rendez-vous</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date & Heure</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Médecin</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {appointments.map((rdv) => (
                    <tr key={rdv.id} className="hover:bg-gray-50" data-testid={`appointment-row-${rdv.id}`}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="font-medium text-gray-900">{new Date(rdv.date_rdv).toLocaleDateString('fr-FR')}</div>
                        <div className="text-gray-500">{new Date(rdv.date_rdv).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{patients[rdv.patient_id]?.numero_dossier || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center"><User className="w-4 h-4 text-gray-400 mr-2" />Dr. {medecins[rdv.medecin_id]?.nom || 'N/A'}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {rdv.type_rdv === 'en_ligne' ? (
                          <span className="flex items-center text-purple-600"><Video className="w-4 h-4 mr-1" />En ligne</span>
                        ) : 'Présentiel'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap"><Badge variant={getVariant(rdv.statut)}>{rdv.statut}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default InfirmiereAppointmentsList;
