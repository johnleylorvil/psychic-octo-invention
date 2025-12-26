import React, { useEffect, useState } from 'react';
import MainLayout from '../../components/Layout/MainLayout';
import { Users, Plus, UserCheck, UserX } from 'lucide-react';
import { Badge } from '../../components/common/Card';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';
import { ROLES, ROLE_LABELS } from '../../utils/constants';
import { toast } from 'sonner';

const UsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterRole, setFilterRole] = useState('');
  const [filterActif, setFilterActif] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadUsers();
  }, [filterRole, filterActif]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filterRole) params.role = filterRole;
      if (filterActif !== '') params.actif = filterActif === 'true';
      
      const response = await api.get('/users', { params });
      setUsers(response.data);
    } catch (error) {
      console.error('Erreur:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (userId, currentStatus) => {
    try {
      await api.put(`/users/${userId}`, { actif: !currentStatus });
      toast.success(currentStatus ? 'Utilisateur désactivé' : 'Utilisateur activé');
      loadUsers();
    } catch (error) {
      toast.error('Erreur lors de la modification');
    }
  };

  const getRoleColor = (role) => {
    const colors = {
      'admin': 'error',
      'médecin': 'info',
      'infirmière': 'success',
      'pharmacien': 'warning',
      'comptable': 'default',
      'patient': 'default'
    };
    return colors[role] || 'default';
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Utilisateurs</h2>
            <p className="text-gray-600 mt-1">Gestion des comptes utilisateurs</p>
          </div>
          <button
            onClick={() => navigate('/admin/users/new')}
            className="bg-gradient-to-r from-sky-600 to-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:from-sky-700 hover:to-emerald-700 transition-all flex items-center space-x-2 shadow-lg"
          >
            <Plus className="w-5 h-5" />
            <span>Nouvel utilisateur</span>
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
          {Object.entries(ROLES).map(([key, role]) => {
            const count = users.filter(u => u.role === role).length;
            return (
              <div key={role} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-600 mb-1">{ROLE_LABELS[role]}</p>
                  <p className="text-2xl font-bold text-gray-900">{count}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Filtres */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div className="flex space-x-4">
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            >
              <option value="">Tous les rôles</option>
              {Object.entries(ROLES).map(([key, role]) => (
                <option key={role} value={role}>{ROLE_LABELS[role]}</option>
              ))}
            </select>
            <select
              value={filterActif}
              onChange={(e) => setFilterActif(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
            >
              <option value="">Tous les statuts</option>
              <option value="true">Actifs</option>
              <option value="false">Inactifs</option>
            </select>
          </div>
        </div>

        {/* Liste des utilisateurs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600"></div>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Aucun utilisateur trouvé</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rôle</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Téléphone</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Spécialité</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Statut</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {users.map(user => (
                    <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{user.prenom} {user.nom}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {user.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant={getRoleColor(user.role)}>
                          {ROLE_LABELS[user.role] || user.role}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {user.telephone || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {user.specialite || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Badge variant={user.actif ? 'success' : 'error'}>
                          {user.actif ? 'Actif' : 'Inactif'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                        <button
                          onClick={() => toggleUserStatus(user.id, user.actif)}
                          className={`inline-flex items-center px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                            user.actif
                              ? 'text-red-700 bg-red-50 hover:bg-red-100'
                              : 'text-emerald-700 bg-emerald-50 hover:bg-emerald-100'
                          }`}
                        >
                          {user.actif ? (
                            <><UserX className="w-4 h-4 mr-1" /> Désactiver</>
                          ) : (
                            <><UserCheck className="w-4 h-4 mr-1" /> Activer</>
                          )}
                        </button>
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

export default UsersPage;