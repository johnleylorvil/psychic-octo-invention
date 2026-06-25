import { toast } from 'sonner';

// Génération PDF via la fonction d'impression du navigateur (Imprimer -> Enregistrer en PDF).
// Architecture prête à être branchée sur un service serveur (ReportLab / wkhtmltopdf) plus tard.
export const generatePDF = (title, contentHTML) => {
  const win = window.open('', '_blank', 'width=900,height=650');
  if (!win) {
    toast.error("Veuillez autoriser les fenêtres pop-up pour exporter en PDF");
    return;
  }

  win.document.write(`
    <html lang="fr">
      <head>
        <meta charset="utf-8" />
        <title>${title}</title>
        <style>
          * { font-family: 'Segoe UI', Arial, sans-serif; color: #1f2937; }
          body { padding: 40px; }
          .header { display:flex; align-items:center; justify-content:space-between; border-bottom: 3px solid #0ea5e9; padding-bottom: 16px; margin-bottom: 24px; }
          .brand { font-size: 22px; font-weight: 700; color: #0ea5e9; }
          h1 { font-size: 20px; margin: 0 0 4px; }
          .muted { color: #6b7280; font-size: 13px; }
          table { width: 100%; border-collapse: collapse; margin-top: 16px; }
          th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #e5e7eb; font-size: 14px; }
          th { background: #f0f9ff; color: #0369a1; }
          .row { display:flex; justify-content:space-between; padding: 6px 0; font-size: 14px; }
          .label { color:#6b7280; }
          .total { margin-top: 18px; font-size: 18px; font-weight: 700; text-align: right; }
          .footer { margin-top: 40px; font-size: 12px; color:#9ca3af; text-align:center; }
        </style>
      </head>
      <body>
        <div class="header">
          <div class="brand">Clinique+</div>
          <div class="muted">Généré le ${new Date().toLocaleString('fr-FR')}</div>
        </div>
        ${contentHTML}
        <div class="footer">Document généré automatiquement par le Système de Gestion de Clinique.</div>
      </body>
    </html>
  `);
  win.document.close();
  win.focus();
  setTimeout(() => win.print(), 400);
  toast.success('Export PDF prêt');
};

export const exportFacturePDF = (facture) => {
  const items = (facture.items || []).map(it => `
    <tr>
      <td>${it.description || it.designation || it.libelle || 'Prestation'}</td>
      <td>${it.quantite ?? 1}</td>
      <td>${(it.montant || it.prix_unitaire || it.prix || 0).toLocaleString()} FCFA</td>
    </tr>`).join('');

  const content = `
    <h1>Facture ${facture.numero_facture || ''}</h1>
    <p class="muted">Statut : ${facture.statut} · Date : ${new Date(facture.created_at).toLocaleDateString('fr-FR')}</p>
    <table>
      <thead><tr><th>Désignation</th><th>Qté</th><th>Montant</th></tr></thead>
      <tbody>${items || '<tr><td colspan="3">Aucun détail</td></tr>'}</tbody>
    </table>
    <div class="total">Total : ${(facture.montant_total || 0).toLocaleString()} FCFA</div>
  `;
  generatePDF(`Facture ${facture.numero_facture || ''}`, content);
};

export const exportPrescriptionPDF = (prescription, medecinNom = '') => {
  const meds = (prescription.medicaments || prescription.items || []).map(m => `
    <tr>
      <td>${m.nom || m.medicament_nom || m.designation || 'Médicament'}</td>
      <td>${m.posologie || m.dosage || '-'}</td>
      <td>${m.duree || m.frequence || '-'}</td>
    </tr>`).join('');

  const content = `
    <h1>Ordonnance médicale</h1>
    <p class="muted">Médecin : Dr. ${medecinNom || prescription.medecin_nom || ''} · Date : ${new Date(prescription.created_at).toLocaleDateString('fr-FR')}</p>
    <table>
      <thead><tr><th>Médicament</th><th>Posologie</th><th>Durée</th></tr></thead>
      <tbody>${meds || '<tr><td colspan="3">Voir notes ci-dessous</td></tr>'}</tbody>
    </table>
    ${prescription.notes ? `<p style="margin-top:16px"><strong>Notes :</strong> ${prescription.notes}</p>` : ''}
  `;
  generatePDF('Ordonnance', content);
};
