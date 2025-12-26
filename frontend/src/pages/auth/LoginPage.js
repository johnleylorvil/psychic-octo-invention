import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Activity, Mail, Lock, AlertCircle } from 'lucide-react';
import { ROLES } from '../../utils/constants';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await login(email, password);
      
      // Redirection selon le rôle
      const role = data.user.role;
      if (role === ROLES.ADMIN) navigate('/admin');
      else if (role === ROLES.MEDECIN) navigate('/medecin');
      else if (role === ROLES.INFIRMIERE) navigate('/infirmiere');
      else if (role === ROLES.PHARMACIEN) navigate('/pharmacien');
      else if (role === ROLES.COMPTABLE) navigate('/comptable');
      else if (role === ROLES.PATIENT) navigate('/patient');
    } catch (err) {
      setError(err.response?.data?.detail || 'Email ou mot de passe incorrect');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-emerald-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo et titre */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-sky-500 to-emerald-500 rounded-2xl shadow-lg mb-4">
            <Activity className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Système de Gestion de Clinique</h1>
          <p className="text-gray-600">Connectez-vous à votre compte</p>
        </div>

        {/* Formulaire de connexion */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3" data-testid="login-error">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Adresse email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all"
                  placeholder="votre@email.com"
                  required
                  data-testid="email-input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all"
                  placeholder="••••••••"
                  required
                  data-testid="password-input"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-sky-600 to-emerald-600 text-white py-3 rounded-lg font-semibold hover:from-sky-700 hover:to-emerald-700 focus:ring-4 focus:ring-sky-300 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              data-testid="login-submit-btn"
            >
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>
        </div>

        {/* Informations de test */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs font-semibold text-blue-900 mb-2">Ð Comptes de test :</p>
          <div className="grid grid-cols-2 gap-2 text-xs text-blue-800">
            <div>
              <p className="font-medium">Admin:</p>
              <p>admin1@clinique.com</p>
            </div>
            <div>
              <p className="font-medium">Médecin:</p>
              <p>medecin1@clinique.com</p>
            </div>
            <div>
              <p className="font-medium">Patient:</p>
              <p>patient1@email.com</p>
            </div>
            <div>
              <p className="font-medium">Mot de passe:</p>
              <p className="font-semibold">admin123 / medecin123 / patient123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;