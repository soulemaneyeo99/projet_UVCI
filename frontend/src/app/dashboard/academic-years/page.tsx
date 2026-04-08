'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import api from '@/lib/api';
import { toast, Toaster } from 'react-hot-toast';

interface AcademicYear {
  id: number;
  libelle: string;
  date_debut: string;
  date_fin: string;
  status: boolean;
}

export default function AcademicYearsPage() {
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingYear, setEditingYear] = useState<AcademicYear | null>(null);

  const [formData, setFormData] = useState({
    libelle: '',
    date_debut: '',
    date_fin: '',
    status: false,
  });

  const fetchYears = async () => {
    try {
      const res = await api.get('/academic-years/');
      setYears(res.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des années académiques');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchYears();
  }, []);

  const openModal = (year?: AcademicYear) => {
    if (year) {
      setEditingYear(year);
      setFormData({
        libelle: year.libelle,
        date_debut: year.date_debut,
        date_fin: year.date_fin,
        status: year.status,
      });
    } else {
      setEditingYear(null);
      setFormData({ libelle: '', date_debut: '', date_fin: '', status: false });
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingYear(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingYear) {
        await api.put(`/academic-years/${editingYear.id}`, formData);
        toast.success('Année académique mise à jour');
      } else {
        await api.post('/academic-years/', formData);
        toast.success('Année académique créée');
      }
      closeModal();
      fetchYears();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    }
  };

  const activateYear = async (year: AcademicYear) => {
    try {
      await api.patch(`/academic-years/${year.id}/activate`);
      toast.success('Année académique activée');
      fetchYears();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'activation');
    }
  };

  const deleteYear = async (year: AcademicYear) => {
    if (!window.confirm(`Êtes-vous sûr de vouloir supprimer l'année ${year.libelle} ?`)) return;
    try {
      await api.delete(`/academic-years/${year.id}`);
      toast.success('Année académique supprimée');
      fetchYears();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  return (
    <MainLayout>
      <Toaster position="top-right" />
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Années Académiques</h1>
          <p className="text-gray-500 text-sm mt-1">Gérez les années académiques et définissez l'année active</p>
        </div>
        <button
          onClick={() => openModal()}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
        >
          Nouvelle Année
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Chargement...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="p-4 font-semibold text-gray-600">Libellé</th>
                <th className="p-4 font-semibold text-gray-600">Date de début</th>
                <th className="p-4 font-semibold text-gray-600">Date de fin</th>
                <th className="p-4 font-semibold text-gray-600">Statut</th>
                <th className="p-4 font-semibold text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {years.map((year) => (
                <tr key={year.id} className={`border-b border-gray-50 hover:bg-gray-50/50 transition ${year.status ? 'bg-indigo-50/30' : ''}`}>
                  <td className="p-4 font-medium text-gray-800">{year.libelle}</td>
                  <td className="p-4 text-gray-600">{new Date(year.date_debut).toLocaleDateString()}</td>
                  <td className="p-4 text-gray-600">{new Date(year.date_fin).toLocaleDateString()}</td>
                  <td className="p-4">
                    {year.status ? (
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700 border border-green-200">
                        Active
                      </span>
                    ) : (
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">
                        Inactive
                      </span>
                    )}
                  </td>
                  <td className="p-4">
                    <div className="flex gap-3 items-center">
                      {!year.status && (
                        <button
                          onClick={() => activateYear(year)}
                          className="text-green-600 hover:text-green-800 font-medium text-sm transition"
                          title="Faire de cette année l'année active"
                        >
                          Activer
                        </button>
                      )}
                      <button
                        onClick={() => openModal(year)}
                        className="text-indigo-600 hover:text-indigo-800 font-medium text-sm transition"
                      >
                        Éditer
                      </button>
                      {!year.status && (
                        <button
                          onClick={() => deleteYear(year)}
                          className="text-red-500 hover:text-red-700 font-medium text-sm transition"
                        >
                          Supprimer
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {years.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-gray-500">Aucune année trouvée</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center">
              <h3 className="font-bold text-lg text-gray-900">
                {editingYear ? 'Modifier Année Académique' : 'Nouvelle Année Académique'}
              </h3>
              <button onClick={closeModal} className="text-gray-400 hover:text-gray-600 text-xl font-semibold">
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Libellé (ex: 2024-2025)</label>
                  <input
                    type="text"
                    required
                    value={formData.libelle}
                    onChange={(e) => setFormData({ ...formData, libelle: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                    placeholder="2024-2025"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date de début</label>
                    <input
                      type="date"
                      required
                      value={formData.date_debut}
                      onChange={(e) => setFormData({ ...formData, date_debut: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Date de fin</label>
                    <input
                      type="date"
                      required
                      value={formData.date_fin}
                      onChange={(e) => setFormData({ ...formData, date_fin: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>
                </div>
                {!editingYear && (
                  <div className="flex items-center gap-2 mt-4">
                    <input
                      type="checkbox"
                      id="status"
                      checked={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.checked })}
                      className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                    />
                    <label htmlFor="status" className="text-sm text-gray-700">Définir comme année active dès la création</label>
                  </div>
                )}
              </div>
              <div className="mt-6 flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition font-medium"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-medium shadow-sm"
                >
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
