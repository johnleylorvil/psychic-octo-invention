import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { FileText, Pill, FileDown } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { exportPrescriptionPDF } from '../../utils/pdfExport';

const PharmacienPrescriptionsList = () => {
  const [prescriptions, setPrescriptions] = useState([]);
  const [patients, setPatients] = useState({});
  const [medecins, setMedecins] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [pRes, patRes, medRes] = await Promise.all([
        api.get('/consultations/prescriptions/'),
        api.get('/patients'),
        api.get('/users?role=médecin')
      ]);
      setPrescriptions(pRes.data);
      const patMap = {}; patRes.data.forEach(p => { patMap[p.id] = p; }); setPatients(patMap);
      const medMap = {}; medRes.data.forEach(m => { medMap[m.id] = m; }); setMedecins(medMap);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6" data-testid="pharmacien-prescriptions-page">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Prescriptions</h2>
          <p className="text-gray-600 mt-1">Ordonnances à préparer</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <FileText className="w-6 h-6 text-sky-600" />
            <h3 className="text-lg font-semibold text-gray-900">Total : {prescriptions.length} ordonnance(s)</h3>
          </div>
          {loading ? (
            <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div></div>
          ) : prescriptions.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Aucune prescription</p>
          ) : (
            <div className="space-y-4">
              {prescriptions.map(p => {
                const medecin = medecins[p.medecin_id];
                return (
                  <div key={p.id} className="border border-gray-200 rounded-lg p-4" data-testid={`prescription-card-${p.id}`}>
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <p className="text-sm font-semibold text-gray-900">Patient : {patients[p.patient_id]?.numero_dossier || 'N/A'}</p>
                        <p className="text-xs text-gray-500">Dr. {medecin?.nom} {medecin?.prenom} · {new Date(p.created_at).toLocaleDateString('fr-FR')}</p>
                      </div>
                      <button
                        onClick={() => exportPrescriptionPDF(p, `${medecin?.nom || ''} ${medecin?.prenom || ''}`)}
                        className="flex items-center space-x-1 text-sky-600 hover:text-sky-800 text-sm"
                        data-testid={`export-prescription-${p.id}`}
                      >
                        <FileDown className="w-4 h-4" /><span>PDF</span>
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {(p.medicaments || []).map((m, idx) => (
                        <Badge key={idx} variant="info">
                          <Pill className="w-3 h-3 inline mr-1" />{m.nom} {m.dosage} ({m.frequence}, {m.duree})
                        </Badge>
                      ))}
                    </div>
                    {p.instructions_generales && <p className="text-sm text-gray-600 mt-3">Instructions : {p.instructions_generales}</p>}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
};

export default PharmacienPrescriptionsList;
