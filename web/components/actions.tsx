import React, { type ReactElement } from "react";
import Tool from "./tool";
import styles from "./actions.module.scss";

interface Props {
  children: ReactElement<typeof Tool> | Array<ReactElement<typeof Tool>>;
}

const Actions: React.FC<Props> = ({ children }) => {
  if (!children) {
    return null;
  }
  if (!Array.isArray(children)) {
    children = [children];
  }
  return (
    <div className={styles.container}>
      {children.map((child) => {
        return child;
      })}
    </div>
  );
};

export default Actions;
