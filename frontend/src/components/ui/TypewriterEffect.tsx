import React, { useState, useEffect } from "react";

interface TypewriterEffectProps {
  text: string;
  speed?: number;
  onComplete?: () => void;
  className?: string;
}

export const TypewriterEffect: React.FC<TypewriterEffectProps> = ({
  text,
  speed = 25,
  onComplete,
  className = "",
}) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    setDisplayedText("");
    let idx = 0;
    const timer = setInterval(() => {
      if (idx < text.length) {
        setDisplayedText(text.slice(0, idx + 1));
        idx++;
      } else {
        clearInterval(timer);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, onComplete]);

  return <span className={`typing-cursor ${className}`}>{displayedText}</span>;
};
