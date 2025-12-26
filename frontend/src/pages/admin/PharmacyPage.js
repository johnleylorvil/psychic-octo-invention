import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Pill, AlertTriangle, Package } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';

const PharmacyPage = () => {
  const [medicaments, setMedicaments] = useState([]);
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('medicaments');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [medsRes, alertsRes] = await Promise.all([
        api.get('/pharmacy/medicaments'),
        api.get('/pharmacy/alerts')
      ]);
      setMedicaments(medsRes.data);
      setAlerts(alertsRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Pharmacie</h2>
          <p className="text-gray-600 mt-1">Gestion des médicaments et stocks</p>
        </div>

        {/* Alertes */}
        {alerts && alerts.total_alertes > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-900 mb-2">Alertes importantes</h3>
                <div className="space-y-2">
                  {alerts.stock_faible.length > 0 && (
                    <p className="text-sm text-red-800">
                      ⚠️ {alerts.stock_faible.length} médicament(s) en stock faible
                    </p>
                  )}
                  {alerts.peremption_proche.length > 0 && (
                    <p className="text-sm text-red-800">
                      ⚠️ {alerts.peremption_proche.length} lot(s) proche de la péremption
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('medicaments')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'medicaments'
                    ? 'border-sky-500 text-sky-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Médicaments
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'alerts'
                    ? 'border-sky-500 text-sky-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Alertes ({alerts?.total_alertes || 0})
              </button>
            </nav>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
              </div>
            ) : activeTab === 'medicaments' ? (
              <div className="space-y-4">
                {medicaments.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">Aucun médicament trouvé</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {medicaments.map((med) => (
                      <div key={med.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            <Pill className="w-5 h-5 text-sky-600" />
                            <h3 className="font-semibold text-gray-900">{med.nom}</h3>
                          </div>
                          <Badge variant="info">{med.forme || 'N/A'}</Badge>
                        </div>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">Dosage:</span>
                            <span className="font-medium">{med.dosage || 'N/A'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Prix unitaire:</span>
                            <span className="font-medium">{med.prix_unitaire} FCFA</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Seuil min:</span>
                            <span className="font-medium">{med.seuil_stock_min}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Fabricant:</span>
                            <span className="font-medium text-xs">{med.fabricant || 'N/A'}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {/* Alertes stock faible */}
                {alerts?.stock_faible.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <Package className="w-5 h-5 mr-2 text-red-600" />
                      Stock faible
                    </h3>
                    <div className="space-y-2">
                      {alerts.stock_faible.map((alert, idx) => (
                        <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium text-red-900">{alert.nom}</p>
                              <p className="text-sm text-red-700">Stock actuel: {alert.quantite_actuelle} (seuil: {alert.seuil_min})</p>
                            </div>
                            <Badge variant="error">Critique</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Alertes péremption */}
                {alerts?.peremption_proche.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
                      <AlertTriangle className="w-5 h-5 mr-2 text-amber-600" />
                      Péremption proche (30 jours)
                    </h3>
                    <div className="space-y-2">
                      {alerts.peremption_proche.map((alert, idx) => (
                        <div key={idx} className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium text-amber-900">{alert.medicament_nom}</p>
                              <p className="text-sm text-amber-700">
                                Lot: {alert.numero_lot} | Quantité: {alert.quantite} | Péremption: {new Date(alert.date_peremption).toLocaleDateString('fr-FR')}
                              </p>
                            </div>
                            <Badge variant="warning">Urgent</Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {(!alerts?.stock_faible.length && !alerts?.peremption_proche.length) && (
                  <div className="text-center py-8">
                    <p className="text-gray-500">Aucune alerte pour le moment</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default PharmacyPage;