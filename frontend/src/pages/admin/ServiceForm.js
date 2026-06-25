import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/Layout/MainLayout';
import { ArrowLeft, Save } from 'lucide-react';
import api from '../../services/api';
import { toast } from 'sonner';

const ServiceForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ nom: '', description: '', etage: '', nombre_lits: 0 });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: name === 'nombre_lits' ? Number(value) : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/services/', form);
      toast.success('Service créé avec succès');
      navigate('/admin/services');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-3xl mx-auto space-y-6" data-testid="service-form-page">
        <div className="flex items-center space-x-4">
          <button onClick={() => navigate('/admin/services')} className="p-2 hover:bg-gray-100 rounded-lg transition-colors"><ArrowLeft className="w-5 h-5" /></button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nouveau service</h2>
            <p className="text-gray-600 mt-1">Créer un service hospitalier</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Nom du service *</label>
              <input name="nom" value={form.nom} onChange={handleChange} required className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" data-testid="service-nom" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Étage</label>
              <input name="etage" value={form.etage} onChange={handleChange} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Nombre de lits</label>
              <input name="nombre_lits" type="number" value={form.nombre_lits} onChange={handleChange} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
              <textarea name="description" value={form.description} onChange={handleChange} rows={3} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500" />
            </div>
          </div>
          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button type="button" onClick={() => navigate('/admin/services')} className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50">Annuler</button>
            <button type="submit" disabled={loading} className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium flex items-center space-x-2 shadow-lg disabled:opacity-50" data-testid="submit-service-btn">
              <Save className="w-5 h-5" /><span>{loading ? 'Enregistrement...' : 'Enregistrer'}</span>
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
};

export default ServiceForm;
