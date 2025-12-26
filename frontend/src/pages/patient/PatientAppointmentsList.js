import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Calendar, Video, Clock } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const PatientAppointmentsList = () => {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [medecins, setMedecins] = useState({});
  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      // Récupérer le patient associé à l'utilisateur
      const patientsRes = await api.get('/patients');
      const myPatient = patientsRes.data.find(p => p.user_id === user.id);
      setPatientData(myPatient);

      if (myPatient) {
        const [appointmentsRes, medecinsRes] = await Promise.all([
          api.get('/appointments', { params: { patient_id: myPatient.id } }),
          api.get('/users?role=médecin')
        ]);
        
        setAppointments(appointmentsRes.data);
        
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

  // Séparer les RDV à venir et passés
  const now = new Date().toISOString();
  const appointmentsUpcoming = appointments.filter(a => a.date_rdv >= now && a.statut !== 'annulé');
  const appointmentsPast = appointments.filter(a => a.date_rdv < now || a.statut === 'terminé');

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Mes rendez-vous</h2>
          <p className="text-gray-600 mt-1">Planning de vos consultations</p>
        </div>

        {/* RDV à venir */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Calendar className="w-6 h-6 text-sky-600" />
            <h3 className="text-lg font-semibold text-gray-900">Prochains rendez-vous ({appointmentsUpcoming.length})</h3>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : appointmentsUpcoming.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Aucun rendez-vous à venir</p>
          ) : (
            <div className="space-y-3">
              {appointmentsUpcoming.map((rdv) => {
                const medecin = medecins[rdv.medecin_id];
                return (
                  <div key={rdv.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex flex-col">
                          <span className="text-sm font-semibold text-gray-900">
                            {new Date(rdv.date_rdv).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
                          </span>
                          <div className="flex items-center space-x-2 mt-1">
                            <Clock className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-600">
                              {new Date(rdv.date_rdv).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                            </span>
                          </div>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-sm text-gray-600">Médecin</span>
                          <span className="text-sm font-medium text-gray-900">
                            Dr. {medecin?.nom} {medecin?.prenom}
                          </span>
                          {medecin?.specialite && (
                            <span className="text-xs text-gray-500">{medecin.specialite}</span>
                          )}
                        </div>
                        {rdv.type_rdv === 'en_ligne' && (
                          <div className="flex items-center space-x-1 text-purple-600">
                            <Video className="w-4 h-4" />
                            <span className="text-xs">Téléconsultation</span>
                          </div>
                        )}
                      </div>
                      <Badge variant={getStatutVariant(rdv.statut)}>
                        {getStatutLabel(rdv.statut)}
                      </Badge>
                    </div>
                    {rdv.motif && (
                      <p className="text-sm text-gray-600 mt-3">Motif: {rdv.motif}</p>
                    )}
                    {rdv.type_rdv === 'en_ligne' && rdv.online_meeting_url && (
                      <a
                        href={rdv.online_meeting_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center mt-3 px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        <Video className="w-4 h-4 mr-2" />
                        Rejoindre la consultation
                      </a>
                    )}
                    {rdv.notes && (
                      <p className="text-xs text-gray-500 mt-2">Notes: {rdv.notes}</p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Historique */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Calendar className="w-6 h-6 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Historique ({appointmentsPast.length})</h3>
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : appointmentsPast.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Aucun rendez-vous passé</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Médecin</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {appointmentsPast.slice(0, 10).map((rdv) => {
                    const medecin = medecins[rdv.medecin_id];
                    return (
                      <tr key={rdv.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(rdv.date_rdv).toLocaleDateString('fr-FR')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          Dr. {medecin?.nom || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {rdv.type_rdv === 'en_ligne' ? 'En ligne' : 'Présentiel'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge variant={getStatutVariant(rdv.statut)}>
                            {getStatutLabel(rdv.statut)}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default PatientAppointmentsList;