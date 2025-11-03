// Badge component for taxonomy and status indicators
import React from 'react';

const Badge = ({ text, variant = 'default', size = 'md', onClick }) => {
  const variants = {
    default: 'bg-ubs-gray-100 text-ubs-gray-700 border-ubs-gray-300',
    primary: 'bg-ubs-red text-white border-ubs-red',
    success: 'bg-green-100 text-green-800 border-green-300',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    info: 'bg-blue-100 text-blue-800 border-blue-300',
    error: 'bg-red-100 text-red-800 border-red-300',
  };

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  const baseClasses = 'inline-flex items-center font-medium border';
  const variantClasses = variants[variant] || variants.default;
  const sizeClasses = sizes[size] || sizes.md;
  const interactiveClasses = onClick
    ? 'cursor-pointer hover:opacity-80 transition-opacity active:scale-95'
    : '';

  return (
    <span
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${interactiveClasses}`}
      onClick={onClick}
    >
      {text}
    </span>
  );
};

export default Badge;