import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { StatCard } from '../../components/common/Card';
import { DollarSign, FileText, TrendingUp, AlertCircle } from 'lucide-react';
import api from '../../services/api';

const ComptableDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tableau de bord comptable</h2>
          <p className="text-gray-600">Gestion financière et facturation</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={DollarSign}
            title="Montant total"
            value={`${(stats?.montant_total || 0).toLocaleString()} F`}
            color="blue"
          />
          <StatCard
            icon={TrendingUp}
            title="Montant payé"
            value={`${(stats?.montant_paye || 0).toLocaleString()} F`}
            color="green"
          />
          <StatCard
            icon={AlertCircle}
            title="Montant impayé"
            value={`${(stats?.montant_impaye || 0).toLocaleString()} F`}
            color="red"
          />
          <StatCard
            icon={FileText}
            title="Factures impayées"
            value={stats?.factures_impayees || 0}
            color="yellow"
          />
        </div>

        {stats?.factures_impayees > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-amber-900 mb-2">Attention</h3>
                <p className="text-sm text-amber-800">
                  {stats.factures_impayees} facture(s) en attente de paiement pour un montant de {(stats.montant_impaye || 0).toLocaleString()} FCFA.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Résumé financier</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Total factures</span>
                <span className="text-lg font-bold text-gray-900">{stats?.total_factures || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-emerald-50 rounded-lg">
                <span className="text-sm text-emerald-700">Factures payées</span>
                <span className="text-lg font-bold text-emerald-900">{stats?.factures_payees || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-amber-50 rounded-lg">
                <span className="text-sm text-amber-700">En attente</span>
                <span className="text-lg font-bold text-amber-900">{stats?.factures_impayees || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Accès rapide</h3>
            <div className="space-y-3">
              <a href="/comptable/factures" className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="w-5 h-5 text-sky-600" />
                    <span className="font-medium text-gray-900">Factures</span>
                  </div>
                  <span className="text-sm text-gray-500">→</span>
                </div>
              </a>
              <a href="/comptable/paiements" className="block p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <DollarSign className="w-5 h-5 text-emerald-600" />
                    <span className="font-medium text-gray-900">Paiements</span>
                  </div>
                  <span className="text-sm text-gray-500">→</span>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ComptableDashboard;