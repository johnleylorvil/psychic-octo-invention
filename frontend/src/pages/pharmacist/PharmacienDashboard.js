import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { StatCard } from '../../components/common/Card';
import { Pill, AlertTriangle, Package } from 'lucide-react';
import api from '../../services/api';

const PharmacienDashboard = () => {
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tableau de bord pharmacien</h2>
          <p className="text-gray-600">Gestion de la pharmacie et des stocks</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatCard
            icon={Pill}
            title="Médicaments"
            value={stats?.total_medicaments || 0}
            color="blue"
          />
          <StatCard
            icon={Package}
            title="Stock faible"
            value={stats?.alertes_stock_faible || 0}
            color="red"
          />
          <StatCard
            icon={AlertTriangle}
            title="Péremption proche"
            value={stats?.alertes_peremption || 0}
            color="yellow"
          />
        </div>

        {(stats?.alertes_stock_faible > 0 || stats?.alertes_peremption > 0) && (
          <div className="space-y-4">
            {stats.alertes_stock_faible > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-6">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-red-900 mb-2">Alertes stock faible</h3>
                    <p className="text-sm text-red-800">
                      {stats.alertes_stock_faible} médicament(s) en dessous du seuil minimum. Réapprovisionnement urgent requis.
                    </p>
                  </div>
                </div>
              </div>
            )}
            {stats.alertes_peremption > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold text-amber-900 mb-2">Péremption imminente</h3>
                    <p className="text-sm text-amber-800">
                      {stats.alertes_peremption} lot(s) arrivent à péremption dans les 30 jours. Vérification nécessaire.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Accès rapide</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/pharmacien/medicaments" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Pill className="w-8 h-8 text-sky-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Médicaments</h4>
              <p className="text-sm text-gray-600 mt-1">Catalogue complet</p>
            </a>
            <a href="/pharmacien/stocks" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Package className="w-8 h-8 text-emerald-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Stocks</h4>
              <p className="text-sm text-gray-600 mt-1">Gestion des stocks</p>
            </a>
            <a href="/pharmacien/prescriptions" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <AlertTriangle className="w-8 h-8 text-purple-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Prescriptions</h4>
              <p className="text-sm text-gray-600 mt-1">Ordonnances en attente</p>
            </a>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default PharmacienDashboard;