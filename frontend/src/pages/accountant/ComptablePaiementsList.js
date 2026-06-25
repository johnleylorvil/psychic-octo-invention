import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { DollarSign, CreditCard } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';

const ComptablePaiementsList = () => {
  const [paiements, setPaiements] = useState([]);
  const [factures, setFactures] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pRes, fRes] = await Promise.all([
        api.get('/billing/paiements'),
        api.get('/billing/factures')
      ]);
      setPaiements(pRes.data);
      const fMap = {}; fRes.data.forEach(f => { fMap[f.id] = f; }); setFactures(fMap);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const total = paiements.reduce((sum, p) => sum + (p.montant || 0), 0);
  const methodeVariant = (m) => ({ 'espèces': 'success', 'carte': 'info', 'virement': 'default', 'assurance': 'warning', 'mobile_money': 'info' }[m] || 'default');

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="comptable-paiements-page">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Paiements</h2>
          <p className="text-gray-600 mt-1">Suivi des encaissements</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div><p className="text-sm text-gray-600 mb-1">Total encaissé</p><p className="text-2xl font-bold text-emerald-700">{total.toLocaleString()} FCFA</p></div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center"><DollarSign className="w-6 h-6 text-white" /></div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div><p className="text-sm text-gray-600 mb-1">Nombre de paiements</p><p className="text-2xl font-bold text-gray-900">{paiements.length}</p></div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center"><CreditCard className="w-6 h-6 text-white" /></div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div></div>
          ) : paiements.length === 0 ? (
            <p className="text-center text-gray-500 py-12">Aucun paiement enregistré</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Facture</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Méthode</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Référence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {paiements.map(p => (
                    <tr key={p.id} className="hover:bg-gray-50" data-testid={`paiement-row-${p.id}`}>
                      <td className="px-6 py-4 text-sm text-gray-600">{new Date(p.date_paiement).toLocaleDateString('fr-FR')}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{factures[p.facture_id]?.numero_facture || p.facture_id?.substring(0, 8)}</td>
                      <td className="px-6 py-4 text-sm font-semibold text-emerald-700">{p.montant.toLocaleString()} FCFA</td>
                      <td className="px-6 py-4"><Badge variant={methodeVariant(p.methode)}>{p.methode}</Badge></td>
                      <td className="px-6 py-4 text-sm text-gray-600">{p.reference || '-'}</td>
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

export default ComptablePaiementsList;
