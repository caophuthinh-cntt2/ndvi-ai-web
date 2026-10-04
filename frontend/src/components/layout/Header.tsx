import React from 'react';

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({ 
  title = 'NDVI AI - TP. HỒ CHÍ MINH',
  subtitle
}) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-8 py-4">
      <h1 className="text-2xl font-bold text-gray-800">{title}</h1>
      {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
    </header>
  );
};

export default Header;
