import { LucideIcon } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface StatCardProps {
  label: string;
  value: string | number;
  description?: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isUp: boolean;
  };
  className?: string;
}

export default function StatCard({
  label,
  value,
  description,
  icon: Icon,
  trend,
  className
}: StatCardProps) {
  return (
    <div className={cn('tonal-card relative overflow-hidden', className)}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-muted">{label}</p>
          <h3 className="mt-1 text-2xl font-bold text-foreground">{value}</h3>
          
          {description && (
            <p className="mt-1 text-xs text-muted">{description}</p>
          )}

          {trend && (
            <div className="mt-2 flex items-center space-x-1">
              <span className={cn(
                'text-xs font-semibold',
                trend.isUp ? 'text-green-600' : 'text-red-500'
              )}>
                {trend.isUp ? '+' : '-'}{trend.value}%
              </span>
              <span className="text-xs text-muted">vs mois dernier</span>
            </div>
          )}
        </div>
        
        <div className="rounded-uvci bg-primary-light p-3 text-primary shadow-sm border border-primary/5">
          <Icon className="h-6 w-6" />
        </div>
      </div>
      
      {/* Decorative accent */}
      <div className="absolute -bottom-6 -right-6 h-24 w-24 rounded-full bg-primary/5"></div>
    </div>
  );
}
