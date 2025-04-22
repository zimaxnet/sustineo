import { useQueryClient, useQuery, useMutation } from "@tanstack/react-query";
import styles from "./agenteditor.module.scss";
import { act, useEffect, useState, type ChangeEvent } from "react";
import { VscNewFile, VscSave, VscStarEmpty } from "react-icons/vsc";
import { MdDeleteOutline, MdClose } from "react-icons/md";
import {
  defaultVoiceDocument,
  VoiceConfiguration,
  type Configuration,
} from "store/voice/configuration";
import { API_ENDPOINT } from "store/endpoint";
import type { AgentConfig } from "store/agents";

const AgentEditor = () => {
  const queryClient = useQueryClient();
  const [selectedConfig, setSelectedConfig] = useState<string>("");
  const [editorValue, setEditorValue] = useState("");

  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);

  const { isPending, isError, data, error } = useQuery({
    queryKey: ["configurations"],
    queryFn: async () => {
      const voiceConfig = new VoiceConfiguration();
      const configs = await voiceConfig.fetchConfigurations();
      if (selectedConfig === "") {
        const defaultConfig = configs.find((config) => config.default);
        if (defaultConfig) {
          setSelectedConfig(defaultConfig.id);
          setEditorValue(defaultConfig.content);
        }
      }
      return configs;
    },
  });

  const {
    isPending: isAgentsPending,
    isError: isAgentsError,
    data: agentConfigs,
    error: agentsError,
  } = useQuery({
    queryKey: ["agents"],
    queryFn: async () => {
      // fetch agents from server
      const uri = `${API_ENDPOINT}/api/agent/`;
      const response = await fetch(uri, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      if (!response.ok) {
        throw new Error("Failed to fetch agents");
      }
      const data: AgentConfig[] = await response.json();
      return data;
    },
  });

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      setEditorValue(value);
    }
  };

  const handleNew = async () => {
    const newConfig = {
      id: Date.now().toString(),
      name: "New Configuration",
      default: false,
      content: defaultVoiceDocument,
    };
    data?.push(newConfig); // Add new config to the data array
    setSelectedConfig(newConfig.id);
    setEditorValue(newConfig.content);
  };

  const saveMutation = useMutation({
    mutationFn: async (config: Configuration) => {
      const voiceConfig = new VoiceConfiguration();
      let c: Configuration;
      if (config.name === "New Configuration") {
        // Create new configuration
        c = await voiceConfig.createConfiguration(config);
      } else {
        // Update existing configuration
        c = await voiceConfig.updateConfiguration(config);
      }

      if (c) {
        setSelectedConfig(c.id);
        setEditorValue(c.content);
      }
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["configurations"] });
    },
  });

  const handleSave = async () => {
    console.log("Save configuration:", selectedConfig);
    const c = data?.find((config) => config.id === selectedConfig);
    if (c) {
      await saveMutation.mutateAsync({
        ...c,
        content: editorValue,
      });
    }
  };

  const setDefaultMutation = useMutation({
    mutationFn: async (configId: string) => {
      const voiceConfig = new VoiceConfiguration();
      await voiceConfig.setDefaultConfiguration(configId);
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["configurations"] });
    },
  });

  const handleSetDefault = async () => {
    console.log("Set as default configuration:", selectedConfig);
    if (selectedConfig === "") {
      return;
    }
    await setDefaultMutation.mutateAsync(selectedConfig);
  };

  const removeMutation = useMutation({
    mutationFn: async (configId: string) => {
      const voiceConfig = new VoiceConfiguration();
      await voiceConfig.deleteConfiguration(configId);
      setSelectedConfig(data?.[0]?.id || "");
      setEditorValue(data?.[0]?.content || "");
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ["configurations"] });
    },
  });

  const handleRemove = async () => {
    const accept = confirm(
      "Are you sure you want to remove this configuration?"
    );
    if (!accept) return;
    await removeMutation.mutateAsync(selectedConfig);
  };

  function changeAgent(event: ChangeEvent<HTMLInputElement>): void {
    const { value, checked } = event.target;
    if (checked) {
      setSelectedAgents((prev) => [...prev, value]);
    } else {
      setSelectedAgents((prev) => prev.filter((agent) => agent !== value));
    }
    //console.log("Selected agents:", selectedAgents);
  }

  useEffect(() => {
    console.log("Selected agents:", selectedAgents);
    const activeAgents = agentConfigs?.filter((agent) =>
      selectedAgents.includes(agent.id)
    );
    console.log("Active agents:", activeAgents);
  }, [selectedAgents]);

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
              const selectedId = e.target.value;
              setSelectedConfig(selectedId);
              if (data) {
                const selectedConfig = data.find(
                  (config) => config.id === selectedId
                );
                if (selectedConfig) {
                  setEditorValue(selectedConfig.content);
                }
              }
            }}
          >
            {isPending && <option>Loading...</option>}
            {isError && <option>Error: {error.message}</option>}
            {data &&
              data.map((config) => (
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
          <MdDeleteOutline size={22} />
        </button>
      </div>
      <div className={styles.editor}>
        <textarea
          id="editor"
          spellCheck="false"
          className={styles.textarea}
          value={editorValue}
          wrap="off"
          onChange={(e) => handleEditorChange(e.target.value)}
          placeholder="Write your agent configuration here..."
        ></textarea>
        <div className={styles.tools}>
          <fieldset className={styles.fieldset}>
            <legend>Available Agents</legend>
            {isAgentsPending && <p>Loading...</p>}
            {isAgentsError && <p>Error: {agentsError.message}</p>}
            {agentConfigs &&
              agentConfigs.map((agent) => (
                <div key={agent.id}>
                  <input
                    type="checkbox"
                    id={agent.id}
                    name={agent.id}
                    value={agent.id}
                    radioGroup="agents"
                    onChange={changeAgent}
                  />
                  <label
                    className={styles.label}
                    htmlFor={agent.id}
                    title={agent.description}
                  >
                    {agent.name}
                  </label>
                </div>
              ))}
          </fieldset>
        </div>
      </div>
    </>
  );
};

export default AgentEditor;
