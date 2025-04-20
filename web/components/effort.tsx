import React, { useEffect } from "react";
import styles from "./effort.module.scss";
import clsx from "clsx";
import { useEffortStore } from "store/effort";
import usePersistStore from "store/usepersiststore";

const Effort= () => {
  const ref = React.useRef<HTMLDivElement>(null);
  const effort = usePersistStore(useEffortStore, (state) => state);
  const getStyle = (type: "message" | "function" | "agent") => {
    switch (type) {
      case "message":
        return styles.message;
      case "function":
        return styles.function;
      case "agent":
        return styles.agent;
      default:
        return styles.nothing;
    }
  }

  const getSourceStyle = (source: string) => {
    switch (source) {
      case "user":
        return styles.user;
      case "assistant":
        return styles.assistant;
      default:
        return styles.nothing;
    }
  }

  const scrollEffort = () => {
    setTimeout(() => {
      if (ref.current) {
        ref.current.scrollTo({
          top: ref.current.scrollHeight,
          behavior: "smooth",
        });
      }
    }, 10);
  };

  useEffect(() => {
    scrollEffort();
  }, [effort?.efforts.length]);

  return (
    <div className={clsx(styles.container, styles.scrollbarHide)} ref={ref}>
      {effort?.efforts.map((item, index) => {
        return (
          <div
            key={index}
            className={clsx(styles.item, getStyle(item.type), getSourceStyle(item.source))}
          >
            {item.content}
          </div>
        );
      })}
    </div>
  );
};

export default Effort;
