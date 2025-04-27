import React, { useEffect } from "react";
import styles from "./effortlist.module.scss";
import clsx from "clsx";
import { useEffortStore, type Effort } from "store/effort";
import usePersistStore from "store/usepersiststore";

const EffortList = () => {
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
  };

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

  const getContent = (effort: Effort) => {
    switch (effort.type) {
      case "message":
        return (
          <div
            className={clsx(styles.message, effort.role === "user" ? styles.user : styles.assistant)}
          >
            {effort.content}
          </div>
        );
      case "function":
        return (
          <div className={styles.function}>
            <div className={styles.functionCall}>
              <span>Agent</span>&nbsp;
              <span className={styles.functionName}>{effort.name}</span>
            </div>
            <div className={styles.functionArgs}>
              {/* enumerate args dictionary */}
              {Object.entries(effort.arguments).map(([key, value], index) => {
                return (
                  <div key={index} className={styles.functionArg} title={key}>
                    {typeof value === "object"
                      ? JSON.stringify(value)
                      : value?.toString()}
                  </div>
                );
              })}
            </div>
          </div>
        );
      case "agent":
        return (
          <>
            <div className={styles.functionCall}>
              <span className={styles.functionName}>{effort.agentName}</span>
              <span>{effort.type}</span>
              <span>{effort.status}</span>
            </div>
          </>
        );
      default:
        return <div className={styles.nothing}>Nothing</div>;
    }
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
          >
            {getContent(item)}
          </div>
        );
      })}
    </div>
  );
};

export default EffortList;
