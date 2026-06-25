import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Save, Plus, Trash2 } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { ROLES } from '../../utils/constants';
import { toast } from 'sonner';

const emptyItem = { description: '', quantite: 1, prix_unitaire: 0 };

const FactureForm = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const backPath = user?.role === ROLES.COMPTABLE ? '/comptable/factures' : '/admin/billing';

  const [loading, setLoading] = useState(false);
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState('');
  const [dateEcheance, setDateEcheance] = useState('');
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState([{ ...emptyItem }]);

  useEffect(() => {
    api.get('/patients').then(res => setPatients(res.data)).catch(err => console.error(err));
  }, []);

  const updateItem = (idx, field, value) => {
    setItems(prev => prev.map((it, i) => i === idx ? { ...it, [field]: field === 'description' ? value : Number(value) } : it));
  };
  const addItem = () => setItems(prev => [...prev, { ...emptyItem }]);
  const removeItem = (idx) => setItems(prev => prev.filter((_, i) => i !== idx));

  const lineTotal = (it) => (it.quantite || 0) * (it.prix_unitaire || 0);
  const montantTotal = items.reduce((sum, it) => sum + lineTotal(it), 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!patientId) { toast.error('Sélectionnez un patient'); return; }
    const validItems = items.filter(it => it.description && it.prix_unitaire > 0);
    if (validItems.length === 0) { toast.error('Ajoutez au moins une ligne'); return; }
    setLoading(true);
    try {
      const payload = {
        patient_id: patientId,
        montant_total: montantTotal,
        items: validItems.map(it => ({ description: it.description, quantite: it.quantite, prix_unitaire: it.prix_unitaire, total: lineTotal(it) })),
        notes
      };
      if (dateEcheance) payload.date_echeance = new Date(dateEcheance).toISOString();
      await api.post('/billing/factures', payload);
      toast.success('Facture créée avec succès');
      navigate(backPath);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="facture-form-page">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate(backPath)} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ArrowLeft className="w-5 h-5" /></button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nouvelle facture</h2>
            <p className="text-gray-600 mt-1">Créer une facture patient</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Patient *</label>
              <select value={patientId} onChange={(e) => setPatientId(e.target.value)} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="facture-patient">
                <option value="">Sélectionner un patient</option>
                {patients.map(p => <option key={p.id} value={p.id}>{p.numero_dossier}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Date d'échéance</label>
              <input type="date" value={dateEcheance} onChange={(e) => setDateEcheance(e.target.value)} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700">Lignes de facturation *</label>
              <button type="button" onClick={addItem} className="text-sky-600 hover:text-sky-800 flex items-center text-sm" data-testid="add-item-btn"><Plus className="w-4 h-4 mr-1" />Ajouter</button>
            </div>
            {items.map((it, idx) => (
              <div key={idx} className="grid grid-cols-1 md:grid-cols-12 gap-2 items-center border border-gray-200 rounded-lg p-3" data-testid={`facture-item-${idx}`}>
                <input value={it.description} onChange={(e) => updateItem(idx, 'description', e.target.value)} placeholder="Désignation" className="md:col-span-5 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500" />
                <input type="number" min="1" value={it.quantite} onChange={(e) => updateItem(idx, 'quantite', e.target.value)} placeholder="Qté" className="md:col-span-2 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500" />
                <input type="number" value={it.prix_unitaire} onChange={(e) => updateItem(idx, 'prix_unitaire', e.target.value)} placeholder="Prix unit." className="md:col-span-3 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500" />
                <span className="md:col-span-1 text-sm text-gray-600 text-right">{lineTotal(it).toLocaleString()}</span>
                <button type="button" onClick={() => removeItem(idx)} className="md:col-span-1 text-red-500 hover:text-red-700 flex justify-center"><Trash2 className="w-4 h-4" /></button>
              </div>
            ))}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
          </div>

          <div className="text-right text-lg font-bold text-gray-900" data-testid="facture-total">Total : {montantTotal.toLocaleString()} FCFA</div>

          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button type="button" onClick={() => navigate(backPath)} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
            <button type="submit" disabled={loading} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 shadow-lg disabled:opacity-50" data-testid="submit-facture-btn">
              <Save className="w-5 h-5" /><span>{loading ? 'Enregistrement...' : 'Créer la facture'}</span>
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
};

export default FactureForm;
