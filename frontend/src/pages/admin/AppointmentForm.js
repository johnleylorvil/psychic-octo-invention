import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Save, Calendar } from 'lucide-react';
import api from '../../services/api';
import { toast } from 'sonner';

const AppointmentForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [loading, setLoading] = useState(false);
  const [patients, setPatients] = useState([]);
  const [medecins, setMedecins] = useState([]);
  const [formData, setFormData] = useState({
    patient_id: '',
    medecin_id: '',
    date_rdv: '',
    type_rdv: 'présentiel',
    motif: '',
    online_meeting_url: '',
    statut: 'planifié',
    notes: ''
  });

  useEffect(() => {
    loadSelects();
    if (isEdit) {
      loadAppointment();
    }
  }, [id]);

  const loadSelects = async () => {
    try {
      const [patientsRes, medecinsRes] = await Promise.all([
        api.get('/patients'),
        api.get('/users?role=médecin')
      ]);
      setPatients(patientsRes.data);
      setMedecins(medecinsRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    }
  };

  const loadAppointment = async () => {
    try {
      const response = await api.get(`/appointments/${id}`);
      setFormData(response.data);
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Erreur lors du chargement');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEdit) {
        await api.put(`/appointments/${id}`, formData);
        toast.success('Rendez-vous mis à jour');
      } else {
        await api.post('/appointments', formData);
        toast.success('Rendez-vous créé avec succès');
      }
      navigate('/admin/appointments');
    } catch (error) {
      console.error('Erreur:', error);
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/admin/appointments')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Modifier le rendez-vous' : 'Nouveau rendez-vous'}
            </h2>
            <p className="text-gray-600 mt-1">Planifier une consultation</p>
          </div>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Patient *
              </label>
              <select
                name="patient_id"
                value={formData.patient_id}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="">Sélectionner un patient</option>
                {patients.map(patient => (
                  <option key={patient.id} value={patient.id}>
                    {patient.numero_dossier}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Médecin *
              </label>
              <select
                name="medecin_id"
                value={formData.medecin_id}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="">Sélectionner un médecin</option>
                {medecins.map(medecin => (
                  <option key={medecin.id} value={medecin.id}>
                    Dr. {medecin.nom} {medecin.prenom} {medecin.specialite && `(${medecin.specialite})`}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date et heure *
              </label>
              <input
                type="datetime-local"
                name="date_rdv"
                value={formData.date_rdv}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de rendez-vous *
              </label>
              <select
                name="type_rdv"
                value={formData.type_rdv}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="présentiel">Présentiel</option>
                <option value="en_ligne">En ligne (téléconsultation)</option>
              </select>
            </div>

            {formData.type_rdv === 'en_ligne' && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Lien de visioconférence
                </label>
                <input
                  type="url"
                  name="online_meeting_url"
                  value={formData.online_meeting_url}
                  onChange={handleChange}
                  placeholder="https://zoom.us/j/123456789"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                />
              </div>
            )}

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motif de consultation
              </label>
              <input
                type="text"
                name="motif"
                value={formData.motif}
                onChange={handleChange}
                placeholder="Ex: Consultation générale, Suivi..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Statut
              </label>
              <select
                name="statut"
                value={formData.statut}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              >
                <option value="planifié">Planifié</option>
                <option value="confirmé">Confirmé</option>
                <option value="en_attente">En attente</option>
                <option value="terminé">Terminé</option>
                <option value="annulé">Annulé</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                placeholder="Notes additionnelles..."
              />
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={() => navigate('/admin/appointments')}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg disabled:opacity-50"
              data-testid="submit-appointment-btn"
            >
              <Save className="w-5 h-5" />
              <span>{loading ? 'Enregistrement...' : 'Enregistrer'}</span>
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
};

export default AppointmentForm;