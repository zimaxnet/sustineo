import { useLocalStorage } from "store/uselocalstorage";
import { useMediaDevices } from "store/usemediadevice";
import { GrPowerReset } from "react-icons/gr";
import styles from "./voicesettings.module.scss";
import {
  defaultConfiguration,
  defaultEagerness,
  defaultVoices,
  type VoiceConfiguration,
} from "store/voice";

const VoiceSettings = () => {
  const {
    storedValue: settings,
    setValue: setSettings,
    reset: resetSettings,
  } = useLocalStorage<VoiceConfiguration>(
    "voice-settings",
    defaultConfiguration
  );
  const { devices, error, isLoading } = useMediaDevices(true);

  return (
    <>
      <div className={styles.control}>
        <div className={styles.label}>Voice Input:</div>
        <select
          id="device"
          name="device"
          className={styles.mediaselect}
          value={settings.inputDeviceId}
          title="Select a device"
          onChange={(e) =>
            setSettings({ ...settings, inputDeviceId: e.target.value })
          }
        >
          {isLoading && <option>Loading...</option>}
          {error && <option>Error: {error}</option>}
          {devices
            .filter((device) => device.kind === "audioinput")
            .map((device) => {
              return (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.label}
                </option>
              );
            })}
        </select>
      </div>
      <div className={styles.control}>
        <div
          className={styles.label}
          title={
            'The eagerness of the model to respond. \"low\" will wait longer for the user to continue speaking, high will respond more quickly.\n "auto" is the default and is equivalent to "medium".'
          }
        >
          Eagerness:
        </div>
        <select
          id="eagerness"
          name="eagerness"
          className={styles.mediaselect}
          value={settings.eagerness}
          title="Select a voice"
          onChange={(e) =>
            setSettings({
              ...settings,
              eagerness: e.target.value as "low" | "medium" | "high" | "auto",
            })
          }
        >
          {defaultEagerness.map((voice) => {
            return (
              <option key={voice.value} value={voice.value}>
                {voice.name}
              </option>
            );
          })}
        </select>
      </div>
      <div className={styles.control}>
        <div
          className={styles.label}
          title={
            "The voice used for the model response for the session.\n\nOnce the voice is used in the session for the model's audio response, it can't be changed."
          }
        >
          Voice:
        </div>
        <select
          id="voice"
          name="voice"
          className={styles.mediaselect}
          value={settings.voice}
          title="Select a voice"
          onChange={(e) => setSettings({ ...settings, voice: e.target.value })}
        >
          {defaultVoices.map((voice) => {
            return (
              <option key={voice.value} value={voice.value}>
                {voice.name}
              </option>
            );
          })}
        </select>
      </div>
      <div className={styles.buttonContainer}>
        <button
          className={styles.resetButton}
          onClick={() => resetSettings()}
          title="Reset to default settings"
        >
          <GrPowerReset size={24} />
        </button>
      </div>
    </>
  );
};

export default VoiceSettings;
