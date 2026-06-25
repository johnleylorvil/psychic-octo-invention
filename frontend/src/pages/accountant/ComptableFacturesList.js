import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { DollarSign, FileText, TrendingUp, FileDown, CheckCircle, Plus } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { exportFacturePDF } from '../../utils/pdfExport';

const ComptableFacturesList = () => {
  const [factures, setFactures] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterStatut, setFilterStatut] = useState('');
  const navigate = useNavigate();

  useEffect(() => { loadData(); }, [filterStatut]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterStatut) params.statut = filterStatut;
      const [fRes, sRes] = await Promise.all([
        api.get('/billing/factures', { params }),
        api.get('/billing/stats')
      ]);
      setFactures(fRes.data);
      setStats(sRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const encaisser = async (facture) => {
    if (!window.confirm(`Encaisser ${facture.montant_total.toLocaleString()} FCFA pour la facture ${facture.numero_facture} ?`)) return;
    try {
      await api.post('/billing/paiements', {
        facture_id: facture.id,
        montant: facture.montant_total,
        methode: 'espèces'
      });
      toast.success(`Facture ${facture.numero_facture} encaissée`);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'encaissement');
    }
  };

  const getVariant = (s) => ({ 'en_attente': 'warning', 'payée': 'success', 'partiellement_payée': 'info', 'annulée': 'error' }[s] || 'default');

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="comptable-factures-page">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Factures</h2>
            <p className="text-gray-600 mt-1">Gestion et suivi des factures</p>
          </div>
          <button
            onClick={() => navigate('/comptable/factures/new')}
            className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
            data-testid="add-facture-btn"
          >
            <Plus className="w-5 h-5" />
            <span>Nouvelle facture</span>
          </button>
        </div>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div><p className="text-sm text-gray-600 mb-1">Total facturé</p><p className="text-2xl font-bold text-gray-900">{stats.total_factures.toLocaleString()} FCFA</p></div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center"><FileText className="w-6 h-6 text-white" /></div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div><p className="text-sm text-gray-600 mb-1">Encaissé</p><p className="text-2xl font-bold text-emerald-700">{stats.total_paye.toLocaleString()} FCFA</p></div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center"><DollarSign className="w-6 h-6 text-white" /></div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div><p className="text-sm text-gray-600 mb-1">Impayés</p><p className="text-2xl font-bold text-red-700">{stats.total_impaye.toLocaleString()} FCFA</p></div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center"><TrendingUp className="w-6 h-6 text-white" /></div>
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div><p className="text-sm text-gray-600 mb-1">Factures</p><p className="text-2xl font-bold text-gray-900">{stats.nombre_factures}</p><p className="text-xs text-gray-500 mt-1">{stats.factures_payees} payées</p></div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center"><FileText className="w-6 h-6 text-white" /></div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Statut :</label>
            <select value={filterStatut} onChange={(e) => setFilterStatut(e.target.value)} className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="statut-filter">
              <option value="">Tous</option>
              <option value="en_attente">En attente</option>
              <option value="payée">Payée</option>
              <option value="partiellement_payée">Partiellement payée</option>
              <option value="annulée">Annulée</option>
            </select>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div></div>
          ) : factures.length === 0 ? (
            <p className="text-center text-gray-500 py-12">Aucune facture trouvée</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Numéro</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {factures.map(f => (
                    <tr key={f.id} className="hover:bg-gray-50" data-testid={`facture-row-${f.id}`}>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{f.numero_facture}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{new Date(f.created_at).toLocaleDateString('fr-FR')}</td>
                      <td className="px-6 py-4 text-sm font-semibold text-gray-900">{f.montant_total.toLocaleString()} FCFA</td>
                      <td className="px-6 py-4"><Badge variant={getVariant(f.statut)}>{f.statut}</Badge></td>
                      <td className="px-6 py-4 text-right text-sm">
                        <div className="flex items-center justify-end space-x-3">
                          {f.statut !== 'payée' && f.statut !== 'annulée' && (
                            <button onClick={() => encaisser(f)} className="flex items-center space-x-1 text-emerald-600 hover:text-emerald-800" data-testid={`encaisser-${f.id}`}>
                              <CheckCircle className="w-4 h-4" /><span>Encaisser</span>
                            </button>
                          )}
                          <button onClick={() => exportFacturePDF(f)} className="flex items-center space-x-1 text-sky-600 hover:text-sky-800" data-testid={`export-facture-${f.id}`}>
                            <FileDown className="w-4 h-4" /><span>PDF</span>
                          </button>
                        </div>
                      </td>
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

export default ComptableFacturesList;
