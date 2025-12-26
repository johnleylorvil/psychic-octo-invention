import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { 
  Home, Users, Calendar, Stethoscope, Pill, 
  DollarSign, Droplet, Building2, Activity,
  FileText, LogOut, Menu, X
} from 'lucide-react';
import { ROLES } from '../../utils/constants';

const Sidebar = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const getMenuItems = () => {
    const items = [];

    switch (user?.role) {
      case ROLES.ADMIN:
        items.push(
          { icon: Home, label: 'Tableau de bord', path: '/admin' },
          { icon: Users, label: 'Utilisateurs', path: '/admin/users' },
          { icon: Users, label: 'Patients', path: '/admin/patients' },
          { icon: Building2, label: 'Services & Lits', path: '/admin/services' },
          { icon: Calendar, label: 'Rendez-vous', path: '/admin/appointments' },
          { icon: Pill, label: 'Pharmacie', path: '/admin/pharmacy' },
          { icon: Droplet, label: 'Banque de sang', path: '/admin/blood-bank' },
          { icon: DollarSign, label: 'Facturation', path: '/admin/billing' }
        );
        break;
      
      case ROLES.MEDECIN:
        items.push(
          { icon: Home, label: 'Tableau de bord', path: '/medecin' },
          { icon: Users, label: 'Mes patients', path: '/medecin/patients' },
          { icon: Calendar, label: 'Mes rendez-vous', path: '/medecin/appointments' },
          { icon: Stethoscope, label: 'Consultations', path: '/medecin/consultations' },
          { icon: FileText, label: 'Prescriptions', path: '/medecin/prescriptions' }
        );
        break;
      
      case ROLES.INFIRMIERE:
        items.push(
          { icon: Home, label: 'Tableau de bord', path: '/infirmiere' },
          { icon: Users, label: 'Patients', path: '/infirmiere/patients' },
          { icon: Calendar, label: 'Rendez-vous', path: '/infirmiere/appointments' },
          { icon: Building2, label: 'Lits', path: '/infirmiere/lits' },
          { icon: Droplet, label: 'Banque de sang', path: '/infirmiere/blood-bank' }
        );
        break;
      
      case ROLES.PHARMACIEN:
        items.push(
          { icon: Home, label: 'Tableau de bord', path: '/pharmacien' },
          { icon: Pill, label: 'Médicaments', path: '/pharmacien/medicaments' },
          { icon: Activity, label: 'Stocks', path: '/pharmacien/stocks' },
          { icon: FileText, label: 'Prescriptions', path: '/pharmacien/prescriptions' }
        );
        break;
      
      case ROLES.COMPTABLE:
        items.push(
          { icon: Home, label: 'Tableau de bord', path: '/comptable' },
          { icon: DollarSign, label: 'Factures', path: '/comptable/factures' },
          { icon: FileText, label: 'Paiements', path: '/comptable/paiements' }
        );
        break;
      
      case ROLES.PATIENT:
        items.push(
          { icon: Home, label: 'Tableau de bord', path: '/patient' },
          { icon: Calendar, label: 'Mes rendez-vous', path: '/patient/appointments' },
          { icon: FileText, label: 'Mes consultations', path: '/patient/consultations' },
          { icon: DollarSign, label: 'Mes factures', path: '/patient/factures' }
        );
        break;
      
      default:
        break;
    }

    return items;
  };

  const menuItems = getMenuItems();

  return (
    <>
      {/* Overlay mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside
        className={`
          fixed left-0 top-0 h-full bg-white border-r border-gray-200 z-50
          transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:block
          w-64
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-2">
              <Activity className="w-8 h-8 text-sky-600" />
              <span className="font-bold text-xl text-gray-800">Clinique+</span>
            </div>
            <button
              onClick={onClose}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
              data-testid="close-sidebar-btn"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* User Info */}
          <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-sky-50 to-emerald-50">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-sky-500 to-emerald-500 flex items-center justify-center text-white font-semibold">
                {user?.prenom?.[0]}{user?.nom?.[0]}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user?.prenom} {user?.nom}
                </p>
                <p className="text-xs text-gray-600 truncate">
                  {user?.role}
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                    ${isActive 
                      ? 'bg-gradient-to-r from-sky-600 to-emerald-600 text-white shadow-md' 
                      : 'text-gray-700 hover:bg-gray-100'
                    }
                  `}
                  onClick={() => window.innerWidth < 1024 && onClose()}
                  data-testid={`nav-${item.path.split('/').pop()}`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={logout}
              className="flex items-center space-x-3 px-4 py-3 w-full rounded-lg text-red-600 hover:bg-red-50 transition-colors"
              data-testid="logout-btn"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Déconnexion</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;