import { useLocalStorage } from "store/uselocalstorage";
import { useMediaDevices } from "store/usemediadevice";
import { GrPowerReset } from "react-icons/gr";
import styles from "./voicesettings.module.scss";
import { defaultConfiguration, defaultVoices, type VoiceConfiguration } from "store/voice";

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
            "The activation threshold for the server VAD turn detection. In noisy environments, you might need to increase the threshold to avoid false positives. In quiet environments, you might need to decrease the threshold to avoid false negatives.\n\nDefaults to 0.5. You can set the threshold to a value between 0.0 and 1.0."
          }
        >
          Sensitivity Threshold (between 0 - 1):
        </div>
        <input
          id="threshold"
          name="threshold"
          type="number"
          title="Sensitivity Threshold"
          min={0}
          max={1}
          step={0.1}
          className={styles.textInput}
          value={settings.threshold}
          onChange={(e) =>
            setSettings({ ...settings, threshold: +e.target.value })
          }
        />
      </div>

      <div className={styles.control}>
        <div
          className={styles.label}
          title={
            "The duration of speech audio (in milliseconds) to include before the start of detected speech.\n\nDefaults to 300."
          }
        >
          Prefix Padding (in ms):
        </div>
        <input
          id="prefix"
          name="chat"
          type="number"
          title="Prefix Padding"
          min={0}
          max={3000}
          step={50}
          className={styles.textInput}
          value={settings.prefix}
          onChange={(e) =>
            setSettings({ ...settings, prefix: +e.target.value })
          }
        />
      </div>
      <div className={styles.control}>
        <div
          className={styles.label}
          title={
            "The duration of silence (in milliseconds) to detect the end of speech. You want to detect the end of speech as soon as possible, but not too soon to avoid cutting off the last part of the speech.\n\nThe model will respond more quickly if you set this value to a lower number, but it might cut off the last part of the speech. If you set this value to a higher number, the model will wait longer to detect the end of speech, but it might take longer to respond."
          }
        >
          Silence Duration (in ms):
        </div>
        <input
          id="silence"
          name="chat"
          type="number"
          title="Silence Duration"
          min={0}
          max={3000}
          step={50}
          className={styles.textInput}
          value={settings.silence}
          onChange={(e) =>
            setSettings({ ...settings, silence: +e.target.value })
          }
        />
      </div>
      <div className={styles.control}>
        <div className={styles.label} title={"The voice used for the model response for the session.\n\nOnce the voice is used in the session for the model's audio response, it can't be changed."}>Voice:</div>
        <select
          id="voice"
          name="voice"
          className={styles.mediaselect}
          value={settings.voice}
          title="Select a voice"
          onChange={(e) =>
            setSettings({ ...settings, voice: e.target.value })
          }
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
