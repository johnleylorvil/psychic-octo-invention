import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Building2, Plus, Bed } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';

const ServicesLitsPage = () => {
  const [services, setServices] = useState([]);
  const [lits, setLits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('lits');
  const [filterService, setFilterService] = useState('');
  const [filterStatut, setFilterStatut] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, [filterService, filterStatut]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterService) params.service_id = filterService;
      if (filterStatut) params.statut = filterStatut;
      
      const [servicesRes, litsRes] = await Promise.all([
        api.get('/services'),
        api.get('/services/lits', { params })
      ]);
      
      setServices(servicesRes.data);
      setLits(litsRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatutColor = (statut) => {
    const colors = {
      'disponible': 'success',
      'occupé': 'error',
      'maintenance': 'warning',
      'réservé': 'info'
    };
    return colors[statut] || 'default';
  };

  const getStatutLabel = (statut) => {
    const labels = {
      'disponible': 'Disponible',
      'occupé': 'Occupé',
      'maintenance': 'Maintenance',
      'réservé': 'Réservé'
    };
    return labels[statut] || statut;
  };

  const getServiceById = (serviceId) => {
    return services.find(s => s.id === serviceId);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Services & Lits</h2>
            <p className="text-gray-600 mt-1">Gestion des services et lits d'hospitalisation</p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={() => navigate('/admin/services/new')}
              className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-4 py-2 rounded-lg font-medium hover:from-purple-700 hover:to-purple-800 transition-all flex items-center space-x-2 shadow-lg"
            >
              <Plus className="w-5 h-5" />
              <span>Nouveau service</span>
            </button>
            <button
              onClick={() => navigate('/admin/services/lits/new')}
              className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
            >
              <Plus className="w-5 h-5" />
              <span>Nouveau lit</span>
            </button>
          </div>
        </div>

        {/* Stats rapides */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Services actifs</p>
                <p className="text-3xl font-bold text-gray-900">{services.length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                <Building2 className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Total lits</p>
                <p className="text-3xl font-bold text-gray-900">{lits.length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center">
                <Bed className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Lits disponibles</p>
                <p className="text-3xl font-bold text-emerald-900">{lits.filter(l => l.statut === 'disponible').length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
                <Bed className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Lits occupés</p>
                <p className="text-3xl font-bold text-red-900">{lits.filter(l => l.statut === 'occupé').length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center">
                <Bed className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('lits')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'lits'
                    ? 'border-sky-500 text-sky-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Lits ({lits.length})
              </button>
              <button
                onClick={() => setActiveTab('services')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'services'
                    ? 'border-sky-500 text-sky-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Services ({services.length})
              </button>
            </nav>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
              </div>
            ) : activeTab === 'lits' ? (
              <div>
                {/* Filtres */}
                <div className="mb-6 flex space-x-4">
                  <select
                    value={filterService}
                    onChange={(e) => setFilterService(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
                  >
                    <option value="">Tous les services</option>
                    {services.map(s => (
                      <option key={s.id} value={s.id}>{s.nom}</option>
                    ))}
                  </select>
                  <select
                    value={filterStatut}
                    onChange={(e) => setFilterStatut(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
                  >
                    <option value="">Tous les statuts</option>
                    <option value="disponible">Disponible</option>
                    <option value="occupé">Occupé</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="réservé">Réservé</option>
                  </select>
                </div>

                {/* Liste des lits */}
                {lits.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">Aucun lit trouvé</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {lits.map(lit => {
                      const service = getServiceById(lit.service_id);
                      return (
                        <div key={lit.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center space-x-2">
                              <Bed className="w-5 h-5 text-sky-600" />
                              <h3 className="font-semibold text-gray-900">{lit.numero}</h3>
                            </div>
                            <Badge variant={getStatutColor(lit.statut)}>
                              {getStatutLabel(lit.statut)}
                            </Badge>
                          </div>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Service:</span>
                              <span className="font-medium">{service?.nom || 'N/A'}</span>
                            </div>
                            {lit.patient_id && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Patient:</span>
                                <span className="font-medium text-xs">ID: {lit.patient_id.substring(0, 8)}...</span>
                              </div>
                            )}
                            {lit.date_admission && (
                              <div className="flex justify-between">
                                <span className="text-gray-600">Admission:</span>
                                <span className="font-medium">{new Date(lit.date_admission).toLocaleDateString('fr-FR')}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {services.map(service => (
                  <div key={service.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center">
                          <Building2 className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{service.nom}</h3>
                          <p className="text-sm text-gray-600">Étage {service.etage || 'N/A'}</p>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-4">{service.description || 'Aucune description'}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Capacité:</span>
                      <span className="font-semibold">{service.nombre_lits} lits</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default ServicesLitsPage;