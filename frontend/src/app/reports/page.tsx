'use client';

import { 
  BarChart3, 
  Download, 
  FileSpreadsheet, 
  FileText, 
  PieChart, 
  TrendingUp,
  Calendar,
  Filter
} from 'lucide-react';
import StatCard from '@/components/ui/StatCard';
import api from '@/lib/api';
import { useState, useEffect } from 'react';

export default function ReportsPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    api.get('/dashboard/stats')
      .then(res => setStats(res.data))
      .catch(console.error);
  }, []);

  const handleExportExcel = async () => {
    try {
      const response = await api.get('/exports/excel', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'etat_global_heures.xlsx');
      document.body.appendChild(link);
      link.click();
    } catch (err) {
      alert('Erreur lors de l\'export Excel');
    }
  };

  return (
    <div className="space-y-8 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Rapports & Statistiques</h1>
          <p className="text-sm text-muted">Analysez la repartition de la charge de travail et exportez les donnees.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 rounded-uvci border border-border bg-white px-4 py-2.5 text-sm font-semibold text-foreground hover:bg-gray-50 transition-all shadow-sm">
            <Calendar className="h-4 w-4" />
            <span>Semestre 1</span>
          </button>
          <button className="flex items-center space-x-2 rounded-uvci border border-border bg-white px-4 py-2.5 text-sm font-semibold text-foreground hover:bg-gray-50 transition-all shadow-sm">
            <Filter className="h-4 w-4" />
            <span>Filtrer</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <StatCard
          label="Charge Totale"
          value={stats ? `${stats.total_volume} h` : '-'}
          icon={TrendingUp}
        />
        <StatCard
          label="Moyenne / Enseignant"
          value={stats && stats.total_teachers > 0 ? `${(parseFloat(stats.total_volume) / stats.total_teachers).toFixed(1)} h` : '0 h'}
          icon={BarChart3}
        />
        <StatCard
          label="Budget Estime"
          value={stats ? `${(parseFloat(stats.total_volume) * 10000).toLocaleString('fr-FR')} FCFA` : '-'}
          icon={PieChart}
          description="Base sur un taux moyen de 10 000F/h"
        />
      </div>

      {/* Analytics Grid */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Departmental Distribution */}
        <div className="tonal-card">
          <h3 className="mb-6 font-bold text-lg">Repartition par Departement</h3>
          <div className="space-y-6">
            {[
              { name: 'Informatique & Numerique', hours: stats ? parseFloat(stats.total_volume) * 0.45 : 0, color: 'bg-primary' },
              { name: 'Sciences de Gestion', hours: stats ? parseFloat(stats.total_volume) * 0.30 : 0, color: 'bg-primary/80' },
              { name: 'Communication & Medias', hours: stats ? parseFloat(stats.total_volume) * 0.15 : 0, color: 'bg-primary/60' },
              { name: 'Langues & Culture', hours: stats ? parseFloat(stats.total_volume) * 0.10 : 0, color: 'bg-primary/40' }
            ].map((dept, i) => (
              <div key={i} className="space-y-2">
                <div className="flex items-center justify-between text-sm font-medium">
                  <span>{dept.name}</span>
                  <span className="font-bold">{dept.hours.toFixed(1)} h</span>
                </div>
                <div className="h-2 w-full rounded-full bg-gray-100 relative overflow-hidden">
                  <div 
                    className={`absolute left-0 top-0 h-full rounded-full ${dept.color}`} 
                    style={{ width: stats && parseFloat(stats.total_volume) > 0 ? `${(dept.hours / parseFloat(stats.total_volume)) * 100}%` : '0%' }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Export Suite */}
        <div className="tonal-card bg-primary-light flex flex-col justify-center items-center text-center p-12 border-2 border-dashed border-primary/20">
          <div className="h-16 w-16 rounded-full bg-white flex items-center justify-center text-primary mb-4 shadow-sm">
            <Download className="h-8 w-8" />
          </div>
          <h3 className="text-xl font-bold text-primary mb-2">Centre d'Exportation</h3>
          <p className="text-sm text-primary/70 mb-8 max-w-xs mx-auto">
            Generer les documents officiels pour la comptabilite et l'administration.
          </p>
          
          <div className="grid grid-cols-1 gap-4 w-full max-w-sm">
            <button 
              onClick={handleExportExcel}
              className="flex items-center justify-center space-x-3 rounded-uvci bg-white px-6 py-4 text-sm font-bold text-primary hover:bg-gray-50 transition-all shadow-premium group"
            >
              <FileSpreadsheet className="h-5 w-5 text-green-600" />
              <span>Exporter l'Etat Global (Excel)</span>
            </button>
            <button className="flex items-center justify-center space-x-3 rounded-uvci bg-white px-6 py-4 text-sm font-bold text-primary hover:bg-gray-50 transition-all shadow-premium">
              <FileText className="h-5 w-5 text-red-600" />
              <span>Generer Releves de Presence</span>
            </button>
          </div>
          
          <p className="mt-6 text-[10px] uppercase font-black tracking-widest text-primary/40">
            Derniere mise a jour : Aujourd'hui 18:45
          </p>
        </div>
      </div>
    </div>
  );
}
