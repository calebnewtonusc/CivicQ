import React from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface BulkAction {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'success' | 'warning' | 'danger';
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

interface BulkActionBarProps {
  selectedCount: number;
  actions: BulkAction[];
  onClear: () => void;
}

const BulkActionBar: React.FC<BulkActionBarProps> = ({
  selectedCount,
  actions,
  onClear,
}) => {
  if (selectedCount === 0) return null;

  const getButtonClasses = (variant: string = 'primary') => {
    const base = 'inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2';

    switch (variant) {
      case 'success':
        return `${base} border-green-300 text-green-700 bg-green-50 hover:bg-green-100 focus:ring-green-500`;
      case 'warning':
        return `${base} border-yellow-300 text-yellow-700 bg-yellow-50 hover:bg-yellow-100 focus:ring-yellow-500`;
      case 'danger':
        return `${base} border-red-300 text-red-700 bg-red-50 hover:bg-red-100 focus:ring-red-500`;
      default:
        return `${base} border-indigo-300 text-indigo-700 bg-indigo-50 hover:bg-indigo-100 focus:ring-indigo-500`;
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 lg:left-64 bg-white border-t border-gray-200 shadow-lg z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">
              {selectedCount} item{selectedCount !== 1 ? 's' : ''} selected
            </span>
            <button
              onClick={onClear}
              className="text-sm text-gray-500 hover:text-gray-700 flex items-center"
            >
              <XMarkIcon className="h-4 w-4 mr-1" />
              Clear selection
            </button>
          </div>
          <div className="flex items-center space-x-3">
            {actions.map((action, index) => {
              const Icon = action.icon;
              return (
                <button
                  key={index}
                  onClick={action.onClick}
                  className={getButtonClasses(action.variant)}
                >
                  {Icon && <Icon className="h-4 w-4 mr-2" />}
                  {action.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BulkActionBar;
