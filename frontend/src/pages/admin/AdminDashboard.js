import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { StatCard } from '../../components/common/Card';
import { Users, Calendar, Building2, Activity, AlertTriangle, Pill } from 'lucide-react';
import api from '../../services/api';

const AdminDashboard = () => {
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
      console.error('Erreur lors du chargement des statistiques:', error);
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tableau de bord administrateur</h2>
          <p className="text-gray-600">Vue d'ensemble de la clinique</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={Users}
            title="Patients totaux"
            value={stats?.total_patients || 0}
            color="blue"
          />
          <StatCard
            icon={Calendar}
            title="Rendez-vous aujourd'hui"
            value={stats?.rendez_vous_aujourdhui || 0}
            color="green"
          />
          <StatCard
            icon={Building2}
            title="Lits disponibles"
            value={stats?.lits_disponibles || 0}
            color="purple"
          />
          <StatCard
            icon={AlertTriangle}
            title="Alertes pharmacie"
            value={stats?.alertes_pharmacie || 0}
            color="red"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-sky-600" />
              Statistiques des services
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Services actifs</span>
                <span className="text-lg font-bold text-gray-900">{stats?.total_services || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Lits occupés</span>
                <span className="text-lg font-bold text-gray-900">{stats?.lits_occupes || 0}</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Utilisateurs actifs</span>
                <span className="text-lg font-bold text-gray-900">{stats?.total_utilisateurs_actifs || 0}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2 text-amber-600" />
              Alertes et notifications
            </h3>
            <div className="space-y-3">
              {stats?.alertes_pharmacie > 0 && (
                <div className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <Pill className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-red-900">
                      Stock de médicaments faible
                    </p>
                    <p className="text-xs text-red-700 mt-1">
                      {stats.alertes_pharmacie} médicament(s) à réapprovisionner
                    </p>
                  </div>
                </div>
              )}
              
              <div className="flex items-start space-x-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <Calendar className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-blue-900">
                    Rendez-vous du jour
                  </p>
                  <p className="text-xs text-blue-700 mt-1">
                    {stats?.rendez_vous_aujourdhui || 0} consultation(s) prévue(s)
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default AdminDashboard;