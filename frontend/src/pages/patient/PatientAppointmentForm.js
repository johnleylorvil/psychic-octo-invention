import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Save, Video } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'sonner';

const PatientAppointmentForm = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [medecins, setMedecins] = useState([]);
  const [patientId, setPatientId] = useState('');
  const [form, setForm] = useState({ medecin_id: '', date_rdv: '', type_rdv: 'présentiel', motif: '' });

  useEffect(() => {
    Promise.all([
      api.get('/users/medecins'),
      api.get('/patients')
    ]).then(([mRes, pRes]) => {
      setMedecins(mRes.data);
      const mine = pRes.data.find(p => p.user_id === user.id) || pRes.data[0];
      if (mine) setPatientId(mine.id);
    }).catch(err => console.error(err));
  }, [user.id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!patientId) { toast.error('Dossier patient introuvable'); return; }
    setLoading(true);
    try {
      await api.post('/appointments', {
        patient_id: patientId,
        medecin_id: form.medecin_id,
        date_rdv: new Date(form.date_rdv).toISOString(),
        type_rdv: form.type_rdv,
        motif: form.motif
      });
      toast.success('Demande de rendez-vous envoyée');
      navigate('/patient/appointments');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="patient-appointment-form-page">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/patient/appointments')} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ArrowLeft className="w-5 h-5" /></button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Prendre un rendez-vous</h2>
            <p className="text-gray-600 mt-1">Demandez une consultation avec un médecin</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Médecin *</label>
            <select name="medecin_id" value={form.medecin_id} onChange={handleChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="rdv-medecin">
              <option value="">Sélectionner un médecin</option>
              {medecins.map(m => <option key={m.id} value={m.id}>Dr. {m.nom} {m.prenom} {m.specialite ? `(${m.specialite})` : ''}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date et heure souhaitées *</label>
              <input name="date_rdv" type="datetime-local" value={form.date_rdv} onChange={handleChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="rdv-date" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Type de consultation *</label>
              <select name="type_rdv" value={form.type_rdv} onChange={handleChange} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="rdv-type">
                <option value="présentiel">Présentiel</option>
                <option value="en_ligne">En ligne (téléconsultation)</option>
              </select>
            </div>
          </div>
          {form.type_rdv === 'en_ligne' && (
            <p className="text-sm text-purple-600 flex items-center"><Video className="w-4 h-4 mr-1" />Un lien de visioconférence vous sera communiqué après confirmation.</p>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Motif</label>
            <textarea name="motif" value={form.motif} onChange={handleChange} rows={3} placeholder="Décrivez brièvement le motif de votre consultation..." className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
          </div>
          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button type="button" onClick={() => navigate('/patient/appointments')} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
            <button type="submit" disabled={loading} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 shadow-lg disabled:opacity-50" data-testid="submit-rdv-btn">
              <Save className="w-5 h-5" /><span>{loading ? 'Envoi...' : 'Demander le rendez-vous'}</span>
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
};

export default PatientAppointmentForm;
