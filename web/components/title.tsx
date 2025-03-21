import React from "react";
import styles from "./title.module.scss";
import { type User } from "store/useuser";
import { TbUser } from "react-icons/tb";

type Props = {
  text: string;
  version: string;
  user?: User;
};

const Title: React.FC<Props> = ({ text, version, user }: Props) => {
  return (
    <div className={styles.container}>
      <div className={styles.logo}>
        <div className={styles.title}>{text}</div>
        <div className={styles.version}>{version}</div>
      </div>
      <div className={styles.grow} />
      {user && (
        <div className={styles.user}>
          <div>
            <div className={styles.name}>{user.name}</div>
            <div className={styles.email}>{user.email}</div>
          </div>
          {user.avatar && (
            <img
              alt={user.name}
              className={styles.avatar}
              src="/images/people/seth-juarez.jpg"
            />
          )}
          {!user.avatar && (
            <div className={styles.userIcon}>
              <TbUser size={24} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Title;
