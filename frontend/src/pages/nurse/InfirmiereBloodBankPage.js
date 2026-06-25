import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Droplet, Plus, User, X } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { GROUPES_SANGUINS } from '../../utils/constants';
import { toast } from 'sonner';

const emptyDonneur = { nom: '', prenom: '', groupe_sanguin: 'O+', telephone: '', email: '', adresse: '', eligible: true };
const emptyPoche = { groupe_sanguin: 'O+', quantite_ml: 450, numero_poche: '', date_collecte: '', date_expiration: '', donneur_id: '' };

const InfirmiereBloodBankPage = () => {
  const [donneurs, setDonneurs] = useState([]);
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyDonneur);
  const [saving, setSaving] = useState(false);
  const [showPoche, setShowPoche] = useState(false);
  const [poche, setPoche] = useState(emptyPoche);
  const [savingPoche, setSavingPoche] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dRes, sRes] = await Promise.all([
        api.get('/blood-bank/donneurs'),
        api.get('/blood-bank/stock/summary')
      ]);
      setDonneurs(dRes.data);
      setSummary(sRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/blood-bank/donneurs', form);
      toast.success('Donneur ajouté avec succès');
      setForm(emptyDonneur);
      setShowForm(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'ajout');
    } finally {
      setSaving(false);
    }
  };

  const stockColor = (statut) => statut === 'critique' ? 'text-red-600 bg-red-50' : statut === 'faible' ? 'text-amber-600 bg-amber-50' : 'text-emerald-600 bg-emerald-50';

  const handlePocheChange = (e) => {
    const { name, value } = e.target;
    setPoche(prev => ({ ...prev, [name]: name === 'quantite_ml' ? Number(value) : value }));
  };

  const handlePocheSubmit = async (e) => {
    e.preventDefault();
    setSavingPoche(true);
    try {
      const payload = { ...poche };
      if (!payload.donneur_id) delete payload.donneur_id;
      await api.post('/blood-bank/stock', payload);
      toast.success('Poche ajoutée au stock');
      setPoche(emptyPoche);
      setShowPoche(false);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'ajout');
    } finally {
      setSavingPoche(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="infirmiere-bloodbank-page">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Banque de sang</h2>
            <p className="text-gray-600 mt-1">Donneurs et stocks de sang</p>
          </div>
          <div className="flex space-x-3">
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
            data-testid="toggle-donneur-form-btn"
          >
            {showForm ? <X className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
            <span>{showForm ? 'Fermer' : 'Nouveau donneur'}</span>
          </button>
          <button
            onClick={() => setShowPoche(!showPoche)}
            className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-lg font-medium hover:from-red-600 hover:to-red-700 transition-all flex items-center space-x-2 shadow-lg"
            data-testid="toggle-poche-form-btn"
          >
            {showPoche ? <X className="w-5 h-5" /> : <Droplet className="w-5 h-5" />}
            <span>{showPoche ? 'Fermer' : 'Ajouter une poche'}</span>
          </button>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          {GROUPES_SANGUINS.map(g => {
            const stock = summary[g];
            return (
              <div key={g} className={`rounded-xl p-4 border-2 ${stock ? stockColor(stock.statut) : 'bg-gray-50 text-gray-400'}`}>
                <div className="flex items-center justify-between mb-2">
                  <Droplet className="w-5 h-5" />
                  <span className="text-xs font-medium">{stock?.nombre_poches || 0} poches</span>
                </div>
                <div className="text-2xl font-bold mb-1">{g}</div>
                <div className="text-sm">{stock?.quantite_ml || 0} ml</div>
              </div>
            );
          })}
        </div>

        {showPoche && (
          <form onSubmit={handlePocheSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4" data-testid="poche-form">
            <h3 className="text-lg font-semibold text-gray-900">Ajouter une poche de sang</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <select name="groupe_sanguin" value={poche.groupe_sanguin} onChange={handlePocheChange} className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="poche-groupe">
                {GROUPES_SANGUINS.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
              <input name="numero_poche" value={poche.numero_poche} onChange={handlePocheChange} required placeholder="Numéro de poche *" className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="poche-numero" />
              <input name="quantite_ml" type="number" value={poche.quantite_ml} onChange={handlePocheChange} required placeholder="Quantité (ml) *" className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="poche-quantite" />
              <select name="donneur_id" value={poche.donneur_id} onChange={handlePocheChange} className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500">
                <option value="">Donneur (optionnel)</option>
                {donneurs.map(d => <option key={d.id} value={d.id}>{d.nom} {d.prenom} ({d.groupe_sanguin})</option>)}
              </select>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date de collecte *</label>
                <input name="date_collecte" type="date" value={poche.date_collecte} onChange={handlePocheChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="poche-collecte" />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Date d'expiration *</label>
                <input name="date_expiration" type="date" value={poche.date_expiration} onChange={handlePocheChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="poche-expiration" />
              </div>
            </div>
            <button type="submit" disabled={savingPoche} className="bg-gradient-to-r from-red-500 to-red-600 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50" data-testid="submit-poche-btn">
              {savingPoche ? 'Enregistrement...' : 'Enregistrer la poche'}
            </button>
          </form>
        )}

        {showForm && (
          <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-4" data-testid="donneur-form">
            <h3 className="text-lg font-semibold text-gray-900">Enregistrer un donneur</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input name="nom" value={form.nom} onChange={handleChange} required placeholder="Nom *" className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="donneur-nom" />
              <input name="prenom" value={form.prenom} onChange={handleChange} required placeholder="Prénom *" className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="donneur-prenom" />
              <select name="groupe_sanguin" value={form.groupe_sanguin} onChange={handleChange} className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="donneur-groupe">
                {GROUPES_SANGUINS.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
              <input name="telephone" value={form.telephone} onChange={handleChange} required placeholder="Téléphone *" className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="donneur-telephone" />
              <input name="email" type="email" value={form.email} onChange={handleChange} placeholder="Email" className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
              <input name="adresse" value={form.adresse} onChange={handleChange} placeholder="Adresse" className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
            <button type="submit" disabled={saving} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium disabled:opacity-50" data-testid="submit-donneur-btn">
              {saving ? 'Enregistrement...' : 'Enregistrer'}
            </button>
          </form>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Donneurs ({donneurs.length})</h3>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : donneurs.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Aucun donneur enregistré</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Groupe</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Téléphone</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {donneurs.map(d => (
                    <tr key={d.id} className="hover:bg-gray-50" data-testid={`donneur-row-${d.id}`}>
                      <td className="px-6 py-4"><div className="flex items-center"><User className="w-4 h-4 text-gray-400 mr-2" />{d.nom} {d.prenom}</div></td>
                      <td className="px-6 py-4"><Badge variant="info">{d.groupe_sanguin}</Badge></td>
                      <td className="px-6 py-4 text-sm text-gray-600">{d.telephone}</td>
                      <td className="px-6 py-4"><Badge variant={d.eligible ? 'success' : 'error'}>{d.eligible ? 'Éligible' : 'Non éligible'}</Badge></td>
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

export default InfirmiereBloodBankPage;
