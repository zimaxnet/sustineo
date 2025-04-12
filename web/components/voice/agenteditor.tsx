import styles from "./agenteditor.module.scss";
import { Editor } from "@monaco-editor/react";
import { useEffect, useState } from "react";
import { VscNewFile, VscSave, VscStarEmpty, VscError } from "react-icons/vsc";
import {
  VoiceConfiguration,
  type Configuration,
} from "store/voice/configuration";

const AgentEditor = () => {
  const [configurations, setConfigurations] = useState<Configuration[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<string>("");
  const [editorValue, setEditorValue] = useState("");

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setEditorValue(value);
    }
  };

  useEffect(() => {
    const voiceConfig = new VoiceConfiguration();
    voiceConfig.fetchConfigurations().then((data) => {
      setConfigurations(data);
      const defaultId = data.find((config) => config.default);
      setSelectedConfig(defaultId?.id || data[0].id);
      setEditorValue(defaultId?.content || data[0].content);
    });
  }, []);

  const handleNew = () => {
    const newConfig = {
      id: Date.now().toString(),
      name: "New Configuration",
      default: false,
      content: "",
    };
    setConfigurations((prev) => [...prev, newConfig]);
    setSelectedConfig(newConfig.id);
    setEditorValue(newConfig.content);
  };

  const handleSave = () => {
    const config = configurations.find(
      (config) => config.id === selectedConfig
    );
    if (config) {
      console.log("Saving configuration:", config);
      // Save the configuration to the server or local storage
      // Example: await saveConfiguration(config.id, editorValue);
    }
  };

  const handleSetDefault = () => {
    const config = configurations.find(
      (config) => config.id === selectedConfig
    );
    if (config?.default) {
      console.log("Already default configuration:", config);
      return;
    }

    console.log(config);
  };

  const handleRemove = () => {
    setConfigurations((prev) =>
      prev.filter((config) => config.id !== selectedConfig)
    );
    setSelectedConfig(configurations[0].id);
    setEditorValue(configurations[0].content);
  };

  function onEditorValidate(markers: any): void {
    console.log("Markers:", markers);
  }

  return (
    <>
      <div className={styles.toolbar}>
        <div>
          <select
            id="config"
            name="config"
            className={styles.promptyselect}
            title="Select Configuration"
            value={selectedConfig}
            onChange={(e) => {
              const selectedConfig = configurations.find(
                (config) => config.id === e.target.value
              );
              if (selectedConfig) {
                setSelectedConfig(selectedConfig.id);
                setEditorValue(selectedConfig.content);
              }
            }}
          >
            {configurations.length === 0 && <option>Loading...</option>}
            {configurations.length > 0 &&
              configurations.map((config) => (
                <option key={config.id} value={config.id}>
                  {config.name}
                  {config.default ? " (default)" : ""}
                </option>
              ))}
          </select>
        </div>
        <button className={styles.icon} title="New" onClick={handleNew}>
          <VscNewFile size={22} />
        </button>
        <button className={styles.icon} title="Save" onClick={handleSave}>
          <VscSave size={22} />
        </button>
        <button
          className={styles.icon}
          title="Set As Default"
          onClick={handleSetDefault}
        >
          <VscStarEmpty size={22} />
        </button>
        <button className={styles.icon} title="Remove" onClick={handleRemove}>
          <VscError size={22} />
        </button>
      </div>
      <Editor
        height="80vh"
        defaultLanguage="markdown"
        value={editorValue}
        onChange={(value) => handleEditorChange(value)}
        onValidate={onEditorValidate}
      />
    </>
  );
};

export default AgentEditor;
