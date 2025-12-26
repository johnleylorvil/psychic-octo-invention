import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { StatCard } from '../../components/common/Card';
import { Users, Calendar, Stethoscope, FileText } from 'lucide-react';
import api from '../../services/api';

const MedecinDashboard = () => {
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tableau de bord médecin</h2>
          <p className="text-gray-600">Vue d'ensemble de votre activité</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={Users}
            title="Mes patients"
            value={stats?.mes_patients || 0}
            color="blue"
          />
          <StatCard
            icon={Calendar}
            title="Mes rendez-vous"
            value={stats?.mes_rendez_vous || 0}
            color="green"
          />
          <StatCard
            icon={Stethoscope}
            title="Consultations (mois)"
            value={stats?.consultations_ce_mois || 0}
            color="purple"
          />
          <StatCard
            icon={FileText}
            title="Patients totaux"
            value={stats?.total_patients || 0}
            color="yellow"
          />
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Activité récente</h3>
          <p className="text-gray-600 text-center py-8">Consultez vos rendez-vous et consultations dans le menu</p>
        </div>
      </div>
    </MainLayout>
  );
};

export default MedecinDashboard;