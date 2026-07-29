import React, { useEffect, useState } from "react";

export const KRATOS_BLOCK_BANNER = `
 █████╗ ██████╗  █████╗ ████████╗██████╗ ███████╗
██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗██╔════╝
███████║██████╔╝███████║   ██║   ██║  ██║███████╗
██╔══██║██╔══██╗██╔══██║   ██║   ██║  ██║╚════██║
██║  ██║██║  ██║██║  ██║   ██║   ██████╔╝███████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚══════╝
 Knowledge-driven Road Analysis for Terrain Occlusion & Security
`;

interface AsciiSplashProps {
  onComplete: () => void;
}

export const AsciiSplash: React.FC<AsciiSplashProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setTimeout(onComplete, 400);
          return 100;
        }
        return prev + 25;
      });
    }, 200);

    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <div className="fixed inset-0 bg-slate-950 text-cyan-400 font-mono flex flex-col items-center justify-center p-6 z-50 select-none">
      <pre className="text-xs sm:text-sm md:text-base leading-tight text-cyan-400 font-bold mb-6 text-center drop-shadow-[0_0_10px_rgba(34,211,238,0.5)]">
        {KRATOS_BLOCK_BANNER}
      </pre>

      <div className="w-64 bg-slate-900 border border-cyan-800 rounded p-1 mb-4">
        <div
          className="bg-cyan-500 h-2 rounded transition-all duration-200"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-slate-400 text-sm tracking-widest uppercase">
        Initializing Agent Orchestrator... {progress}%
      </p>
    </div>
  );
};
