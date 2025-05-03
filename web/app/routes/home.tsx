import type { Route } from "./+types/home";
import Settings from "components/settings";
import Setting from "components/setting";
import { TbArticle, TbSettingsCog, TbClearAll } from "react-icons/tb";
import VoiceSettings from "components/voice/voicesettings";
import Actions from "components/actions";
import { version } from "store/version";
import Title from "components/title";
import { useEffect } from "react";
import type { Update } from "store/voice/voice-client";
import { useUser } from "store/useuser";
import { useRealtime } from "components/voice/userealtime";
import { useEffortStore } from "store/effort";
import usePersistStore from "store/usepersiststore";
import styles from "./home.module.scss";
import AgentEditor from "components/voice/agenteditor";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { API_ENDPOINT } from "store/endpoint";

import VoiceTool from "components/voicetool";
import Effort from "components/effortlist";
import Tool from "components/tool";
import {
  useOutputStore,
  type TextData,
  type ImageData,
} from "store/output";
import { v4 as uuidv4 } from "uuid";
import Output from "components/output";

const queryClient = new QueryClient();

export function meta({}: Route.MetaArgs) {
  return [
    { title: "sustineō" },
    { name: "description", content: "Your Digital Support Agent" },
  ];
}

export default function Home() {
  const { user, error } = useUser();
  useEffect(() => {
    if (error) {
      console.error("Error fetching user data:", error);
    }
  }, [error]);

  const effort = usePersistStore(useEffortStore, (state) => state);
  const output = usePersistStore(useOutputStore, (state) => state);

  const addOutput = async (
    parent: string,
    agent: string,
    call_id: string,
    content: Array<Record<string, any>>
  ) => {
    console.log("Adding output", parent, agent, call_id, content);
    output?.addOrUpdateRootLeaf({
      id: parent,
      title: agent,
      value: 1,
      children: [],
    });

    for (const item of content) {
      if (item.type === "text") {
        const textData: TextData = {
          id: uuidv4(),
          type: "text",
          value: item.value,
          annotations: item.annotations,
        };
        output?.addLeaf(parent, {
          id: uuidv4(),
          title: agent,
          value: 1,
          data: textData,
          children: [],
        });
        await sendRealtime({
          id: uuidv4(),
          type: "function_completion",
          call_id: call_id,
          output: item.value,
        });
      } else if (item.type === "image") {
        const imageData: ImageData = {
          id: uuidv4(),
          type: "image",
          description: item.description,
          image_url: item.image_url,
          size: item.size,
          quality: item.quality,
        };
        output?.addLeaf(parent, {
          id: uuidv4(),
          title: agent,
          value: 1,
          data: imageData,
          children: [],
        });
        await sendRealtime({
          id: uuidv4(),
          type: "function_completion",
          call_id: call_id,
          output: `Generated image as described by ${item.description}. It is ${item.size} and ${item.quality}. It has been saved and is currently being displayed to ${user.name}.`,
        });
      }
    }
  };

  const handleServerMessage = async (serverEvent: Update): Promise<void> => {
    console.log(serverEvent);
    switch (serverEvent.type) {
      case "message":
        if (serverEvent.content) {
          effort?.addEffort(serverEvent);
        }
        break;
      case "function":
        // no need to await for this, just send it to the server
        sendRealtime({
          id: serverEvent.id,
          type: "function_completion",
          call_id: serverEvent.call_id,
          output:
            "Working on it - will continue to update as I go. Feel free to work on other tasks in the meantime. Make sure to let the user know you are working on it and can do other tasks.",
        });

        effort?.addEffort(serverEvent);

        const endpoint = API_ENDPOINT;
        if (endpoint.startsWith("http://")) {
          endpoint.replace("http://", "https://");
        }
        
        const api = `${endpoint}/api/agent/${user.key}/`;
        console.log("Sending function call to agent", api, serverEvent);
        await fetch(api, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            call_id: serverEvent.call_id,
            id: serverEvent.id,
            name: serverEvent.name,
            arguments: serverEvent.arguments,
          }),
        });
        break;
      case "agent":
        effort?.addEffort(serverEvent);
        if (serverEvent.content) {
          addOutput(
            serverEvent.name.toLowerCase().replaceAll(" ", "_"),
            serverEvent.name,
            serverEvent.call_id,
            serverEvent.content?.content
          );
        }
        break;
    }
  };

  const { toggleRealtime, talking, sendRealtime, callState } = useRealtime(
    user,
    handleServerMessage
  );

  const handleVoice = async () => {
    if (callState === "idle") {
      effort?.clearEfforts();
      output?.reset();
    }
    toggleRealtime();
  };

  const addOutpuItem = () => {
    const o: TextData = {
      id: uuidv4(),
      type: "text",
      value:
        "Here are the latest trends for spring hiking in 2025:\n\n### 1. Gear Essentials\n- **Sustainable & Lightweight Gear**: Minimalist designs using eco-friendly materials, like sustainable hiking boots and recycled backpacks.\n- **Tech Gadgets**: Solar-powered chargers and lightweight GPS devices continue to be popular.\n- **Outerwear**: Lightweight, weather-resistant layers, including breathable rain jackets【7:3†source】【7:4†source】.\n\n### 2. Popular Destinations\n- Iconic locations like U.S. national parks (e.g., Yosemite and Zion) draw crowds.\n- Spring blossoms and trails in Japan's countryside and Europe are sought-after for scenery.\n\n### 3. Outdoor Activities\n- Multi-day treks and nature photography dominate trends.\n- Reconnect-with-nature initiatives include trail cleanup hikes and eco-projects.\n\nWould you like detailed info on any specific category?",
      annotations: [
        {
          type: "url_citation",
          text: "【7:3†source】",
          start_index: 403,
          end_index: 415,
          url_citation: {
            url: "https://gwynandami.com/2025-outdoor-gear-guide-hiking-backpacking-and-more/",
            title: "2025 Outdoor Gear Guide: hiking, backpacking, and more",
          },
        },
        {
          type: "url_citation",
          text: "【7:4†source】",
          start_index: 415,
          end_index: 427,
          url_citation: {
            url: "https://explore-mag.com/10-of-the-best-gear-items-for-spring-2025/",
            title:
              "10 of the Best Gear Items for Spring 2025 – Explore Magazine",
          },
        },
      ],
    };

    output?.addOrUpdateRootLeaf({
      id: "bing_search_agent",
      title: "Bing Search Agent",
      description: "Bing Search Agent",
      value: 1,
      children: [],
    });

    output?.addLeaf("bing_search_agent", {
      id: uuidv4(),
      title: "Results for Search about dogs",
      description: "Bing Search Agent",
      value: 1,
      data: o,
      children: [],
    });
  };

  return (
    <QueryClientProvider client={queryClient}>
      <main className={styles.home}>
        <Title text="sustineō" version={version} user={user} />
        <div className={styles.scratch}>
          <div className={styles.effort}>
            <Effort />
          </div>
          <div className={styles.output}>
            {output && output.output && output.output.children.length > 0 && (
              <Output data={output.output} />
            )}
          </div>
        </div>
        <Actions>
          <Tool
            icon={<TbClearAll size={18} />}
            onClick={() => {
              effort?.clearEfforts();
              output?.reset();
            }}
          />
          <Tool icon={<TbArticle size={18} />} onClick={() => addOutpuItem()} />
          <VoiceTool onClick={() => handleVoice()} />
        </Actions>
        <Settings>
          <Setting
            id={"voice-settings"}
            icon={<TbSettingsCog size={18} />}
            className={styles.voice}
          >
            <VoiceSettings />
          </Setting>
          <Setting
            id={"voice-agent-settings"}
            icon={<TbArticle size={18} />}
            className={styles.editor}
          >
            <AgentEditor />
          </Setting>
        </Settings>
      </main>
    </QueryClientProvider>
  );
}
