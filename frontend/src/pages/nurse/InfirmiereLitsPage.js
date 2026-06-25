import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Bed, Building2 } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { toast } from 'sonner';

const InfirmiereLitsPage = () => {
  const [services, setServices] = useState([]);
  const [lits, setLits] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [sRes, lRes] = await Promise.all([api.get('/services'), api.get('/services/lits')]);
      setServices(sRes.data);
      setLits(lRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateStatut = async (lit, statut) => {
    try {
      const payload = { statut };
      if (statut === 'occupé') payload.date_admission = new Date().toISOString();
      if (statut === 'disponible') { payload.patient_id = ''; }
      await api.put(`/services/lits/${lit.id}`, payload);
      toast.success(`Lit ${lit.numero} : ${statut}`);
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la mise à jour');
    }
  };

  const getVariant = (s) => ({ 'disponible': 'success', 'occupé': 'error', 'maintenance': 'warning', 'réservé': 'info' }[s] || 'default');
  const serviceName = (id) => services.find(s => s.id === id)?.nom || 'N/A';

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="infirmiere-lits-page">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Gestion des lits</h2>
          <p className="text-gray-600 mt-1">Admissions et libérations des lits d'hospitalisation</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">Total lits</p>
            <p className="text-3xl font-bold text-gray-900">{lits.length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">Disponibles</p>
            <p className="text-3xl font-bold text-emerald-700">{lits.filter(l => l.statut === 'disponible').length}</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <p className="text-sm text-gray-600 mb-1">Occupés</p>
            <p className="text-3xl font-bold text-red-700">{lits.filter(l => l.statut === 'occupé').length}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : lits.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Aucun lit enregistré</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {lits.map((lit) => (
                <div key={lit.id} className="border border-gray-200 rounded-lg p-4" data-testid={`lit-card-${lit.id}`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Bed className="w-5 h-5 text-sky-600" />
                      <h3 className="font-semibold text-gray-900">{lit.numero}</h3>
                    </div>
                    <Badge variant={getVariant(lit.statut)}>{lit.statut}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 flex items-center mb-3"><Building2 className="w-4 h-4 mr-1" />{serviceName(lit.service_id)}</p>
                  <select
                    value={lit.statut}
                    onChange={(e) => updateStatut(lit, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-sky-500"
                    data-testid={`lit-statut-select-${lit.id}`}
                  >
                    <option value="disponible">Disponible</option>
                    <option value="occupé">Occupé</option>
                    <option value="réservé">Réservé</option>
                    <option value="maintenance">Maintenance</option>
                  </select>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default InfirmiereLitsPage;
