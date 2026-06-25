import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { DollarSign, FileText, TrendingUp, FileDown } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { exportFacturePDF } from '../../utils/pdfExport';

const BillingPage = () => {
  const [factures, setFactures] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filterStatut, setFilterStatut] = useState('');

  useEffect(() => {
    loadData();
  }, [filterStatut]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterStatut) params.statut = filterStatut;
      
      const [facturesRes, statsRes] = await Promise.all([
        api.get('/billing/factures', { params }),
        api.get('/billing/stats')
      ]);
      
      setFactures(facturesRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatutVariant = (statut) => {
    const variants = {
      'en_attente': 'warning',
      'payée': 'success',
      'partiellement_payée': 'info',
      'annulée': 'error'
    };
    return variants[statut] || 'default';
  };

  const getStatutLabel = (statut) => {
    const labels = {
      'en_attente': 'En attente',
      'payée': 'Payée',
      'partiellement_payée': 'Partiellement payée',
      'annulée': 'Annulée'
    };
    return labels[statut] || statut;
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Facturation</h2>
          <p className="text-gray-600 mt-1">Gestion des factures et paiements</p>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Total facturé</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_factures.toLocaleString()} FCFA</p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Total encaissé</p>
                  <p className="text-2xl font-bold text-emerald-900">{stats.total_paye.toLocaleString()} FCFA</p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Impayés</p>
                  <p className="text-2xl font-bold text-red-900">{stats.total_impaye.toLocaleString()} FCFA</p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Factures</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.nombre_factures}</p>
                  <p className="text-xs text-gray-500 mt-1">{stats.factures_payees} payées</p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                  <FileText className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filtre */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Statut :</label>
            <select
              value={filterStatut}
              onChange={(e) => setFilterStatut(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            >
              <option value="">Tous les statuts</option>
              <option value="en_attente">En attente</option>
              <option value="payée">Payée</option>
              <option value="partiellement_payée">Partiellement payée</option>
              <option value="annulée">Annulée</option>
            </select>
          </div>
        </div>

        {/* Liste des factures */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : factures.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune facture trouvée</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Numéro
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Montant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Items
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {factures.map((facture) => (
                    <tr key={facture.id} className="hover:bg-gray-50 transition-colors" data-testid={`facture-row-${facture.id}`}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{facture.numero_facture}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(facture.created_at).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-gray-900">{facture.montant_total.toLocaleString()} FCFA</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant={getStatutVariant(facture.statut)}>
                          {getStatutLabel(facture.statut)}
                        </Badge>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          {facture.items.length} item(s)
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => exportFacturePDF(facture)}
                          className="inline-flex items-center space-x-1 text-sky-600 hover:text-sky-800 text-sm"
                          data-testid={`export-facture-${facture.id}`}
                        >
                          <FileDown className="w-4 h-4" /><span>PDF</span>
                        </button>
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

export default BillingPage;