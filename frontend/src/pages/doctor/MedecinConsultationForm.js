import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Save } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'sonner';

const MedecinConsultationForm = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [patients, setPatients] = useState([]);
  const [form, setForm] = useState({
    patient_id: '', motif: '', symptomes: '', diagnostic: '', traitement: '', notes: '', examens_demandes: ''
  });

  useEffect(() => {
    api.get('/patients').then(res => setPatients(res.data)).catch(err => console.error(err));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/consultations', { ...form, medecin_id: user.id });
      toast.success('Consultation enregistrée');
      navigate('/medecin/consultations');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="consultation-form-page">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/medecin/consultations')} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ArrowLeft className="w-5 h-5" /></button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nouvelle consultation</h2>
            <p className="text-gray-600 mt-1">Enregistrer une consultation médicale</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Patient *</label>
            <select name="patient_id" value={form.patient_id} onChange={handleChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="consultation-patient">
              <option value="">Sélectionner un patient</option>
              {patients.map(p => <option key={p.id} value={p.id}>{p.numero_dossier}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Motif *</label>
            <input name="motif" value={form.motif} onChange={handleChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="consultation-motif" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Symptômes</label>
              <textarea name="symptomes" value={form.symptomes} onChange={handleChange} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Diagnostic</label>
              <textarea name="diagnostic" value={form.diagnostic} onChange={handleChange} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Traitement</label>
              <textarea name="traitement" value={form.traitement} onChange={handleChange} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Examens demandés</label>
              <textarea name="examens_demandes" value={form.examens_demandes} onChange={handleChange} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
            <textarea name="notes" value={form.notes} onChange={handleChange} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
          </div>
          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button type="button" onClick={() => navigate('/medecin/consultations')} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
            <button type="submit" disabled={loading} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 shadow-lg disabled:opacity-50" data-testid="submit-consultation-btn">
              <Save className="w-5 h-5" /><span>{loading ? 'Enregistrement...' : 'Enregistrer'}</span>
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
};

export default MedecinConsultationForm;
