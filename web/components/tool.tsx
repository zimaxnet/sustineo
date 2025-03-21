import React from "react";
import styles from "./tool.module.scss";

interface Props {
  icon: React.ReactNode;
  onClick: () => void;
}

const Tool: React.FC<Props> = ({ icon, onClick }) => {
  return (
    <div className={styles.button} onClick={onClick}>
      {icon}
    </div>
  );
};

export default Tool;
