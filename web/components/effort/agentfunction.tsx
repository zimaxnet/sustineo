import styles from "./agentfunction.module.scss";
import type { FunctionUpdate } from "store/voice/voice-client";

type Props = {
  func: FunctionUpdate;
};
const AgentFunction = ({ func }: Props) => {
  return (
    <div className={styles.function}>
      <div className={styles.functionCall}>
        <span>executing</span>&nbsp;
        <span className={styles.functionName}>{func.name}</span>
      </div>
      <div className={styles.functionArgs}>
        {/* enumerate args dictionary */}
        {Object.entries(func.arguments).map(([key, value], index) => {
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
};

export default AgentFunction;
