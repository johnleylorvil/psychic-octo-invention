import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { DollarSign, FileText } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const PatientFacturesList = () => {
  const { user } = useAuth();
  const [factures, setFactures] = useState([]);
  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const patientsRes = await api.get('/patients');
      const myPatient = patientsRes.data.find(p => p.user_id === user.id);
      setPatientData(myPatient);

      if (myPatient) {
        const facturesRes = await api.get('/billing/factures', { params: { patient_id: myPatient.id } });
        setFactures(facturesRes.data);
      }
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatutVariant = (statut) => {
    const variants = {
      'en_attente': 'warning',
      'payée': 'success',
      'partiellement_payée': 'info',
      'annulée': 'error'
    };
    return variants[statut] || 'default';
  };

  const getStatutLabel = (statut) => {
    const labels = {
      'en_attente': 'En attente',
      'payée': 'Payée',
      'partiellement_payée': 'Partiellement payée',
      'annulée': 'Annulée'
    };
    return labels[statut] || statut;
  };

  const totalImpaye = factures
    .filter(f => f.statut === 'en_attente' || f.statut === 'partiellement_payée')
    .reduce((sum, f) => sum + f.montant_total, 0);

  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Mes factures</h2>
          <p className="text-gray-600 mt-1">Historique de vos factures et paiements</p>
        </div>

        {/* Résumé */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Total factures</p>
                <p className="text-3xl font-bold text-gray-900">{factures.length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Factures payées</p>
                <p className="text-3xl font-bold text-emerald-900">{factures.filter(f => f.statut === 'payée').length}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Montant impayé</p>
                <p className="text-3xl font-bold text-red-900">{totalImpaye.toLocaleString()} F</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Liste des factures */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : factures.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucune facture</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Numéro</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Montant</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Items</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {factures.map((facture) => (
                    <tr key={facture.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{facture.numero_facture}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(facture.created_at).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-gray-900">{facture.montant_total.toLocaleString()} FCFA</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant={getStatutVariant(facture.statut)}>
                          {getStatutLabel(facture.statut)}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {facture.items.length} service(s)
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default PatientFacturesList;