import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Save, Plus, Trash2 } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { toast } from 'sonner';

const emptyMed = { medicament_id: '', nom: '', dosage: '', frequence: '', duree: '' };

const MedecinPrescriptionForm = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [consultations, setConsultations] = useState([]);
  const [medicaments, setMedicaments] = useState([]);
  const [form, setForm] = useState({ consultation_id: '', patient_id: '', instructions_generales: '' });
  const [lignes, setLignes] = useState([{ ...emptyMed }]);

  useEffect(() => {
    Promise.all([
      api.get('/consultations', { params: { medecin_id: user.id } }),
      api.get('/pharmacy/medicaments')
    ]).then(([cRes, mRes]) => {
      setConsultations(cRes.data);
      setMedicaments(mRes.data);
    }).catch(err => console.error(err));
  }, [user.id]);

  const handleConsultationChange = (e) => {
    const consultation_id = e.target.value;
    const consult = consultations.find(c => c.id === consultation_id);
    setForm(prev => ({ ...prev, consultation_id, patient_id: consult?.patient_id || '' }));
  };

  const updateLigne = (idx, field, value) => {
    setLignes(prev => prev.map((l, i) => {
      if (i !== idx) return l;
      if (field === 'medicament_id') {
        const med = medicaments.find(m => m.id === value);
        return { ...l, medicament_id: value, nom: med?.nom || '', dosage: med?.dosage || l.dosage };
      }
      return { ...l, [field]: value };
    }));
  };

  const addLigne = () => setLignes(prev => [...prev, { ...emptyMed }]);
  const removeLigne = (idx) => setLignes(prev => prev.filter((_, i) => i !== idx));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.consultation_id || !form.patient_id) {
      toast.error('Veuillez sélectionner une consultation');
      return;
    }
    const validLignes = lignes.filter(l => l.medicament_id && l.nom);
    if (validLignes.length === 0) {
      toast.error('Ajoutez au moins un médicament');
      return;
    }
    setLoading(true);
    try {
      await api.post('/consultations/prescriptions', {
        consultation_id: form.consultation_id,
        patient_id: form.patient_id,
        medecin_id: user.id,
        medicaments: validLignes.map(l => ({ medicament_id: l.medicament_id, nom: l.nom, dosage: l.dosage || '-', frequence: l.frequence || '-', duree: l.duree || '-' })),
        instructions_generales: form.instructions_generales
      });
      toast.success('Prescription créée');
      navigate('/medecin/prescriptions');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="prescription-form-page">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/medecin/prescriptions')} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ArrowLeft className="w-5 h-5" /></button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nouvelle prescription</h2>
            <p className="text-gray-600 mt-1">Émettre une ordonnance</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Consultation associée *</label>
            <select value={form.consultation_id} onChange={handleConsultationChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="prescription-consultation">
              <option value="">Sélectionner une consultation</option>
              {consultations.map(c => <option key={c.id} value={c.id}>{c.motif} · {new Date(c.date_consultation).toLocaleDateString('fr-FR')}</option>)}
            </select>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Médicaments *</label>
              <button type="button" onClick={addLigne} className="text-sky-600 hover:text-sky-800 flex items-center text-sm" data-testid="add-med-line-btn"><Plus className="w-4 h-4 mr-1" />Ajouter</button>
            </div>
            {lignes.map((l, idx) => (
              <div key={idx} className="grid grid-cols-1 md:grid-cols-12 gap-2 items-center border border-gray-200 rounded-lg p-3" data-testid={`med-line-${idx}`}>
                <select value={l.medicament_id} onChange={(e) => updateLigne(idx, 'medicament_id', e.target.value)} className="md:col-span-4 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 text-sm">
                  <option value="">Médicament</option>
                  {medicaments.map(m => <option key={m.id} value={m.id}>{m.nom}</option>)}
                </select>
                <input value={l.dosage} onChange={(e) => updateLigne(idx, 'dosage', e.target.value)} placeholder="Dosage" className="md:col-span-3 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500" />
                <input value={l.frequence} onChange={(e) => updateLigne(idx, 'frequence', e.target.value)} placeholder="Fréquence" className="md:col-span-2 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500" />
                <input value={l.duree} onChange={(e) => updateLigne(idx, 'duree', e.target.value)} placeholder="Durée" className="md:col-span-2 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500" />
                <button type="button" onClick={() => removeLigne(idx)} className="md:col-span-1 text-red-500 hover:text-red-700 flex justify-center"><Trash2 className="w-4 h-4" /></button>
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Instructions générales</label>
            <textarea name="instructions_generales" value={form.instructions_generales} onChange={(e) => setForm(prev => ({ ...prev, instructions_generales: e.target.value }))} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
          </div>

          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button type="button" onClick={() => navigate('/medecin/prescriptions')} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
            <button type="submit" disabled={loading} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 shadow-lg disabled:opacity-50" data-testid="submit-prescription-btn">
              <Save className="w-5 h-5" /><span>{loading ? 'Enregistrement...' : 'Enregistrer'}</span>
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
};

export default MedecinPrescriptionForm;
