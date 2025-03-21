import React, { useEffect, useState } from "react";
import styles from "./setting.module.scss";
import Tool from "./tool";

interface Props {
  id: string;
  icon: React.ReactNode;
  children?: React.ReactNode;
}

const Setting: React.FC<Props> = ({ id, icon, children }: Props) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleOpen = () => {
    setIsOpen((prev) => !prev);
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest(`#${id}`)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <div id={id} className={styles.settings}>
      {isOpen && (
        <div className={styles.content}>
          {children}
        </div>
      )}
      <Tool icon={icon} onClick={toggleOpen} />
    </div>
  );
};

export default Setting;
