import React from "react";
import styles from "./voicetool.module.scss";
import clsx from "clsx";
import { HiMiniMicrophone } from "react-icons/hi2";

interface Props {
  onClick: () => void;
  className?: string;
}

const VoiceTool: React.FC<Props> = ({ onClick, className }) => {
  const style = className || styles.button;
  return (
    <div className={style} onClick={onClick}>
      <HiMiniMicrophone size={48} />
    </div>
  );
};

export default VoiceTool;
