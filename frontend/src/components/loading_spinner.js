import React from 'react';

const LoadingSpinner = () => (
  <div className="loading-spinner">
    <svg width="10em" height="10em" xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
      <g transform="rotate(0 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.9s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(36 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.8s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(72 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.7s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(108 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.6s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(144 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.5s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(180 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.4s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(216 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.3s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(252 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.2s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(288 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="-0.1s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
      <g transform="rotate(324 50 50)">
        <rect x="47.5" y="30" rx="9.5" ry="6" width="5" height="10" fill="#7aa228">
          <animate attributeName="opacity" values="1;0" times="0;1" dur="1s" begin="0s"
                   repeatCount="indefinite"></animate>
        </rect>
      </g>
    </svg>
  </div>
);

export default LoadingSpinner;

