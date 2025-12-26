import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Droplet, Plus, AlertTriangle, User } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { GROUPES_SANGUINS } from '../../utils/constants';

const BloodBankPage = () => {
  const [donneurs, setDonneurs] = useState([]);
  const [stockSummary, setStockSummary] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('donneurs');
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [donneursRes, summaryRes] = await Promise.all([
        api.get('/blood-bank/donneurs'),
        api.get('/blood-bank/stock/summary')
      ]);
      setDonneurs(donneursRes.data);
      setStockSummary(summaryRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStockColor = (statut) => {
    if (statut === 'critique') return 'text-red-600 bg-red-50';
    if (statut === 'faible') return 'text-amber-600 bg-amber-50';
    return 'text-emerald-600 bg-emerald-50';
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Banque de sang</h2>
            <p className="text-gray-600 mt-1">Gestion des donneurs et stocks de sang</p>
          </div>
          <button
            onClick={() => navigate('/admin/blood-bank/donneurs/new')}
            className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
          >
            <Plus className="w-5 h-5" />
            <span>Nouveau donneur</span>
          </button>
        </div>

        {/* Stock Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          {GROUPES_SANGUINS.map(groupe => {
            const stock = stockSummary[groupe];
            return (
              <div key={groupe} className={`rounded-xl p-4 border-2 transition-all hover:shadow-md ${
                stock ? getStockColor(stock.statut) : 'bg-gray-50 text-gray-400'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <Droplet className="w-5 h-5" />
                  <span className="text-xs font-medium">{stock?.nombre_poches || 0} poches</span>
                </div>
                <div className="text-2xl font-bold mb-1">{groupe}</div>
                <div className="text-sm">{stock?.quantite_ml || 0} ml</div>
              </div>
            );
          })}
        </div>

        {/* Alertes critiques */}
        {Object.values(stockSummary).some(s => s.statut === 'critique') && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900 mb-2">Alertes critiques</h3>
                <p className="text-sm text-red-800">
                  {Object.entries(stockSummary).filter(([_, s]) => s.statut === 'critique').map(([g]) => g).join(', ')} : Stock critique - Contacter les donneurs
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('donneurs')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'donneurs'
                    ? 'border-sky-500 text-sky-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Donneurs ({donneurs.length})
              </button>
              <button
                onClick={() => setActiveTab('stock')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'stock'
                    ? 'border-sky-500 text-sky-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Stocks par groupe
              </button>
            </nav>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
              </div>
            ) : activeTab === 'donneurs' ? (
              <div className="overflow-x-auto">
                {donneurs.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">Aucun donneur enregistré</p>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Groupe sanguin</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Téléphone</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dernière donation</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {donneurs.map(donneur => (
                        <tr key={donneur.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div className="flex items-center">
                              <User className="w-4 h-4 text-gray-400 mr-2" />
                              <span className="font-medium text-gray-900">{donneur.nom} {donneur.prenom}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant="info">{donneur.groupe_sanguin}</Badge>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">{donneur.telephone}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {donneur.date_derniere_donation ? new Date(donneur.date_derniere_donation).toLocaleDateString('fr-FR') : 'Jamais'}
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant={donneur.eligible ? 'success' : 'error'}>
                              {donneur.eligible ? 'Éligible' : 'Non éligible'}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(stockSummary).map(([groupe, data]) => (
                  <div key={groupe} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <Droplet className="w-6 h-6 text-red-600" />
                        <h3 className="text-xl font-bold text-gray-900">{groupe}</h3>
                      </div>
                      <Badge variant={data.statut === 'critique' ? 'error' : data.statut === 'faible' ? 'warning' : 'success'}>
                        {data.statut}
                      </Badge>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Quantité totale:</span>
                        <span className="font-semibold">{data.quantite_ml} ml</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Nombre de poches:</span>
                        <span className="font-semibold">{data.nombre_poches}</span>
                      </div>
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

export default BloodBankPage;