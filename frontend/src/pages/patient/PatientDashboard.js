import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { StatCard } from '../../components/common/Card';
import { Calendar, FileText, DollarSign, Stethoscope } from 'lucide-react';
import api from '../../services/api';

const PatientDashboard = () => {
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Mon espace patient</h2>
          <p className="text-gray-600">Bienvenue sur votre portail patient</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={Calendar}
            title="Mes rendez-vous"
            value={stats?.mes_rendez_vous || 0}
            color="blue"
          />
          <StatCard
            icon={Stethoscope}
            title="Mes consultations"
            value={stats?.mes_consultations || 0}
            color="green"
          />
          <StatCard
            icon={FileText}
            title="Mes factures"
            value={stats?.mes_factures || 0}
            color="purple"
          />
          <StatCard
            icon={DollarSign}
            title="Factures impayées"
            value={stats?.factures_impayees || 0}
            color="red"
          />
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Accès rapide</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/patient/appointments" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Calendar className="w-8 h-8 text-sky-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Mes rendez-vous</h4>
              <p className="text-sm text-gray-600 mt-1">Consultez vos rendez-vous</p>
            </a>
            <a href="/patient/consultations" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <FileText className="w-8 h-8 text-emerald-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Mes consultations</h4>
              <p className="text-sm text-gray-600 mt-1">Historique médical</p>
            </a>
            <a href="/patient/factures" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <DollarSign className="w-8 h-8 text-purple-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Mes factures</h4>
              <p className="text-sm text-gray-600 mt-1">Consultez vos factures</p>
            </a>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default PatientDashboard;