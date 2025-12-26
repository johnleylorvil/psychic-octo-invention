import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service de notification pour les rappels de rendez-vous et autres alertes.
    Pour l'instant, ce service log uniquement les notifications.
    Plus tard, il pourra être connecté à un service SMS/Email réel.
    """
    
    @staticmethod
    def send_appointment_reminder(patient_data: Dict[str, Any], appointment_data: Dict[str, Any]) -> bool:
        """
        Envoie un rappel de rendez-vous au patient.
        
        Args:
            patient_data: Données du patient (nom, email, téléphone)
            appointment_data: Données du rendez-vous (date, médecin, motif)
        
        Returns:
            bool: True si la notification a été envoyée avec succès
        """
        try:
            message = f"""
            === RAPPEL DE RENDEZ-VOUS ===
            Patient: {patient_data.get('nom')} {patient_data.get('prenom')}
            Email: {patient_data.get('email')}
            Téléphone: {patient_data.get('telephone')}
            
            Date du rendez-vous: {appointment_data.get('date_rdv')}
            Médecin: Dr. {appointment_data.get('medecin_nom')}
            Type: {appointment_data.get('type_rdv')}
            Motif: {appointment_data.get('motif', 'Non spécifié')}
            
            Veuillez vous présenter 15 minutes avant l'heure du rendez-vous.
            ==============================
            """
            logger.info(message)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du rappel: {str(e)}")
            return False
    
    @staticmethod
    def send_prescription_notification(patient_data: Dict[str, Any], prescription_data: Dict[str, Any]) -> bool:
        """
        Notifie le patient qu'une nouvelle prescription est disponible.
        """
        try:
            message = f"""
            === NOUVELLE PRESCRIPTION ===
            Patient: {patient_data.get('nom')} {patient_data.get('prenom')}
            Email: {patient_data.get('email')}
            
            Une nouvelle prescription vous a été émise par Dr. {prescription_data.get('medecin_nom')}.
            Vous pouvez la retirer à la pharmacie de la clinique.
            ============================
            """
            logger.info(message)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification: {str(e)}")
            return False
    
    @staticmethod
    def send_stock_alert(medicament_data: Dict[str, Any]) -> bool:
        """
        Alerte pour stock faible ou médicament proche de la péremption.
        """
        try:
            message = f"""
            === ALERTE PHARMACIE ===
            Médicament: {medicament_data.get('nom')}
            Type d'alerte: {medicament_data.get('type_alerte')}
            Quantité restante: {medicament_data.get('quantite', 'N/A')}
            Date de péremption: {medicament_data.get('date_peremption', 'N/A')}
            
            Action requise: Réapprovisionnement ou retrait du stock
            =======================
            """
            logger.warning(message)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'alerte: {str(e)}")
            return False
    
    @staticmethod
    def send_blood_stock_alert(blood_type: str, quantity_ml: int) -> bool:
        """
        Alerte pour stock de sang faible.
        """
        try:
            message = f"""
            === ALERTE BANQUE DE SANG ===
            Groupe sanguin: {blood_type}
            Quantité restante: {quantity_ml} ml
            
            ATTENTION: Stock faible - Contactez les donneurs
            ================================
            """
            logger.warning(message)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'alerte: {str(e)}")
            return False