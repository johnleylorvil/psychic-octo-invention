import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Package, AlertTriangle, Pill } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';

const PharmacienStocksPage = () => {
  const [medicaments, setMedicaments] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [alerts, setAlerts] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [medsRes, stockRes, alertsRes] = await Promise.all([
        api.get('/pharmacy/medicaments'),
        api.get('/pharmacy/stock'),
        api.get('/pharmacy/alerts')
      ]);
      setMedicaments(medsRes.data);
      setStocks(stockRes.data);
      setAlerts(alertsRes.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const medName = (id) => medicaments.find(m => m.id === id)?.nom || 'N/A';
  const totalForMed = (id) => stocks.filter(s => s.medicament_id === id).reduce((sum, s) => sum + (s.quantite || 0), 0);

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="pharmacien-stocks-page">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Stocks</h2>
          <p className="text-gray-600 mt-1">Gestion des stocks et alertes</p>
        </div>

        {alerts && alerts.total_alertes > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4" data-testid="stock-alerts">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-900 mb-2">Alertes ({alerts.total_alertes})</h3>
                {alerts.stock_faible.length > 0 && <p className="text-sm text-red-800">{alerts.stock_faible.length} médicament(s) en stock faible</p>}
                {alerts.peremption_proche.length > 0 && <p className="text-sm text-red-800">{alerts.peremption_proche.length} lot(s) proche de la péremption</p>}
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div></div>
        ) : (
          <>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center"><Package className="w-5 h-5 mr-2 text-sky-600" />Quantités par médicament</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {medicaments.map(med => {
                  const total = totalForMed(med.id);
                  const low = total < (med.seuil_stock_min || 10);
                  return (
                    <div key={med.id} className={`border rounded-lg p-4 ${low ? 'border-red-200 bg-red-50' : 'border-gray-200'}`} data-testid={`stock-med-${med.id}`}>
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2"><Pill className="w-4 h-4 text-sky-600" /><span className="font-medium text-gray-900">{med.nom}</span></div>
                        {low && <Badge variant="error">Faible</Badge>}
                      </div>
                      <p className="text-sm text-gray-600">Quantité totale : <span className="font-semibold">{total}</span> (seuil {med.seuil_stock_min})</p>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Lots en stock ({stocks.length})</h3>
              {stocks.length === 0 ? (
                <p className="text-center text-gray-500 py-8">Aucun lot enregistré</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Médicament</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lot</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quantité</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Péremption</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {stocks.map(s => (
                        <tr key={s.id} className="hover:bg-gray-50" data-testid={`stock-row-${s.id}`}>
                          <td className="px-6 py-4 text-sm text-gray-900">{medName(s.medicament_id)}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{s.numero_lot}</td>
                          <td className="px-6 py-4 text-sm font-medium">{s.quantite}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{s.date_peremption ? new Date(s.date_peremption).toLocaleDateString('fr-FR') : 'N/A'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </MainLayout>
  );
};

export default PharmacienStocksPage;
