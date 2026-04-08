'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import api from '@/lib/api';
import { toast, Toaster } from 'react-hot-toast';

interface Coefficient {
  niveau_complexite: number;
  type_activite: string;
  coefficient: number;
}

interface Quota {
  grade: string;
  statut: string;
  quota_heures: number;
}

export default function ConfigPage() {
  const [coefficients, setCoefficients] = useState<Coefficient[]>([]);
  const [quotas, setQuotas] = useState<Quota[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Added newly for UI interactions
  const grades = [
    'Assistant',
    'Maître-Assistant',
    'Maître de Conférences',
    'Professeur',
  ];
  const statuts = ['Permanent', 'Vacataire'];
  const niveaux = [1, 2, 3];
  const typesActivite = ['creation', 'mise_a_jour'];

  const fetcData = async () => {
    setIsLoading(true);
    try {
      const [coefRes, quotasRes] = await Promise.all([
        api.get('/config/coefficients'),
        api.get('/config/quotas'),
      ]);
      setCoefficients(coefRes.data);
      setQuotas(quotasRes.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des configurations');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetcData();
  }, []);

  const handleCoefChange = (niveau: number, type: string, value: number) => {
    setCoefficients(prev => {
      const existing = prev.find(c => c.niveau_complexite === niveau && c.type_activite === type);
      if (existing) {
        return prev.map(c => 
          (c.niveau_complexite === niveau && c.type_activite === type) 
            ? { ...c, coefficient: value } 
            : c
        );
      } else {
        return [...prev, { niveau_complexite: niveau, type_activite: type, coefficient: value }];
      }
    });
  };

  const handleQuotaChange = (grade: string, statut: string, value: number) => {
    setQuotas(prev => {
      const existing = prev.find(q => q.grade === grade && q.statut === statut);
      if (existing) {
        return prev.map(q => 
          (q.grade === grade && q.statut === statut) 
            ? { ...q, quota_heures: value } 
            : q
        );
      } else {
        return [...prev, { grade, statut, quota_heures: value }];
      }
    });
  };

  const saveCoefficients = async () => {
    try {
      await api.put('/config/coefficients', coefficients);
      toast.success('Coefficients mis à jour');
    } catch (err) {
      toast.error('Erreur lors de la sauvegarde des coefficients');
    }
  };

  const saveQuotas = async () => {
    try {
      await api.put('/config/quotas', quotas);
      toast.success('Quotas statutaires mis à jour');
    } catch (err) {
      toast.error('Erreur lors de la sauvegarde des quotas');
    }
  };

  const getCoef = (niveau: number, type: string) => {
    return coefficients.find(c => c.niveau_complexite === niveau && c.type_activite === type)?.coefficient || 0;
  };

  const getQuota = (grade: string, statut: string) => {
    return quotas.find(q => q.grade === grade && q.statut === statut)?.quota_heures || 0;
  };

  return (
    <MainLayout>
      <Toaster position="top-right" />
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configuration Globale</h1>
          <p className="text-gray-500 text-sm mt-1">Gérez les coefficients horaires et les quotas statutaires</p>
        </div>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-gray-500 bg-white rounded-xl shadow-sm border border-gray-100">Chargement...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Coefficients Horaires */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-gray-800">Coefficients Horaires</h2>
              <button 
                onClick={saveCoefficients}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition"
              >
                Sauvegarder
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100">
                    <th className="p-3 font-semibold text-gray-600 text-sm">Niveau</th>
                    <th className="p-3 font-semibold text-gray-600 text-sm">Création</th>
                    <th className="p-3 font-semibold text-gray-600 text-sm">Mise à jour</th>
                  </tr>
                </thead>
                <tbody>
                  {niveaux.map((niveau) => (
                    <tr key={`niveau-${niveau}`} className="border-b border-gray-50">
                      <td className="p-3 font-medium text-gray-700">Niveau {niveau}</td>
                      <td className="p-3">
                        <input 
                          type="number" 
                          step="0.01"
                          value={getCoef(niveau, 'creation')}
                          onChange={(e) => handleCoefChange(niveau, 'creation', parseFloat(e.target.value) || 0)}
                          className="w-20 border border-gray-300 rounded px-2 py-1 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
                        />
                      </td>
                      <td className="p-3">
                        <input 
                          type="number" 
                          step="0.01"
                          value={getCoef(niveau, 'mise_a_jour')}
                          onChange={(e) => handleCoefChange(niveau, 'mise_a_jour', parseFloat(e.target.value) || 0)}
                          className="w-20 border border-gray-300 rounded px-2 py-1 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Quotas Statutaires */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold text-gray-800">Quotas Statutaires (Heures)</h2>
              <button 
                onClick={saveQuotas}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition"
              >
                Sauvegarder
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100">
                    <th className="p-3 font-semibold text-gray-600 text-sm">Grade</th>
                    <th className="p-3 font-semibold text-gray-600 text-sm">Permanent</th>
                    <th className="p-3 font-semibold text-gray-600 text-sm">Vacataire</th>
                  </tr>
                </thead>
                <tbody>
                  {grades.map((grade) => (
                    <tr key={`grade-${grade}`} className="border-b border-gray-50">
                      <td className="p-3 font-medium text-gray-700 max-w-[150px] truncate" title={grade}>{grade}</td>
                      <td className="p-3">
                        <input 
                          type="number" 
                          step="1"
                          value={getQuota(grade, 'Permanent')}
                          onChange={(e) => handleQuotaChange(grade, 'Permanent', parseFloat(e.target.value) || 0)}
                          className="w-20 border border-gray-300 rounded px-2 py-1 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
                        />
                      </td>
                      <td className="p-3">
                        <input 
                          type="number" 
                          step="1"
                          value={getQuota(grade, 'Vacataire')}
                          onChange={(e) => handleQuotaChange(grade, 'Vacataire', parseFloat(e.target.value) || 0)}
                          className="w-20 border border-gray-300 rounded px-2 py-1 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </MainLayout>
  );
}
