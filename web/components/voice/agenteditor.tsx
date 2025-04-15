import styles from "./agenteditor.module.scss";
import { Editor } from "@monaco-editor/react";
import { useEffect, useState } from "react";
import { VscNewFile, VscSave, VscStarEmpty, VscError } from "react-icons/vsc";
import {
  defaultVoiceDocument,
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

  const refreshConfigurations = async () => {
    const voiceConfig = new VoiceConfiguration();
    const data = await voiceConfig.fetchConfigurations();
    setConfigurations(data);
  };

  const handleNew = async () => {
    const newConfig = {
      id: Date.now().toString(),
      name: "New Configuration",
      default: false,
      content: defaultVoiceDocument,
    };
    setConfigurations((prev) => [...prev, newConfig]);
    setSelectedConfig(newConfig.id);
    setEditorValue(newConfig.content);
  };

  const handleSave = async () => {
    const config = configurations.find(
      (config) => config.id === selectedConfig
    );

    if (config) {
      const voiceConfig = new VoiceConfiguration();
      let c: Configuration | undefined = undefined;
      if (config.name === "New Configuration") {
        c = await voiceConfig.createConfiguration(editorValue);
        if (!c) {
          console.error("Error creating configuration");
          return;
        }
        setConfigurations((prev) =>
          prev.map((cfg) => (cfg.name === "New Configuration" ? c! : cfg))
        );
        setSelectedConfig(c.id);
        setEditorValue(c.content);
      } else {
        c = await voiceConfig.updateConfiguration(config.id, editorValue);
        if (!c) {
          console.error("Error updating configuration");
          return;
        }
        setConfigurations((prev) =>
          prev.map((cfg) => (cfg.id === config.id ? c! : cfg))
        );
        setSelectedConfig(c.id);
        setEditorValue(c.content);
      }
    }
  };

  const handleSetDefault = async () => {
    const config = configurations.find(
      (config) => config.id === selectedConfig
    );

    if (config?.default) {
      console.log("Already default configuration:", config);
      return;
    }

    if (config) {
      const voiceConfig = new VoiceConfiguration();
      const updatedConfig = await voiceConfig.setDefaultConfiguration(
        config.id
      );
      if (updatedConfig.error) {
        console.error(
          "Error setting default configuration:",
          updatedConfig.error
        );
        return;
      }

      setConfigurations((prev) =>
        prev.map((cfg) =>
          cfg.id === config.id
            ? { ...cfg, default: true }
            : { ...cfg, default: false }
        )
      );
      setSelectedConfig(updatedConfig.id);
    }

    console.log(config);
  };

  const handleRemove = async () => {
    
    const voiceConfig = new VoiceConfiguration();
    const action = await voiceConfig.deleteConfiguration(selectedConfig);
    if (action.error) {
      console.error("Error deleting configuration:", action.error);
      return;
    }

    setConfigurations((prev) =>
      prev.filter((config) => config.id !== selectedConfig)
    );

    setSelectedConfig(configurations[0].id);
    setEditorValue(configurations[0].content);
  };

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
      />
    </>
  );
};

export default AgentEditor;
