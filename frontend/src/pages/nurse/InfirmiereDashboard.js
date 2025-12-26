import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { StatCard } from '../../components/common/Card';
import { Building2, Droplet, Users, AlertTriangle } from 'lucide-react';
import api from '../../services/api';

const InfirmiereDashboard = () => {
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
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Tableau de bord infirmière</h2>
          <p className="text-gray-600">Vue d'ensemble des soins et hospitalisations</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={Users}
            title="Patients totaux"
            value={stats?.total_patients || 0}
            color="blue"
          />
          <StatCard
            icon={Building2}
            title="Lits disponibles"
            value={stats?.lits_disponibles || 0}
            color="green"
          />
          <StatCard
            icon={Building2}
            title="Lits occupés"
            value={stats?.lits_occupes || 0}
            color="red"
          />
          <StatCard
            icon={Droplet}
            title="Alertes sang"
            value={stats?.groupes_sanguins_critiques || 0}
            color="purple"
          />
        </div>

        {stats?.groupes_sanguins_critiques > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-2">Alertes critiques - Banque de sang</h3>
                <p className="text-sm text-red-800">
                  {stats.groupes_sanguins_critiques} groupe(s) sanguin(s) en stock critique. Vérifiez la banque de sang.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Accès rapide</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a href="/infirmiere/lits" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Building2 className="w-8 h-8 text-sky-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Gestion des lits</h4>
              <p className="text-sm text-gray-600 mt-1">Admissions et libérations</p>
            </a>
            <a href="/infirmiere/blood-bank" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Droplet className="w-8 h-8 text-red-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Banque de sang</h4>
              <p className="text-sm text-gray-600 mt-1">Gestion des stocks</p>
            </a>
            <a href="/infirmiere/patients" className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <Users className="w-8 h-8 text-emerald-600 mb-2" />
              <h4 className="font-semibold text-gray-900">Patients</h4>
              <p className="text-sm text-gray-600 mt-1">Consultation des dossiers</p>
            </a>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default InfirmiereDashboard;