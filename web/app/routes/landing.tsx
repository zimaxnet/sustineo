import { useUser } from 'store/useuser';
import MicIcon from '../components/MicIcon';
import styles from './landing.module.scss';

export default function Landing() {
  return (
    <div className={styles.root}>
      <div className={styles.container}>
        <h1>Let's bring your event to life</h1>
        <p>Tell me more about your event—type, size, date—and we'll handle every detail.</p>
      </div>
      <div className={styles.micContainer}>
        <MicIcon className={styles.micIcon} />
      </div>
    </div>
  );
}
