import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Save } from 'lucide-react';
import api from '../../services/api';
import { toast } from 'sonner';

const LitForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [services, setServices] = useState([]);
  const [form, setForm] = useState({ numero: '', service_id: '', statut: 'disponible', notes: '' });

  useEffect(() => {
    api.get('/services').then(res => {
      setServices(res.data);
      if (res.data.length > 0) setForm(prev => ({ ...prev, service_id: res.data[0].id }));
    }).catch(err => console.error(err));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/services/lits', form);
      toast.success('Lit créé avec succès');
      navigate('/admin/services');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="lit-form-page">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/admin/services')} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ArrowLeft className="w-5 h-5" /></button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nouveau lit</h2>
            <p className="text-gray-600 mt-1">Ajouter un lit d'hospitalisation</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Numéro du lit *</label>
              <input name="numero" value={form.numero} onChange={handleChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="lit-numero" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Service *</label>
              <select name="service_id" value={form.service_id} onChange={handleChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="lit-service">
                <option value="">Sélectionner un service</option>
                {services.map(s => <option key={s.id} value={s.id}>{s.nom}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Statut</label>
              <select name="statut" value={form.statut} onChange={handleChange} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500">
                <option value="disponible">Disponible</option>
                <option value="maintenance">Maintenance</option>
                <option value="réservé">Réservé</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
              <textarea name="notes" value={form.notes} onChange={handleChange} rows={2} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
          </div>
          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button type="button" onClick={() => navigate('/admin/services')} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
            <button type="submit" disabled={loading} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 shadow-lg disabled:opacity-50" data-testid="submit-lit-btn">
              <Save className="w-5 h-5" /><span>{loading ? 'Enregistrement...' : 'Enregistrer'}</span>
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
};

export default LitForm;
