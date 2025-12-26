export const ROLES = {
  ADMIN: 'admin',
  MEDECIN: 'médecin',
  INFIRMIERE: 'infirmière',
  PHARMACIEN: 'pharmacien',
  COMPTABLE: 'comptable',
  PATIENT: 'patient'
};

export const ROLE_LABELS = {
  [ROLES.ADMIN]: 'Administrateur',
  [ROLES.MEDECIN]: 'Médecin',
  [ROLES.INFIRMIERE]: 'Infirmière',
  [ROLES.PHARMACIEN]: 'Pharmacien',
  [ROLES.COMPTABLE]: 'Comptable',
  [ROLES.PATIENT]: 'Patient'
};

export const STATUT_RDV = {
  PLANIFIE: 'planifié',
  CONFIRME: 'confirmé',
  ANNULE: 'annulé',
  TERMINE: 'terminé',
  EN_ATTENTE: 'en_attente'
};

export const GROUPES_SANGUINS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export const STATUT_FACTURE = {
  EN_ATTENTE: 'en_attente',
  PAYEE: 'payée',
  PARTIELLEMENT_PAYEE: 'partiellement_payée',
  ANNULEE: 'annulée'
};