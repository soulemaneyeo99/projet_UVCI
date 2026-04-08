'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import api from '@/lib/api';
import { toast, Toaster } from 'react-hot-toast';

interface User {
  id: number;
  email: string;
  role: string;
  est_actif: boolean;
  created_at: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'teacher',
    est_actif: true,
  });

  const fetchUsers = async () => {
    try {
      const res = await api.get('/users/');
      setUsers(res.data);
    } catch (error) {
      toast.error('Erreur lors du chargement des utilisateurs');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const openModal = (user?: User) => {
    if (user) {
      setEditingUser(user);
      setFormData({
        email: user.email,
        password: '',
        role: user.role,
        est_actif: user.est_actif,
      });
    } else {
      setEditingUser(null);
      setFormData({ email: '', password: '', role: 'teacher', est_actif: true });
    }
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingUser(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await api.put(`/users/${editingUser.id}`, formData);
        toast.success('Utilisateur mis à jour avec succès');
      } else {
        await api.post('/users/', formData);
        toast.success('Utilisateur créé avec succès');
      }
      closeModal();
      fetchUsers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    }
  };

  const toggleStatus = async (user: User) => {
    try {
      if (user.est_actif) {
        await api.patch(`/users/${user.id}/desactiver`);
        toast.success('Utilisateur désactivé');
      } else {
        await api.patch(`/users/${user.id}/activer`);
        toast.success('Utilisateur activé');
      }
      fetchUsers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Une erreur est survenue');
    }
  };

  return (
    <MainLayout>
      <Toaster position="top-right" />
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestion des Utilisateurs</h1>
          <p className="text-gray-500 text-sm mt-1">Créez et gérez les accès au système</p>
        </div>
        <button
          onClick={() => openModal()}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition"
        >
          Nouvel Utilisateur
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Chargement...</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="p-4 font-semibold text-gray-600">Email</th>
                <th className="p-4 font-semibold text-gray-600">Rôle</th>
                <th className="p-4 font-semibold text-gray-600">Date d'ajout</th>
                <th className="p-4 font-semibold text-gray-600">Statut</th>
                <th className="p-4 font-semibold text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition">
                  <td className="p-4 text-gray-800">{user.email}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium 
                      ${user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 
                        user.role === 'secretary' ? 'bg-orange-100 text-orange-700' : 
                        'bg-blue-100 text-blue-700'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="p-4 text-gray-500">{new Date(user.created_at).toLocaleDateString()}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${user.est_actif ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {user.est_actif ? 'Actif' : 'Inactif'}
                    </span>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button
                        onClick={() => openModal(user)}
                        className="text-indigo-600 hover:text-indigo-800 font-medium text-sm transition"
                      >
                        Éditer
                      </button>
                      <button
                        onClick={() => toggleStatus(user)}
                        className={`${user.est_actif ? 'text-red-600 hover:text-red-800' : 'text-green-600 hover:text-green-800'} font-medium text-sm transition`}
                      >
                        {user.est_actif ? 'Désactiver' : 'Activer'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-8 text-center text-gray-500">Aucun utilisateur trouvé</td>
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
                {editingUser ? 'Modifier Utilisateur' : 'Nouvel Utilisateur'}
              </h3>
              <button onClick={closeModal} className="text-gray-400 hover:text-gray-600">
                ✕
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Mot de passe {editingUser && '(Laisser vide pour ne pas changer)'}
                  </label>
                  <input
                    type="password"
                    required={!editingUser}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rôle</label>
                  <select
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                  >
                    <option value="admin">Administrateur</option>
                    <option value="secretary">Secrétaire</option>
                    <option value="teacher">Enseignant</option>
                  </select>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <input
                    type="checkbox"
                    id="est_actif"
                    checked={formData.est_actif}
                    onChange={(e) => setFormData({ ...formData, est_actif: e.target.checked })}
                    className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                  />
                  <label htmlFor="est_actif" className="text-sm text-gray-700">Compte actif</label>
                </div>
              </div>
              <div className="mt-6 flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
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
