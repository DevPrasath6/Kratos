import React, { useState, useEffect } from "react";

interface NumberCounterProps {
  value: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
}

export const NumberCounter: React.FC<NumberCounterProps> = ({
  value,
  duration = 1000,
  prefix = "",
  suffix = "",
  className = "",
}) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = value;
    if (start === end) {
      setCount(end);
      return;
    }

    const stepTime = Math.abs(Math.floor(duration / (end || 1)));
    const timer = setInterval(() => {
      start += 1;
      setCount(start);
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      }
    }, Math.max(stepTime, 20));

    return () => clearInterval(timer);
  }, [value, duration]);

  return (
    <span className={className}>
      {prefix}
      {count}
      {suffix}
    </span>
  );
};
